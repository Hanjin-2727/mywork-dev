"""
[Release 3 - Sprint 5] 420세대 실물 NFC 목걸이 주민증 발급 & UID 매핑 모듈
"""
from typing import Dict, Optional

class NFCCardManager:
    def __init__(self):
        # nfc_card_uid => pseudo_did_uid 매핑
        self.nfc_registry = {}

    def register_nfc_necklace(self, household_number: str, nfc_chip_uid: str, pseudo_did_uid: str) -> Dict:
        """420세대 실물 NFC 목걸이 주민증 등록"""
        record = {
            "household": household_number,
            "nfc_chip_uid": nfc_chip_uid,
            "pseudo_did_uid": pseudo_did_uid,
            "card_type": "NFC_NECKLACE_V1",
            "is_active": True
        }
        self.nfc_registry[nfc_chip_uid] = record
        return {
            "status": "SUCCESS",
            "household": household_number,
            "nfc_chip_uid": nfc_chip_uid,
            "message": "실물 NFC 목걸이 주민증 활성화 및 DID 연계 완료"
        }

    def resolve_did_by_nfc(self, nfc_chip_uid: str) -> Optional[str]:
        """NFC 태깅 시 연동된 DID 반환"""
        if nfc_chip_uid in self.nfc_registry and self.nfc_registry[nfc_chip_uid]["is_active"]:
            return self.nfc_registry[nfc_chip_uid]["pseudo_did_uid"]
        return None
