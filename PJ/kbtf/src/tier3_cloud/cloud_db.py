"""
[Tier 3 Cloud DB] 공공클라우드 CSAP '하' 등급 Zero-PII 데이터베이스
개인식별정보 0% 보장: 하드웨어 NFC UID, W3C DID, VC/VP 검증 로그, KPI 집계 원장 관리
"""
import sqlite3
import uuid
import json
from datetime import datetime, date, timezone
from typing import Dict, Any, List, Optional
from ..core.security import ZeroPIISanitizer

class CloudDatabase:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        if self.db_path == ":memory:":
            self._persistent_conn = sqlite3.connect(":memory:")
            self._persistent_conn.row_factory = sqlite3.Row
        else:
            self._persistent_conn = None
        self._init_schema()
        self._init_default_policies()

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
            CREATE TABLE IF NOT EXISTS custodial_wallets (
                nfc_uid TEXT PRIMARY KEY,
                custodial_did TEXT UNIQUE NOT NULL,
                public_key TEXT NOT NULL,
                key_id TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS verifiable_credentials (
                vc_id TEXT PRIMARY KEY,
                nfc_uid TEXT NOT NULL,
                credential_type TEXT NOT NULL,
                service_domain TEXT NOT NULL,
                is_eligible INTEGER DEFAULT 1,
                subsidy_tier TEXT DEFAULT 'TIER_A',
                issuance_date TEXT NOT NULL,
                expiration_date TEXT NOT NULL,
                vc_payload TEXT NOT NULL,
                FOREIGN KEY (nfc_uid) REFERENCES custodial_wallets(nfc_uid)
            );
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS sensor_policies (
                sensor_id TEXT PRIMARY KEY,
                location_name TEXT NOT NULL,
                target_vc_type TEXT NOT NULL,
                daily_limit INTEGER DEFAULT 1,
                is_active INTEGER DEFAULT 1
            );
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS dining_verification_logs (
                tx_id TEXT PRIMARY KEY,
                sensor_id TEXT NOT NULL,
                nfc_uid TEXT NOT NULL,
                result_status TEXT NOT NULL,
                verification_method TEXT DEFAULT 'NFC_TAG',
                failure_reason TEXT,
                verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_kpi_aggregates (
                report_date TEXT PRIMARY KEY,
                total_meal_count INTEGER DEFAULT 0,
                total_bento_count INTEGER DEFAULT 0,
                total_unique_users INTEGER DEFAULT 0,
                duplicate_prevented INTEGER DEFAULT 0,
                manual_pass_count INTEGER DEFAULT 0,
                onchain_tx_hash TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            conn.commit()

    def _init_default_policies(self):
        """센서 정책 기본 테이블 세팅"""
        policies = [
            ("SENSOR_MEAL_01", "경로식당 1라인 (현장식사 배식대)", "CommunityMealCredential", 1),
            ("SENSOR_BENTO_02", "경로식당 2라인 (도시락 배부처)", "WelfareBentoCredential", 1),
            ("SENSOR_HEALTH_01", "단지 내 헬스케어센터", "ResidentHealthCredential", 2),
            ("SENSOR_DOOR_01", "커뮤니티센터 주출입구", "ComplexAccessCredential", 10)
        ]
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for p in policies:
                cursor.execute("""
                INSERT OR IGNORE INTO sensor_policies (sensor_id, location_name, target_vc_type, daily_limit)
                VALUES (?, ?, ?, ?)
                """, p)
            conn.commit()

    def save_custodial_wallet(self, nfc_uid: str, did: str, public_key: str, key_id: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO custodial_wallets (nfc_uid, custodial_did, public_key, key_id)
            VALUES (?, ?, ?, ?)
            """, (nfc_uid, did, public_key, key_id))
            conn.commit()

    def get_wallet(self, nfc_uid: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM custodial_wallets WHERE nfc_uid = ? AND is_active = 1", (nfc_uid,))
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None

    def save_vc(self, vc: Dict[str, Any], nfc_uid: str):
        vc_id = vc["id"]
        cred_type = [t for t in vc["type"] if t != "VerifiableCredential"][0]
        domain = vc["credentialSubject"].get("service_domain", "GENERAL")
        tier = vc["credentialSubject"].get("subsidy_tier", "TIER_A")
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO verifiable_credentials 
            (vc_id, nfc_uid, credential_type, service_domain, is_eligible, subsidy_tier, issuance_date, expiration_date, vc_payload)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (vc_id, nfc_uid, cred_type, domain, 1, tier, vc["issuanceDate"], vc["expirationDate"], json.dumps(vc)))
            conn.commit()

    def get_active_vcs(self, nfc_uid: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT vc_payload FROM verifiable_credentials WHERE nfc_uid = ?", (nfc_uid,))
            rows = cursor.fetchall()
            return [json.loads(r["vc_payload"]) for r in rows]

    def get_sensor_policy(self, sensor_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sensor_policies WHERE sensor_id = ? AND is_active = 1", (sensor_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None

    def log_dining_verification(self, sensor_id: str, nfc_uid: str, result_status: str, method: str = "NFC_TAG", reason: str = "") -> str:
        tx_id = str(uuid.uuid4())
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO dining_verification_logs (tx_id, sensor_id, nfc_uid, result_status, verification_method, failure_reason)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (tx_id, sensor_id, nfc_uid, result_status, method, reason))
            conn.commit()
        return tx_id

    def check_today_completed_meals(self, nfc_uid: str) -> List[Dict[str, Any]]:
        """당일 이미 성공한 식사/도시락 수령 이력 조회"""
        today_start = date.today().isoformat() + " 00:00:00"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT * FROM dining_verification_logs
            WHERE nfc_uid = ? AND result_status = 'APPROVED' AND verified_at >= ?
            """, (nfc_uid, today_start))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def purge_logs_older_than_7_days(self) -> int:
        """7일 경과 상세 로그 자동 영구 파기 (국정원 보안 및 프라이버시 컴플라이언스)"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            DELETE FROM dining_verification_logs 
            WHERE verified_at < datetime('now', '-7 days')
            """)
            deleted = cursor.rowcount
            conn.commit()
            return deleted
