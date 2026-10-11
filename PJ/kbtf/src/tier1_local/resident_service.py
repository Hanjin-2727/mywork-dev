"""
[Tier 1 Resident Service] 관리사무소 대면 등록 및 미지참자 구두 확인 서비스
시퀀스 1 (대면 등록) 및 시퀀스 4 (에지 사설망 구제) 처리
"""
from typing import Dict, Any, Optional
from .local_db import LocalDatabase
from ..core.security import ZeroPIISanitizer

CHOSUNG_LIST = [
    'ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 
    'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'
]

def mask_korean_name_chosung(name: str) -> str:
    """한국어 성명을 초성 마스킹 (예: '김철수' -> 'ㄱㅊㅅ')"""
    result = []
    for char in name:
        code = ord(char) - 0xAC00
        if 0 <= code <= 11171:
            chosung_index = code // 588
            result.append(CHOSUNG_LIST[chosung_index])
        else:
            result.append(char)
    return "".join(result)

class ResidentService:
    def __init__(self, db: LocalDatabase):
        self.db = db

    def register_senior(
        self,
        name: str,
        birth_date: str,
        building_no: str,
        room_no: str,
        nfc_uid: str,
        welfare_tier: str = "TIER_A"
    ) -> Dict[str, Any]:
        """
        [시퀀스 1] 2G폰 어르신 창구 대면 등록.
        로컬 DB에 개인정보를 영구 보관하고, 클라우드로 보낼 Zero-PII 페이로드를 생성하여 반환.
        """
        resident_id = self.db.insert_resident(
            name=name,
            birth_date=birth_date,
            building_no=building_no,
            room_no=room_no,
            nfc_uid=nfc_uid,
            welfare_tier=welfare_tier
        )

        # 클라우드로 전송할 페이로드 (개인정보 0% 보장)
        cloud_payload = {
            "uid": nfc_uid,
            "tier": welfare_tier
        }
        # Zero-PII 감사
        ZeroPIISanitizer.audit_payload(cloud_payload)

        return {
            "status": "LOCAL_REGISTERED",
            "resident_id": resident_id,
            "cloud_payload": cloud_payload
        }

    def verify_oral_identity(
        self,
        building_no: str,
        room_no: str,
        birth_date: str,
        officer_name: str = "현장확인관"
    ) -> Optional[Dict[str, Any]]:
        """
        [시퀀스 4] 카드 미지참자 현장 에지 사설망 구두 확인.
        관리자 스마트폰 브라우저에 성명 초성과 NFC UID를 반환하여 즉시 배식 승인을 가능하게 함.
        """
        resident = self.db.find_resident_by_oral_info(building_no, room_no, birth_date)
        if not resident:
            return None

        # 감사 로그 기록
        self.db.log_manual_check(resident["resident_id"], officer_name, check_reason="CARD_LEFT_HOME")

        masked_name = mask_korean_name_chosung(resident["resident_name"])
        
        return {
            "status": "MATCHED",
            "masked_name": masked_name, # 예: 'ㄱㅊㅅ'
            "nfc_uid": resident["nfc_uid"],
            "welfare_tier": resident["welfare_tier"]
        }
