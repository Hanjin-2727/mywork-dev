"""
[Tier 1 Local DB] 관리사무소 온프레미스 폐쇄망 데이터베이스
개인정보(성명, 생년월일, 동호수) ↔ 하드웨어 NFC UID 매핑 영구 보관 (외부 인터넷 직접 연결 차단)
"""
import sqlite3
import os
import uuid
from typing import Dict, Any, List, Optional

class LocalDatabase:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        if self.db_path == ":memory:":
            self._persistent_conn = sqlite3.connect(":memory:")
            self._persistent_conn.row_factory = sqlite3.Row
        else:
            self._persistent_conn = None
        self._init_schema()

    def _get_connection(self):
        if self._persistent_conn:
            return self._persistent_conn
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS local_residents (
                resident_id TEXT PRIMARY KEY,
                resident_name TEXT NOT NULL,
                birth_date TEXT NOT NULL,
                building_no TEXT NOT NULL,
                room_no TEXT NOT NULL,
                phone_number TEXT,
                nfc_uid TEXT UNIQUE NOT NULL,
                welfare_tier TEXT DEFAULT 'TIER_A',
                status TEXT DEFAULT 'ACTIVE',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS local_card_inventory (
                card_id TEXT PRIMARY KEY,
                card_serial TEXT UNIQUE NOT NULL,
                nfc_uid TEXT UNIQUE NOT NULL,
                inventory_status TEXT DEFAULT 'AVAILABLE',
                issued_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS local_manual_audit_logs (
                log_id TEXT PRIMARY KEY,
                resident_id TEXT NOT NULL,
                officer_name TEXT NOT NULL,
                check_reason TEXT DEFAULT 'CARD_LEFT_HOME',
                checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (resident_id) REFERENCES local_residents(resident_id)
            );
            """)
            conn.commit()

    def insert_resident(self, name: str, birth_date: str, building_no: str, room_no: str, nfc_uid: str, welfare_tier: str = "TIER_A", phone: str = "") -> str:
        resident_id = str(uuid.uuid4())
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO local_residents (resident_id, resident_name, birth_date, building_no, room_no, phone_number, nfc_uid, welfare_tier)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (resident_id, name, birth_date, building_no, room_no, phone, nfc_uid, welfare_tier))
            conn.commit()
        return resident_id

    def find_resident_by_oral_info(
        self,
        birth_date: str,
        building_no: Optional[str] = None,
        room_no: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if building_no and room_no:
                cursor.execute("""
                SELECT * FROM local_residents 
                WHERE building_no = ? AND room_no = ? AND birth_date = ? AND status = 'ACTIVE'
                """, (building_no, room_no, birth_date))
            else:
                cursor.execute("""
                SELECT * FROM local_residents 
                WHERE birth_date = ? AND status = 'ACTIVE'
                """, (birth_date,))
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None

    def log_manual_check(self, resident_id: str, officer_name: str, check_reason: str = "CARD_LEFT_HOME") -> str:
        log_id = str(uuid.uuid4())
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO local_manual_audit_logs (log_id, resident_id, officer_name, check_reason)
            VALUES (?, ?, ?, ?)
            """, (log_id, resident_id, officer_name, check_reason))
            conn.commit()
        return log_id
