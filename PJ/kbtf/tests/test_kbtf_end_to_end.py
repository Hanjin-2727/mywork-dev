"""
[K-BTF E2E Test Suite]
5대 핵심 시나리오 및 CSAP '하' 등급 Zero-PII 컴플라이언스 통합 자동화 테스트
"""
import unittest
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.did_kms import CustodialKMS
from src.core.security import ZeroPIISanitizer, ZeroPIISanitizationError
from src.tier1_local.local_db import LocalDatabase
from src.tier1_local.resident_service import ResidentService, mask_korean_name_chosung
from src.tier1_local.batch_preprocessor import BatchPreprocessor
from src.tier3_cloud.cloud_db import CloudDatabase
from src.tier3_cloud.custodial_agent import CustodialAgent
from src.tier3_cloud.verifier_service import VerifierService
from src.tier3_cloud.batch_anchorer import DailyBatchAnchorer
from src.edge_terminal.sensor_reader import DiningSensorTerminal

class TestKBTFEndToEnd(unittest.TestCase):
    def setUp(self):
        self.local_db = LocalDatabase()
        self.cloud_db = CloudDatabase()
        self.kms = CustodialKMS()

        self.resident_service = ResidentService(self.local_db)
        self.batch_preprocessor = BatchPreprocessor(self.local_db)
        self.custodial_agent = CustodialAgent(self.cloud_db, self.kms)
        self.verifier_service = VerifierService(self.cloud_db, self.custodial_agent)
        self.batch_anchorer = DailyBatchAnchorer(self.cloud_db)

        self.sensor_meal = DiningSensorTerminal("SENSOR_MEAL_01", "경로식당 1라인", self.verifier_service)
        self.sensor_bento = DiningSensorTerminal("SENSOR_BENTO_02", "경로식당 2라인", self.verifier_service)

    def test_sequence_1_resident_registration_and_did(self):
        """[시퀀스 1] 대면 등록 및 익명 Custodial DID 발급 검증"""
        nfc_uid = "04:AA:BB:CC:DD:EE:01"
        reg = self.resident_service.register_senior(
            name="홍길동",
            birth_date="450101",
            building_no="101동",
            room_no="1001호",
            nfc_uid=nfc_uid,
            welfare_tier="TIER_A"
        )
        self.assertEqual(reg["status"], "LOCAL_REGISTERED")
        
        # 클라우드 전송 페이로드에 PII가 일체 없는지 검증
        cloud_payload = reg["cloud_payload"]
        self.assertNotIn("name", cloud_payload)
        self.assertNotIn("birth_date", cloud_payload)
        self.assertEqual(cloud_payload["uid"], nfc_uid)

        # 클라우드 DID 발급 검증
        did_res = self.custodial_agent.register_custodial_identity(cloud_payload["uid"], cloud_payload["tier"])
        self.assertTrue(did_res["did"].startswith("did:kbtf:resident:"))
        self.assertEqual(did_res["status"], "CUSTODIAL_IDENTITY_CREATED")

    def test_sequence_2_batch_vc_issuance(self):
        """[시퀀스 2] 2주 엑셀 비식별화 및 단기 VC 분기 배치 발급 검증"""
        uid_meal = "04:11:22:33:44:55:01"
        uid_bento = "04:66:77:88:99:00:02"

        raw_excel = [
            {"name": "이영자", "birth_date": "500301", "building_no": "102동", "room_no": "201호", "nfc_uid": uid_meal, "meal_type": "MEAL"},
            {"name": "박철수", "birth_date": "520815", "building_no": "103동", "room_no": "504호", "nfc_uid": uid_bento, "meal_type": "BENTO"}
        ]

        prep = self.batch_preprocessor.process_excel_records(raw_excel)
        self.assertEqual(prep["local_saved_count"], 2)
        self.assertIn(uid_meal, prep["cloud_payload"]["meal_uids"])
        self.assertIn(uid_bento, prep["cloud_payload"]["bento_uids"])

        # 클라우드 배치 발급
        batch_res = self.custodial_agent.process_batch_vc_issuance(prep["cloud_payload"])
        self.assertEqual(batch_res["total_issued"], 2)
        self.assertEqual(batch_res["meal_vc_count"], 1)
        self.assertEqual(batch_res["bento_vc_count"], 1)

        # 발급된 VC 검증
        meal_vcs = self.cloud_db.get_active_vcs(uid_meal)
        self.assertTrue(any("CommunityMealCredential" in vc["type"] for vc in meal_vcs))
        bento_vcs = self.cloud_db.get_active_vcs(uid_bento)
        self.assertTrue(any("WelfareBentoCredential" in vc["type"] for vc in bento_vcs))

    def test_sequence_3_fast_precheck_and_dining_verification(self):
        """[시퀀스 3] 경로식당 0.05초 선확인 및 비동기 Verifier 검증"""
        nfc_uid = "04:MEAL:TEST:01"
        self.custodial_agent.register_custodial_identity(nfc_uid)
        self.custodial_agent.process_batch_vc_issuance({"meal_uids": [nfc_uid], "bento_uids": []})

        # 센서 캐시 동기화
        self.sensor_meal.sync_whitelist_cache({nfc_uid})

        # 태깅 실행
        tag_result = self.sensor_meal.tag_card(nfc_uid)
        
        # 0.05초(50ms) 선확인 기준 검증
        self.assertLess(tag_result["pre_check_latency_ms"], 50.0)
        self.assertTrue(tag_result["fast_pass"])
        self.assertEqual(tag_result["led_indicator"], "GREEN")
        self.assertEqual(tag_result["cloud_response"]["status"], "APPROVED")

    def test_sequence_4_edge_lan_oral_rescue(self):
        """[시퀀스 4] 카드 미지참자 현장 에지 사설망 구두 확인 및 구제 검증"""
        nfc_uid = "04:ORAL:RESCUE:01"
        self.resident_service.register_senior("최순자", "491225", "105동", "703호", nfc_uid)
        self.custodial_agent.register_custodial_identity(nfc_uid)
        self.custodial_agent.process_batch_vc_issuance({"meal_uids": [nfc_uid], "bento_uids": []})

        # 1. 구두 신원 확인
        oral = self.resident_service.verify_oral_identity("105동", "703호", "491225")
        self.assertIsNotNone(oral)
        self.assertEqual(oral["masked_name"], "ㅊㅅㅈ")
        self.assertEqual(oral["nfc_uid"], nfc_uid)

        # 2. 클라우드로 오직 UID만 전송하여 MANUAL_PASS 승인
        rescue_res = self.verifier_service.verify_dining_access("SENSOR_MEAL_01", oral["nfc_uid"], method="MANUAL_PASS")
        self.assertEqual(rescue_res["status"], "APPROVED")
        self.assertEqual(rescue_res["verification_method"], "MANUAL_PASS")

    def test_sequence_5_same_day_duplicate_block(self):
        """[시퀀스 5] 당일 현장식사 완료 후 도시락 중복 수령 실시간 차단 검증"""
        nfc_uid = "04:BUNKER:USER:01"
        self.custodial_agent.register_custodial_identity(nfc_uid)
        self.custodial_agent.process_batch_vc_issuance({
            "meal_uids": [nfc_uid],
            "bento_uids": [nfc_uid]
        })

        # 1. 현장식사 정상 완료
        meal_res = self.verifier_service.verify_dining_access("SENSOR_MEAL_01", nfc_uid)
        self.assertEqual(meal_res["status"], "APPROVED")

        # 2. 같은 날 도시락 라인에서 태깅 시도 -> 즉시 차단 (403)
        bento_tag = self.sensor_bento.tag_card(nfc_uid)
        self.assertEqual(bento_tag["cloud_response"]["status"], "DENIED")
        self.assertEqual(bento_tag["cloud_response"]["code"], 403)
        self.assertEqual(bento_tag["cloud_response"]["reason"], "ALREADY_DINED_TODAY")

    def test_sequence_6_daily_anchoring_and_kpi(self):
        """[시퀀스 6] 일일 18시 온체인 배치 앵커링 및 KPI 집계 검증"""
        nfc_uid = "04:ANCHOR:TEST:01"
        self.custodial_agent.register_custodial_identity(nfc_uid)
        self.custodial_agent.process_batch_vc_issuance({"meal_uids": [nfc_uid], "bento_uids": []})
        self.verifier_service.verify_dining_access("SENSOR_MEAL_01", nfc_uid)

        anchor = self.batch_anchorer.execute_daily_anchoring()
        self.assertEqual(anchor["status"], "ANCHORED_CONFIRMED")
        self.assertGreaterEqual(anchor["total_meals"], 1)
        self.assertTrue(anchor["onchain_tx_hash"].startswith("0x"))

    def test_zero_pii_strict_audit(self):
        """[보안 감사] Zero-PII 감사기가 금지된 개인정보 필드를 올바르게 탐지하고 차단하는지 검증"""
        # 안전한 페이로드 (통과되어야 함)
        safe_payload = {"uid": "04:11:22", "tier": "TIER_A", "sensor_id": "SENSOR_MEAL_01"}
        self.assertTrue(ZeroPIISanitizer.audit_payload(safe_payload))

        # PII 키가 포함된 유출 시도 (즉시 예외 발생해야 함)
        leaky_payload = {"uid": "04:11:22", "resident_name": "홍길동"}
        with self.assertRaises(ZeroPIISanitizationError):
            ZeroPIISanitizer.audit_payload(leaky_payload)

        # 동호수 또는 전화번호 패턴이 포함된 경우 (즉시 차단되어야 함)
        phone_payload = {"uid": "04:11:22", "contact": "010-1234-5678"}
        with self.assertRaises(ZeroPIISanitizationError):
            ZeroPIISanitizer.audit_payload(phone_payload)

if __name__ == "__main__":
    unittest.main()
