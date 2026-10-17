"""
[Vercel Serverless Function] K-BTF API Gateway (api/index.py)
Zero-PII 및 CSAP '하' 등급 아키텍처를 Vercel 서버리스 런타임에서 완벽 구동
"""
import sys
import os
import json
import urllib.parse
from http.server import BaseHTTPRequestHandler

# 프로젝트 루트 경로를 sys.path에 추가하여 src 모듈 임포트
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.core.did_kms import CustodialKMS
from src.core.security import ZeroPIISanitizer
from src.tier1_local.local_db import LocalDatabase
from src.tier1_local.resident_service import ResidentService
from src.tier1_local.batch_preprocessor import BatchPreprocessor
from src.tier3_cloud.cloud_db import CloudDatabase
from src.tier3_cloud.custodial_agent import CustodialAgent
from src.tier3_cloud.verifier_service import VerifierService
from src.tier3_cloud.batch_anchorer import DailyBatchAnchorer

# 전역 싱글톤 인스턴스 (서버리스 웜 스타트 캐시)
LOCAL_DB = LocalDatabase()
CLOUD_DB = CloudDatabase()
KMS = CustodialKMS()

RESIDENT_SERVICE = ResidentService(LOCAL_DB)
BATCH_PREPROCESSOR = BatchPreprocessor(LOCAL_DB)
CUSTODIAL_AGENT = CustodialAgent(CLOUD_DB, KMS)
VERIFIER_SERVICE = VerifierService(CLOUD_DB, CUSTODIAL_AGENT)
BATCH_ANCHORER = DailyBatchAnchorer(CLOUD_DB)

# 데모용 기본 거주자 및 VC 사전 등록 (초기 체험용)
def _seed_initial_demo_data():
    demo_residents = [
        {"name": "김만석", "birth_date": "480514", "building_no": "101동", "room_no": "1204호", "nfc_uid": "04:A1:B2:C3:D4:E5:01", "meal_type": "MEAL"},
        {"name": "이영자", "birth_date": "510920", "building_no": "102동", "room_no": "305호", "nfc_uid": "04:B2:C3:D4:E5:F6:02", "meal_type": "BENTO"},
        {"name": "박철수", "birth_date": "451203", "building_no": "103동", "room_no": "708호", "nfc_uid": "04:C3:D4:E5:F6:07:03", "meal_type": "MEAL"}
    ]
    for r in demo_residents:
        RESIDENT_SERVICE.register_senior(
            name=r["name"],
            birth_date=r["birth_date"],
            building_no=r["building_no"],
            room_no=r["room_no"],
            nfc_uid=r["nfc_uid"],
            welfare_tier="TIER_A"
        )
        CUSTODIAL_AGENT.register_custodial_identity(r["nfc_uid"], "TIER_A")
    
    # 2주 배치 VC 발급
    BATCH_PREPROCESSOR.process_excel_records(demo_residents)
    CUSTODIAL_AGENT.process_batch_vc_issuance({
        "meal_uids": ["04:A1:B2:C3:D4:E5:01", "04:C3:D4:E5:F6:07:03"],
        "bento_uids": ["04:B2:C3:D4:E5:F6:02"]
    })

_seed_initial_demo_data()

