"""
[Tier 1 Batch Preprocessor] 2주 주기 수급자 엑셀 명단 비식별 분리 전처리기
시퀀스 2 (엑셀 배치 업로드) 처리: 개인정보는 로컬에 격리하고 식사유형별 UID 목록만 클라우드로 추출
"""
from typing import Dict, Any, List
from .local_db import LocalDatabase
from ..core.security import ZeroPIISanitizer

class BatchPreprocessor:
    def __init__(self, db: LocalDatabase):
        self.db = db

    def process_excel_records(self, raw_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        [시퀀스 2] 원본 엑셀 행을 읽어 개인정보는 로컬 DB에 반영하고,
        클라우드 발송용 비식별 UID 목록을 2-1(현장식사)과 2-2(도시락)로 분리 추출.
        """
        meal_uids = []
        bento_uids = []

        for row in raw_records:
            # 1. 로컬 폐쇄망 DB에 인적사항 적재/갱신
            self.db.insert_resident(
                name=row["name"],
                birth_date=row["birth_date"],
                building_no=row["building_no"],
                room_no=row["room_no"],
                nfc_uid=row["nfc_uid"],
                welfare_tier=row.get("welfare_tier", "TIER_A"),
                phone=row.get("phone", "")
            )

            # 2. 식사 유형에 따라 비식별 UID 분기
            meal_type = row.get("meal_type", "MEAL").upper()
            if meal_type == "BENTO":
                bento_uids.append(row["nfc_uid"])
            else:
                meal_uids.append(row["nfc_uid"])

        # 클라우드로 전송할 최종 배치 페이로드
        batch_payload = {
            "batch_cycle": "2_WEEKS",
            "meal_uids": meal_uids,
            "bento_uids": bento_uids,
            "total_count": len(meal_uids) + len(bento_uids)
        }

        # Zero-PII 감사 실행
        ZeroPIISanitizer.audit_payload(batch_payload)

        return {
            "status": "PREPROCESSED_SUCCESS",
            "local_saved_count": len(raw_records),
            "cloud_payload": batch_payload
        }
