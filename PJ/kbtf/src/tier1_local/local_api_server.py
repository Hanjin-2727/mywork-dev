"""
[Tier 1 Local API Server] 관리사무소 로컬 PC 폐쇄망 HTTP API 서버
사설 Wi-Fi(192.168.0.x) 상에서 관리자 스마트폰 브라우저 요청 처리 (에어갭 격리)
"""
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any
from .local_db import LocalDatabase
from .resident_service import ResidentService

class LocalRequestHandler(BaseHTTPRequestHandler):
    resident_service: ResidentService = None

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

        # 1. 미지참자 구두 확인 엔드포인트: /api/residents/search
        if self.path == "/api/residents/search":
            building_no = req_data.get("building_no", "")
            room_no = req_data.get("room_no", "")
            birth_date = req_data.get("birth_date", "")
            officer_name = req_data.get("officer_name", "현장관리자")

            result = self.resident_service.verify_oral_identity(
                building_no=building_no,
                room_no=room_no,
                birth_date=birth_date,
                officer_name=officer_name
            )
            if result:
                self._send_json_response(200, result)
            else:
                self._send_json_response(404, {"status": "NOT_FOUND", "message": "거주자 명부에 일치하는 정보가 없습니다."})

        # 2. 대면 등록 엔드포인트: /api/residents/register
        elif self.path == "/api/residents/register":
            name = req_data.get("name", "")
            birth_date = req_data.get("birth_date", "")
            building_no = req_data.get("building_no", "")
            room_no = req_data.get("room_no", "")
            nfc_uid = req_data.get("nfc_uid", "")
            welfare_tier = req_data.get("welfare_tier", "TIER_A")

            res = self.resident_service.register_senior(
                name=name,
                birth_date=birth_date,
                building_no=building_no,
                room_no=room_no,
                nfc_uid=nfc_uid,
                welfare_tier=welfare_tier
            )
            self._send_json_response(200, res)

        else:
            self._send_json_response(404, {"error": "Not Found"})

    def log_message(self, format, *args):
        # 표준 에러 로그 억제
        pass

def create_local_api_server(service: ResidentService, host: str = "127.0.0.1", port: int = 8000) -> HTTPServer:
    LocalRequestHandler.resident_service = service
    server = HTTPServer((host, port), LocalRequestHandler)
    return server
