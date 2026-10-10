#!/usr/bin/env python3
"""
[Local Web Server] K-BTF Vercel 로컬 개발 및 시연 웹 서버
Vercel 환경과 동일하게 정적 파일(public/)과 API(api/index.py)를 포트 3000에서 단일 서빙
"""
import sys
import os
import io
import mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from api.index import handler as VercelApiHandler

PUBLIC_DIR = os.path.join(PROJECT_ROOT, "public")

class LocalUnifiedDevServer(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        VercelApiHandler.do_OPTIONS(self)

    def do_GET(self):
        if self.path.startswith("/api/"):
            VercelApiHandler.do_GET(self)
        else:
            self._serve_static()

    def do_POST(self):
        if self.path.startswith("/api/"):
            VercelApiHandler.do_POST(self)
        else:
            self.send_error(405, "Method Not Allowed")

    def _serve_static(self):
        clean_path = self.path.split("?")[0]
        if clean_path in ("/", ""):
            clean_path = "/index.html"

        file_path = os.path.join(PUBLIC_DIR, clean_path.lstrip("/"))
        if os.path.isdir(file_path):
            file_path = os.path.join(file_path, "index.html")

        if not os.path.isfile(file_path):
            self.send_error(404, f"File Not Found: {clean_path}")
            return

        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = mime_type or "application/octet-stream"

        try:
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", mime_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Internal Error: {str(e)}")

    def log_message(self, format, *args):
        # 콘솔 깔끔한 요청 로그
        print(f"[{self.log_date_time_string()}] {args[0]}")

def run(host="127.0.0.1", port=3000):
    server = HTTPServer((host, port), LocalUnifiedDevServer)
    print("=" * 70)
    print(f"🚀 K-BTF Stage 1 로컬 Vercel 웹 서버가 시작되었습니다.")
    print(f"👉 브라우저 접속 주소: http://{host}:{port}")
    print(f"👉 Vercel 배포 시에는 'git push'만으로 자동 배포됩니다.")
    print("=" * 70)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n웹 서버를 정상 종료합니다.")

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    run(port=port)
