"""
[Tier 3 Cloud API Server] 공공클라우드 CSAP '하' Zero-PII REST API 서버
경로식당 센서 및 관리사무소로부터 비식별 난수 패킷 수신 및 검증 처리
"""
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any
from .custodial_agent import CustodialAgent
from .verifier_service import VerifierService
from .batch_anchorer import DailyBatchAnchorer
from ..core.security import ZeroPIISanitizer

class CloudRequestHandler(BaseHTTPRequestHandler):
    custodial_agent: CustodialAgent = None
    verifier_service: VerifierService = None
    batch_anchorer: DailyBatchAnchorer = None

    def _send_json_response(self, status_code: int, data: Dict[str, Any]):
        response_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            req_data = json.loads(body)
        except Exception:
            self._send_json_response(400, {"error": "Invalid JSON"})
            return

        # [필수 감사] 클라우드로 수신된 페이로드 Zero-PII 검증
        try:
            ZeroPIISanitizer.audit_payload(req_data)
        except Exception as e:
            self._send_json_response(403, {"error": f"Zero-PII Compliance Violation: {str(e)}"})
            return

        # 1. 익명 DID 등록: /api/v1/custodial/register
        if self.path == "/api/v1/custodial/register":
            uid = req_data.get("uid")
            tier = req_data.get("tier", "TIER_A")
            res = self.custodial_agent.register_custodial_identity(uid, tier)
            self._send_json_response(200, res)

        # 2. 2주 엑셀 배치 VC 발급: /api/v1/vc/batch-issue
        elif self.path == "/api/v1/vc/batch-issue":
            res = self.custodial_agent.process_batch_vc_issuance(req_data)
            self._send_json_response(200, res)

        # 3. 경로식당 식사/도시락 검증: /api/v1/dining/verify
        elif self.path == "/api/v1/dining/verify":
            sensor_id = req_data.get("sensor_id")
            nfc_uid = req_data.get("nfc_uid")
            method = req_data.get("method", "NFC_TAG")
            res = self.verifier_service.verify_dining_access(sensor_id, nfc_uid, method)
            self._send_json_response(res.get("code", 200), res)

        # 4. 일일 18시 온체인 배치 앵커링: /api/v1/kpi/anchor-batch
        elif self.path == "/api/v1/kpi/anchor-batch":
            target_date = req_data.get("target_date")
            res = self.batch_anchorer.execute_daily_anchoring(target_date)
            self._send_json_response(200, res)

        else:
            self._send_json_response(404, {"error": "Not Found"})

    def do_GET(self):
        # 5. 센서용 화이트리스트 동기화: /api/v1/dining/whitelist
        if self.path == "/api/v1/dining/whitelist":
            with self.custodial_agent.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT nfc_uid FROM custodial_wallets WHERE is_active = 1")
                rows = cursor.fetchall()
                uids = [r["nfc_uid"] for r in rows]
            self._send_json_response(200, {"active_uids": uids, "total": len(uids)})
        else:
            self._send_json_response(404, {"error": "Not Found"})

    def log_message(self, format, *args):
        pass

def create_cloud_api_server(
    custodial_agent: CustodialAgent,
    verifier_service: VerifierService,
    batch_anchorer: DailyBatchAnchorer,
    host: str = "127.0.0.1",
    port: int = 8080
) -> HTTPServer:
    CloudRequestHandler.custodial_agent = custodial_agent
    CloudRequestHandler.verifier_service = verifier_service
    CloudRequestHandler.batch_anchorer = batch_anchorer
    server = HTTPServer((host, port), CloudRequestHandler)
    return server