class handler(BaseHTTPRequestHandler):
    def _send_json(self, status_code: int, data: dict):
        resp = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(resp)))
        self.end_headers()
        self.wfile.write(resp)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # 1. 상태 조회: /api/status 또는 /api/v1/status
        if path in ("/api/status", "/api/v1/status"):
            with CLOUD_DB._get_connection() as conn:
                c = conn.cursor()
                c.execute("SELECT COUNT(*) as cnt FROM custodial_wallets")
                wallet_cnt = c.fetchone()["cnt"]
                c.execute("SELECT COUNT(*) as cnt FROM verifiable_credentials")
                vc_cnt = c.fetchone()["cnt"]
                c.execute("SELECT COUNT(*) as cnt FROM dining_verification_logs WHERE result_status = 'APPROVED'")
                approved_cnt = c.fetchone()["cnt"]
                c.execute("SELECT COUNT(*) as cnt FROM dining_verification_logs WHERE result_status = 'DUPLICATE_BLOCKED'")
                blocked_cnt = c.fetchone()["cnt"]

            self._send_json(200, {
                "status": "HEALTHY",
                "stage": "STAGE_1_MOCK_CHAIN_VERCEL",
                "compliance": "CSAP_LOWER_ZERO_PII",
                "stats": {
                    "total_wallets": wallet_cnt,
                    "total_active_vcs": vc_cnt,
                    "meals_approved": approved_cnt,
                    "duplicates_blocked": blocked_cnt
                }
            })

        # 2. 최근 로그 조회: /api/v1/logs
        elif path == "/api/v1/logs":
            with CLOUD_DB._get_connection() as conn:
                c = conn.cursor()
                c.execute("SELECT * FROM dining_verification_logs ORDER BY verified_at DESC LIMIT 15")
                rows = [dict(r) for r in c.fetchall()]
            self._send_json(200, {"logs": rows})

        else:
            self._send_json(404, {"error": "Not Found", "path": path})

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            req_data = json.loads(body)
        except Exception:
            self._send_json(400, {"error": "Invalid JSON"})
            return

        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # [Zero-PII 클라우드 API 감사]
        if path.startswith("/api/v1/"):
            try:
                ZeroPIISanitizer.audit_payload(req_data)
            except Exception as e:
                self._send_json(403, {"error": f"CSAP '하' Zero-PII Compliance Violation: {str(e)}"})
                return

        # 1. 센서 태깅 및 0.05초 선확인 검증: /api/v1/dining/verify
        if path == "/api/v1/dining/verify":
            sensor_id = req_data.get("sensor_id", "SENSOR_MEAL_01")
            nfc_uid = req_data.get("nfc_uid")
            method = req_data.get("method", "NFC_TAG")
            res = VERIFIER_SERVICE.verify_dining_access(sensor_id, nfc_uid, method)
            self._send_json(res.get("code", 200), res)

        # 2. 미지참자 현장 에지 사설망 구두 확인 (생년월일 단일 확인): /api/residents/search
        elif path == "/api/residents/search":
            birth_date = str(req_data.get("birth_date", "")).strip()
            building_no = req_data.get("building_no", "").strip() or None
            room_no = req_data.get("room_no", "").strip() or None
            officer_name = req_data.get("officer_name", "현장관리자")

            res = RESIDENT_SERVICE.verify_oral_identity(
                birth_date=birth_date,
                building_no=building_no,
                room_no=room_no,
                officer_name=officer_name
            )
            if res:
                self._send_json(200, res)
            else:
                self._send_json(404, {"status": "NOT_FOUND", "message": "거주자 명부에 일치하는 생년월일 정보가 없습니다."})

        # 3. 일일 18시 온체인 배치 앵커링: /api/v1/kpi/anchor-batch
        elif path == "/api/v1/kpi/anchor-batch":
            target_date = req_data.get("target_date")
            res = BATCH_ANCHORER.execute_daily_anchoring(target_date)
            self._send_json(200, res)

        # 4. 신규 대면 등록: /api/residents/register
        elif path == "/api/residents/register":
            name = req_data.get("name")
            birth_date = req_data.get("birth_date")
            building_no = req_data.get("building_no")
            room_no = req_data.get("room_no")
            nfc_uid = req_data.get("nfc_uid")
            tier = req_data.get("tier", "TIER_A")
            
            local_res = RESIDENT_SERVICE.register_senior(name, birth_date, building_no, room_no, nfc_uid, tier)
            cloud_res = CUSTODIAL_AGENT.register_custodial_identity(nfc_uid, tier)
            CUSTODIAL_AGENT.process_batch_vc_issuance({"meal_uids": [nfc_uid], "bento_uids": []})
            
            self._send_json(200, {
                "local": local_res,
                "cloud": cloud_res,
                "message": "대면 등록 및 Custodial DID/VC 발급 완료"
            })

        else:
            self._send_json(404, {"error": "Not Found", "path": path})

    def log_message(self, format, *args):
        pass
