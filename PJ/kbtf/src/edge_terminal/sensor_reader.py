"""
[Edge Terminal] 경로식당 센스 단말 에뮬레이터 모듈
0.05초(50ms) 초고속 로컬 선확인 및 비동기 클라우드 전송 지원
"""
import time
from typing import Dict, Any, Set, Optional

class DiningSensorTerminal:
    def __init__(self, sensor_id: str, location_name: str, verifier_service=None):
        self.sensor_id = sensor_id
        self.location_name = location_name
        self.verifier_service = verifier_service
        self.cached_whitelist_uids: Set[str] = set()
        self.last_sync_time = None

    def sync_whitelist_cache(self, active_uids: Set[str]):
        """클라우드 또는 로컬 사설망으로부터 최신 유효 UID 화이트리스트 캐시 동기화"""
        self.cached_whitelist_uids = set(active_uids)
        self.last_sync_time = time.time()

    def tag_card(self, nfc_uid: str) -> Dict[str, Any]:
        """
        [시퀀스 3] 경로식당 원터치 태깅 실행
        1단계: 단말 로컬 0.05초 초고속 선확인 (대기열 병목 원천 차단)
        2단계: 비동기 클라우드 Zero-PII 전송 및 실적 앵커링
        """
        start_time = time.perf_counter()

        # 1단계: 0.05초 초고속 선확인 (메모리 캐시 조회)
        is_cached_valid = nfc_uid in self.cached_whitelist_uids
        pre_check_elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        if is_cached_valid:
            led_status = "GREEN"
            voice_output = "띵동! 반갑습니다. 맛있게 드세요."
            fast_pass = True
        else:
            led_status = "YELLOW"
            voice_output = "카드를 확인 중입니다. 잠시만 기다려주세요."
            fast_pass = False

        # 2단계: 클라우드로 비동기 전송
        cloud_result = None
        if self.verifier_service:
            cloud_result = self.verifier_service.verify_dining_access(
                sensor_id=self.sensor_id,
                nfc_uid=nfc_uid,
                method="NFC_TAG"
            )
            # 만약 당일 중복 차단 등이 발생한 경우 LED 상태 업데이트
            if cloud_result.get("status") == "DENIED":
                led_status = "YELLOW"
                voice_output = cloud_result.get("message", "승인 거부되었습니다.")
                fast_pass = False

        total_elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return {
            "sensor_id": self.sensor_id,
            "nfc_uid": nfc_uid,
            "pre_check_latency_ms": round(pre_check_elapsed_ms, 2),
            "total_latency_ms": round(total_elapsed_ms, 2),
            "fast_pass": fast_pass,
            "led_indicator": led_status,
            "speaker_voice": voice_output,
            "cloud_response": cloud_result
        }
