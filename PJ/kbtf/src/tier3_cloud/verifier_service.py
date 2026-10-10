"""
[Tier 3 Verifier Service] 검증 및 중복 차단, 정부 과제 실적 로깅 서비스
시퀀스 3 (정규 검증), 시퀀스 4 (미지참자 구제), 시퀀스 5 (중복 수령 실시간 차단) 처리
"""
from typing import Dict, Any, Optional
from .cloud_db import CloudDatabase
from .custodial_agent import CustodialAgent
from ..core.security import ZeroPIISanitizer

class VerifierService:
    def __init__(self, db: CloudDatabase, custodial_agent: CustodialAgent):
        self.db = db
        self.custodial_agent = custodial_agent

    def verify_dining_access(
        self,
        sensor_id: str,
        nfc_uid: str,
        method: str = "NFC_TAG"
    ) -> Dict[str, Any]:
        """
        [시퀀스 3, 4, 5 통합 검증 파이프라인]
        1. 당일 중복 수령 상호배제 검사 (현장식사 + 도시락 중복 차단)
        2. Custodial Agent에 의한 익명 VP 동적 조합
        3. 암호학적 전자서명 및 W3C VC 유효성 검증
        4. 정부 과제 정량 실적 로깅 원장 기록
        """
        # 1. [시퀀스 5] 당일 중복 수령(Bunker) 차단 검사
        today_records = self.db.check_today_completed_meals(nfc_uid)
        if today_records:
            tx_id = self.db.log_dining_verification(
                sensor_id=sensor_id,
                nfc_uid=nfc_uid,
                result_status="DUPLICATE_BLOCKED",
                method=method,
                reason="당일 이미 식사 또는 도시락 수령을 완료하였습니다."
            )
            return {
                "status": "DENIED",
                "code": 403,
                "reason": "ALREADY_DINED_TODAY",
                "message": "오늘 이미 배식을 완료하셨습니다. (중복 수령 차단)",
                "tx_id": tx_id
            }

        # 2. Custodial Agent로부터 해당 센서용 VP 조합 요청
        vp = self.custodial_agent.assemble_presentation_for_sensor(nfc_uid, sensor_id)
        if not vp:
            tx_id = self.db.log_dining_verification(
                sensor_id=sensor_id,
                nfc_uid=nfc_uid,
                result_status="REJECTED",
                method=method,
                reason="해당 센서에 유효한 자격증명(VC)이 존재하지 않습니다."
            )
            return {
                "status": "DENIED",
                "code": 404,
                "reason": "NO_ELIGIBLE_VC",
                "message": "유효한 식사 수급 자격증명이 없습니다.",
                "tx_id": tx_id
            }

        # 3. 암호학적 서명 검증
        wallet = self.db.get_wallet(nfc_uid)
        is_valid = self.custodial_agent.vc_engine.verify_presentation(vp, wallet["key_id"])

        if not is_valid:
            tx_id = self.db.log_dining_verification(
                sensor_id=sensor_id,
                nfc_uid=nfc_uid,
                result_status="REJECTED",
                method=method,
                reason="VP 암호학적 서명 검증 실패"
            )
            return {
                "status": "DENIED",
                "code": 401,
                "reason": "INVALID_SIGNATURE",
                "message": "자격증명 위변조 또는 서명 오류입니다.",
                "tx_id": tx_id
            }

        # 4. 검증 성공: 정부 과제 실적 원장 로깅
        tx_id = self.db.log_dining_verification(
            sensor_id=sensor_id,
            nfc_uid=nfc_uid,
            result_status="APPROVED",
            method=method,
            reason="정상 자격 확인 및 승인"
        )

        return {
            "status": "APPROVED",
            "code": 200,
            "message": "배식 승인 완료 (정상 통과)",
            "verification_method": method,
            "sensor_id": sensor_id,
            "tx_id": tx_id
        }
