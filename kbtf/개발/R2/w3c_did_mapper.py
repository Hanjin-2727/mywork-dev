"""
[Release 2 - Sprint 3] W3C 표준 DID 발급 및 비식별 난수 UID 매핑 모듈
"""
import uuid
import hashlib
from typing import Dict

class W3CDIDManager:
    def __init__(self):
        # 실명 개인정보는 완전히 격리된 가상 저장소에만 보관하고 온체인/외부망에는 비식별 UID만 노출
        self._private_isolated_db = {}
        self.did_registry = {}

    def issue_did(self, resident_real_name: str, resident_ssn_hash: str) -> Dict[str, str]:
        # 1. 암호학적 비식별 난수 생성 (UUID v4 + Salt Hash)
        raw_seed = f"{uuid.uuid4()}-{resident_ssn_hash}"
        pseudo_uid = hashlib.sha256(raw_seed.encode()).hexdigest()[:32]
        
        # 2. W3C 표준 규격 DID 문자열 생성
        did_identifier = f"did:kbtf:resident:{pseudo_uid}"
        
        # 3. 비식별 난수 매핑 테이블 정합
        self.did_registry[pseudo_uid] = {
            "did": did_identifier,
            "status": "ACTIVE",
            "auth_type": "W3C_DID_v1.0"
        }
        
        # 개인정보 가상 격리 저장
        self._private_isolated_db[pseudo_uid] = {
            "masked_name": resident_real_name[0] + "*" + resident_real_name[-1] if len(resident_real_name) > 1 else "*",
            "registered": True
        }
        
        return {
            "pseudo_uid": pseudo_uid,
            "did": did_identifier,
            "message": "W3C 표준 DID 발급 및 비식별 난수 매핑 완료 (개인정보 격리 완료)"
        }

    def verify_did(self, pseudo_uid: str) -> bool:
        return pseudo_uid in self.did_registry and self.did_registry[pseudo_uid]["status"] == "ACTIVE"
