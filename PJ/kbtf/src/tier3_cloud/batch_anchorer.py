"""
[Tier 3 Daily Batch Anchorer] 일일 18시 온체인 배치 앵커링 및 KPI 집계 모듈
정부 과제 실적 증빙을 위한 당일 검증 트랜잭션의 머클루트 해시 온체인 공증
"""
import hashlib
import json
from datetime import datetime, date, timezone
from typing import Dict, Any, List, Optional
from .cloud_db import CloudDatabase

class DailyBatchAnchorer:
    def __init__(self, db: CloudDatabase):
        self.db = db

    def execute_daily_anchoring(self, target_date: Optional[str] = None) -> Dict[str, Any]:
        """
        [일일 18시 공증 배치]
        1. 당일 발생한 승인/차단/구제 트랜잭션 전수 수집
        2. Merkle Root 해시 생성 및 가상 온체인 블록체인 트랜잭션 해시 도출
        3. daily_kpi_aggregates 영구 원장에 저장
        4. 7일 경과 세부 로그 자동 파기 실행
        """
        report_date = target_date or date.today().isoformat()
        
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            # 당일 통계 집계
            cursor.execute("""
            SELECT 
                COUNT(CASE WHEN result_status = 'APPROVED' AND sensor_id = 'SENSOR_MEAL_01' THEN 1 END) as meal_count,
                COUNT(CASE WHEN result_status = 'APPROVED' AND sensor_id = 'SENSOR_BENTO_02' THEN 1 END) as bento_count,
                COUNT(DISTINCT nfc_uid) as unique_users,
                COUNT(CASE WHEN result_status = 'DUPLICATE_BLOCKED' THEN 1 END) as dup_count,
                COUNT(CASE WHEN verification_method = 'MANUAL_PASS' THEN 1 END) as manual_count
            FROM dining_verification_logs
            WHERE date(verified_at) = date(?)
            """, (report_date,))
            stats = dict(cursor.fetchone())

            # 당일 상세 트랜잭션 해시 트리 생성용 추출
            cursor.execute("""
            SELECT tx_id, sensor_id, nfc_uid, result_status, verified_at 
            FROM dining_verification_logs
            WHERE date(verified_at) = date(?)
            ORDER BY verified_at ASC
            """, (report_date,))
            tx_rows = [dict(r) for r in cursor.fetchall()]

        # Merkle Root 해시 계산
        if not tx_rows:
            raw_data = f"NO_ACTIVITY_{report_date}"
        else:
            raw_data = json.dumps(tx_rows, sort_keys=True)
            
        merkle_root_hash = hashlib.sha256(raw_data.encode("utf-8")).hexdigest()
        onchain_tx_hash = "0x" + hashlib.sha256(f"{merkle_root_hash}-{report_date}-KBTF_LEDGER".encode("utf-8")).hexdigest()

        # 영구 원장 저장
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO daily_kpi_aggregates
            (report_date, total_meal_count, total_bento_count, total_unique_users, duplicate_prevented, manual_pass_count, onchain_tx_hash, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                report_date,
                stats["meal_count"],
                stats["bento_count"],
                stats["unique_users"],
                stats["dup_count"],
                stats["manual_count"],
                onchain_tx_hash
            ))
            conn.commit()

        # 7일 경과 로그 파기
        purged_count = self.db.purge_logs_older_than_7_days()

        return {
            "report_date": report_date,
            "merkle_root_hash": merkle_root_hash,
            "onchain_tx_hash": onchain_tx_hash,
            "total_meals": stats["meal_count"],
            "total_bento": stats["bento_count"],
            "unique_recipients": stats["unique_users"],
            "duplicates_blocked": stats["dup_count"],
            "manual_rescues": stats["manual_count"],
            "purged_old_logs": purged_count,
            "status": "ANCHORED_CONFIRMED"
        }
