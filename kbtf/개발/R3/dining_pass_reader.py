"""
[Release 3 - Sprint 6] 산남종합사회복지관 경로식당 1초 식사패스 인증 모듈
"""
import time
from datetime import datetime
from typing import Dict

class DiningPassReader:
    def __init__(self, nfc_manager):
        self.nfc_manager = nfc_manager
        self.today_meal_logs = []

    def process_meal_tag(self, nfc_chip_uid: str) -> Dict:
        """경로식당 배식구 무선 태깅 시 1초 내 식사 자격 승인"""
        start_time = time.time()
        
        did_uid = self.nfc_manager.resolve_did_by_nfc(nfc_chip_uid)
        if not did_uid:
            return {
                "auth_result": "DENIED",
                "reason": "미등록 또는 비활성화된 NFC 카드",
                "response_time_ms": int((time.time() - start_time) * 1000)
            }

        # 1초 식사패스 승인 기록
        log_entry = {
            "did_uid": did_uid,
            "tag_time": datetime.utcnow().isoformat(),
            "location": "산남종합사회복지관 경로식당 배식구 1호기",
            "status": "PASS"
        }
        self.today_meal_logs.append(log_entry)
        elapsed_ms = int((time.time() - start_time) * 1000)

        return {
            "auth_result": "PASS",
            "message": "식사패스 승인 완료 (1초 인증 성공)",
            "response_time_ms": elapsed_ms,
            "log": log_entry
        }
