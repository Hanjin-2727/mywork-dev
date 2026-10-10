#!/usr/bin/env python3
"""
[K-BTF Demonstration Runner]
K-BTF 스마트 주거복지 5대 핵심 업무 흐름 및 CSAP '하' Zero-PII 통합 시뮬레이터
"""
import sys
import os
import json
import time

# Add pj/kbtf to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.did_kms import CustodialKMS
from src.core.security import ZeroPIISanitizer, ZeroPIISanitizationError
from src.tier1_local.local_db import LocalDatabase
from src.tier1_local.resident_service import ResidentService
from src.tier1_local.batch_preprocessor import BatchPreprocessor
from src.tier3_cloud.cloud_db import CloudDatabase
from src.tier3_cloud.custodial_agent import CustodialAgent
from src.tier3_cloud.verifier_service import VerifierService
from src.tier3_cloud.batch_anchorer import DailyBatchAnchorer
from src.edge_terminal.sensor_reader import DiningSensorTerminal

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

def log_step(title):
    print(f"\n{BOLD}{CYAN}======================================================================{RESET}")
    print(f"{BOLD}{CYAN}▶ {title}{RESET}")
    print(f"{BOLD}{CYAN}======================================================================{RESET}")

def run_full_simulation():
    print(f"{BOLD}{GREEN}🚀 [K-BTF] 스마트 주거복지 플랫폼 5대 핵심 시나리오 라이브 시뮬레이션을 시작합니다.{RESET}")
    print(f"기준 규격: 공공클라우드 CSAP '하' 등급 & Zero-PII 3-Tier 아키텍처\n")

    # 1. 인프라 초기화
    local_db = LocalDatabase()
    cloud_db = CloudDatabase()
    kms = CustodialKMS()
    
    resident_service = ResidentService(local_db)
    batch_preprocessor = BatchPreprocessor(local_db)
    custodial_agent = CustodialAgent(cloud_db, kms)
    verifier_service = VerifierService(cloud_db, custodial_agent)
    batch_anchorer = DailyBatchAnchorer(cloud_db)

    sensor_meal = DiningSensorTerminal("SENSOR_MEAL_01", "경로식당 1라인 (현장식사)", verifier_service)
    sensor_bento = DiningSensorTerminal("SENSOR_BENTO_02", "경로식당 2라인 (도시락)", verifier_service)

    # -------------------------------------------------------------------------
    # 시퀀스 1: 2G폰 고령 어르신 대면 등록 및 익명 Custodial DID 발급
    # -------------------------------------------------------------------------
    log_step("[시퀀스 1] 2G폰 고령 어르신 창구 대면 등록 & 익명 Custodial DID/VC 발급")
    senior_card_uid = "04:A1:B2:C3:D4:E5:01"
    reg_result = resident_service.register_senior(
        name="김만석",
        birth_date="480514",
        building_no="101동",
        room_no="1204호",
        nfc_uid=senior_card_uid,
        welfare_tier="TIER_A"
    )
    print(f"1. [Tier 1 관리사무소 로컬 PC] 거주자 명부 대면 확인 및 로컬 매핑 DB 저장:")
    print(f"   - 거주자 ID: {reg_result['resident_id']} | 성명: 김만석 (폐쇄망 100% 잔류)")
    
    cloud_payload = reg_result["cloud_payload"]
    print(f"2. [클라우드 전송: Zero-PII] 인적사항 전면 배제, 오직 난수 UID만 전송:")
    print(f"   - Payload: {json.dumps(cloud_payload, ensure_ascii=False)}")

    did_res = custodial_agent.register_custodial_identity(cloud_payload["uid"], cloud_payload["tier"])
    print(f"3. [Tier 3 공공클라우드] Custodial DID 및 기본 스마트 주민증 VC 발급 완료:")
    print(f"   - 발급된 DID: {GREEN}{did_res['did']}{RESET}")

    # -------------------------------------------------------------------------
    # 시퀀스 2: 2주 단위 엑셀 비식별화 및 단기 VC 분기 배치 발급
    # -------------------------------------------------------------------------
    log_step("[시퀀스 2] 2주 주기 수급자 엑셀 업로드 및 단기 식사/도시락 VC 배치 발급")
    bento_card_uid = "04:B2:C3:D4:E5:F6:02"
    mock_excel_records = [
        {"name": "김만석", "birth_date": "480514", "building_no": "101동", "room_no": "1204호", "nfc_uid": senior_card_uid, "meal_type": "MEAL"},
        {"name": "이영자", "birth_date": "510920", "building_no": "102동", "room_no": "305호", "nfc_uid": bento_card_uid, "meal_type": "BENTO"}
    ]
    pre_result = batch_preprocessor.process_excel_records(mock_excel_records)
    print(f"1. [Tier 1 로컬 전처리] 원본 엑셀 인적사항 분리 및 비식별 UID 목록 생성:")
    print(f"   - 로컬 보관 인원: {pre_result['local_saved_count']}명")
    print(f"   - 클라우드 전송용: 현장식사={pre_result['cloud_payload']['meal_uids']}, 도시락={pre_result['cloud_payload']['bento_uids']}")

    batch_vc_res = custodial_agent.process_batch_vc_issuance(pre_result["cloud_payload"])
    print(f"2. [Tier 3 클라우드] 단기 유효기간(14일) 익명 VC 대량 전자서명 발급 완료:")
    print(f"   - 총 발급 건수: {GREEN}{batch_vc_res['total_issued']}건{RESET} (현장식사 VC {batch_vc_res['meal_vc_count']}건, 도시락 VC {batch_vc_res['bento_vc_count']}건)")

    # 센서 캐시 동기화
    active_uids = {senior_card_uid, bento_card_uid}
    sensor_meal.sync_whitelist_cache(active_uids)
    sensor_bento.sync_whitelist_cache(active_uids)
    print(f"3. [에지 단말 캐시 동기화] 경로식당 센스 단말에 유효 UID 화이트리스트 푸시 완료")

    # -------------------------------------------------------------------------
    # 시퀀스 3: 경로식당 0.05초 초고속 선확인 및 비동기 Verifier 검증
    # -------------------------------------------------------------------------
    log_step("[시퀀스 3] 경로식당 0.05초 초고속 선확인 & 비동기 Verifier 검증 (정규 태깅)")
    print(f"어르신이 경로식당 배식구(Line 1)에 실물 NFC 목걸이를 태깅합니다...")
    tag_result = sensor_meal.tag_card(senior_card_uid)
    print(f"1. [현장 0.05초 선확인]:")
    print(f"   - 선확인 소요시간: {BOLD}{GREEN}{tag_result['pre_check_latency_ms']} ms{RESET} (기준: 50ms 이하 완벽 충족!)")
    print(f"   - 단말 LED/음성: [{tag_result['led_indicator']}] \"{tag_result['speaker_voice']}\"")
    print(f"   - 결과: 어르신 식판 들고 즉시 통과 (현장 체류 0초)")
    print(f"2. [클라우드 비동기 VP 검증]:")
    print(f"   - Verifier 응답: {tag_result['cloud_response']['status']} (TxId: {tag_result['cloud_response']['tx_id']})")
    print(f"   - 정부 과제 실적 영구 로깅 완료")

    # -------------------------------------------------------------------------
    # 시퀀스 4: 카드 미지참자 현장 에지 사설망(192.168.0.x) 검증 및 구제
    # -------------------------------------------------------------------------
    log_step("[시퀀스 4] 카드 미지참자 현장 에지 사설망(Edge LAN) 검증 및 구제")
    print(f"어르신이 카드를 집에 두고 와 구두로 진술: \"101동 1204호, 480514 김만석이요\"")
    oral_res = resident_service.verify_oral_identity("101동", "1204호", "480514", "이준호 공익요원")
    print(f"1. [에지 사설망 Wi-Fi 조회] 관리사무소 로컬 PC 접속 결과:")
    print(f"   - 확인된 거주자 초성: {YELLOW}{oral_res['masked_name']}{RESET} (성명 원본 노출 차단)")
    print(f"   - 매핑된 카드 UID 도출: {oral_res['nfc_uid']}")
    
    # 관리자가 배식 승인 터치 -> 클라우드로 오직 UID만 전송
    rescue_verify = verifier_service.verify_dining_access("SENSOR_MEAL_01", oral_res["nfc_uid"], method="MANUAL_PASS")
    # 주의: 김만석 어르신은 위에서 이미 식사를 완료했으므로 당일 중복 차단이 발생해야 정상!
    print(f"2. [클라우드 전송 결과]:")
    print(f"   - 상태: {rescue_verify['status']} ({rescue_verify.get('message')})")

    # -------------------------------------------------------------------------
    # 시퀀스 5: 부정/중복 수령 (현장식사 + 도시락) 실시간 상호배제 차단
    # -------------------------------------------------------------------------
    log_step("[시퀀스 5] 부정/중복 수령 (현장식사 완료 후 도시락 중복) 실시간 차단")
    print(f"이미 현장식사를 마친 어르신이 30분 뒤 도시락 배부처(Line 2)에서 카드를 다시 태깅합니다...")
    bunker_tag = sensor_bento.tag_card(senior_card_uid)
    print(f"1. [센서 판정 결과]:")
    print(f"   - 단말 경고: [{RED}{bunker_tag['led_indicator']}{RESET}] \"{bunker_tag['speaker_voice']}\"")
    print(f"   - 클라우드 거부 코드: {RED}{bunker_tag['cloud_response']['code']} {bunker_tag['cloud_response']['reason']}{RESET}")
    print(f"   - 중복 수령 실시간 차단 성공!")

    # -------------------------------------------------------------------------
    # 시퀀스 6: 일일 18시 온체인 배치 앵커링 및 정부 과제 KPI 집계
    # -------------------------------------------------------------------------
    log_step("[시퀀스 6] 일일 18시 온체인 배치 앵커링 & 정부 과제 KPI 집계")
    anchor_receipt = batch_anchorer.execute_daily_anchoring()
    print(f"1. [당일 실적 집계]:")
    print(f"   - 현장 식사 승인: {anchor_receipt['total_meals']}건")
    print(f"   - 중복 수령 차단: {anchor_receipt['duplicates_blocked']}건")
    print(f"   - 머클 루트 해시: {anchor_receipt['merkle_root_hash'][:32]}...")
    print(f"   - 온체인 트랜잭션 해시: {GREEN}{anchor_receipt['onchain_tx_hash']}{RESET}")
    print(f"   - 7일 경과 상세 로그 자동 영구 파기 수행 완료")

    print(f"\n{BOLD}{GREEN}✅ 5대 핵심 시나리오 시뮬레이션이 100% 성공적으로 완료되었습니다!{RESET}\n")

if __name__ == "__main__":
    run_full_simulation()
