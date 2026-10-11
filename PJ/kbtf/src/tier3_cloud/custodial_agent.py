"""
[Tier 3 Custodial Agent] 클라우드 커스터디 에이전트 모듈
W3C DID 관리 및 센서 맥락 인지형(Context-Aware) 무자각 VP 동적 조합기
"""
from typing import Dict, Any, List, Optional
from .cloud_db import CloudDatabase
from ..core.did_kms import CustodialKMS, DIDManager
from ..core.vc_engine import VCEngine
from ..core.security import ZeroPIISanitizer

class CustodialAgent:
    def __init__(self, db: CloudDatabase, kms: CustodialKMS):
        self.db = db
        self.kms = kms
        self.did_manager = DIDManager(self.kms)
        self.vc_engine = VCEngine(self.kms)

    def register_custodial_identity(self, nfc_uid: str, subsidy_tier: str = "TIER_A") -> Dict[str, Any]:
        """
        [시퀀스 1 단계 7~16] 로컬에서 수신된 난수 NFC UID로 Custodial DID 및 기본 거주자 VC 발급
        """
        # 1. DID 생성
        did_record = self.did_manager.create_custodial_did(nfc_uid)
        
        # 2. 클라우드 지갑 저장소 등록
        self.db.save_custodial_wallet(
            nfc_uid=nfc_uid,
            did=did_record["did"],
            public_key=did_record["public_key"],
            key_id=did_record["key_id"]
        )

        # 3. 스마트 거주 자격 VC 발급
        resident_vc = self.vc_engine.issue_credential(
            holder_did=did_record["did"],
            nfc_uid=nfc_uid,
            credential_type="ResidentCredential",
            service_domain="HOUSING_RESIDENT",
            validity_days=730, # 2년
            subsidy_tier=subsidy_tier
        )
        self.db.save_vc(resident_vc, nfc_uid)

        return {
            "status": "CUSTODIAL_IDENTITY_CREATED",
            "nfc_uid": nfc_uid,
            "did": did_record["did"]
        }

    def process_batch_vc_issuance(self, batch_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        [시퀀스 2 단계 3~6] 2주 주기 엑셀 비식별 UID 목록을 받아 대량 익명 단기 VC 배치 발급
        - meal_uids -> CommunityMealCredential (2-1 현장식사)
        - bento_uids -> WelfareBentoCredential (2-2 도시락 수령)
        """
        ZeroPIISanitizer.audit_payload(batch_payload)
        
        meal_uids = batch_payload.get("meal_uids", [])
        bento_uids = batch_payload.get("bento_uids", [])
        issued_count = 0

        # 현장식사 VC 발급 (14일 유효)
        for uid in meal_uids:
            wallet = self.db.get_wallet(uid)
            if not wallet:
                self.register_custodial_identity(uid)
                wallet = self.db.get_wallet(uid)
            
            vc = self.vc_engine.issue_credential(
                holder_did=wallet["custodial_did"],
                nfc_uid=uid,
                credential_type="CommunityMealCredential",
                service_domain="WELFARE_MEAL",
                validity_days=14,
                subsidy_tier="TIER_A"
            )
            self.db.save_vc(vc, uid)
            issued_count += 1

        # 도시락 VC 발급 (14일 유효)
        for uid in bento_uids:
            wallet = self.db.get_wallet(uid)
            if not wallet:
                self.register_custodial_identity(uid)
                wallet = self.db.get_wallet(uid)

            vc = self.vc_engine.issue_credential(
                holder_did=wallet["custodial_did"],
                nfc_uid=uid,
                credential_type="WelfareBentoCredential",
                service_domain="WELFARE_BENTO",
                validity_days=14,
                subsidy_tier="TIER_A"
            )
            self.db.save_vc(vc, uid)
            issued_count += 1

        return {
            "status": "BATCH_VC_ISSUED_SUCCESS",
            "total_issued": issued_count,
            "meal_vc_count": len(meal_uids),
            "bento_vc_count": len(bento_uids)
        }

    def assemble_presentation_for_sensor(self, nfc_uid: str, sensor_id: str) -> Optional[Dict[str, Any]]:
        """
        [시퀀스 3 & 4 단계] Sensor ID의 정책을 인지하여 해당 목적에 부합하는 VC를 선별하고,
        불필요한 정보를 노출하지 않는 최소공개 VP를 동적 생성 및 서명.
        """
        wallet = self.db.get_wallet(nfc_uid)
        if not wallet:
            return None

        policy = self.db.get_sensor_policy(sensor_id)
        if not policy:
            return None

        target_vc_type = policy["target_vc_type"]
        vcs = self.db.get_active_vcs(nfc_uid)

        # 타겟 VC 선별
        selected_vcs = [vc for vc in vcs if target_vc_type in vc["type"]]
        if not selected_vcs:
            return None

        # 동적 VP 생성 및 홀더 키 서명
        vp = self.vc_engine.create_verifiable_presentation(
            holder_did=wallet["custodial_did"],
            holder_key_id=wallet["key_id"],
            selected_vcs=selected_vcs
        )
        return vp
