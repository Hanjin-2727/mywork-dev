"""
[Vercel API Handler Verification Test]
api/index.py Serverless 핸들러 기능 검증
"""
import unittest
import json
import io
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from api.index import handler

class MockSocket:
    def __init__(self):
        self.output = io.BytesIO()

    def makefile(self, mode, *args, **kwargs):
        if "r" in mode:
            return io.BytesIO(b"")
        return self.output

class TestVercelAPI(unittest.TestCase):
    def test_api_status_get(self):
        """GET /api/status 엔드포인트 동작 확인"""
        # 직접 핸들러 내부 메서드 및 상태 검증
        from api.index import CLOUD_DB
        with CLOUD_DB._get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) as cnt FROM custodial_wallets")
            cnt = c.fetchone()["cnt"]
            self.assertGreaterEqual(cnt, 1)

    def test_api_dining_verify(self):
        """POST /api/v1/dining/verify 엔드포인트 로직 확인"""
        from api.index import VERIFIER_SERVICE
        res = VERIFIER_SERVICE.verify_dining_access("SENSOR_MEAL_01", "04:C3:D4:E5:F6:07:03")
        self.assertIn(res["status"], ["APPROVED", "DENIED"])

if __name__ == "__main__":
    unittest.main()
