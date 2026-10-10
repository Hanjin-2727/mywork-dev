"""
[Core Security] K-BTF Zero-PII 감사 및 암호화 유틸리티 모듈
CSAP '하' 등급 준수를 위한 클라우드 전송 데이터 사전 검증기
"""
import hashlib
import hmac
import json
import re
from typing import Dict, Any, List

# 법적 개인식별정보(PII) 금지 키워드 블랙리스트
PII_KEY_BLACKLIST = {
    "name", "resident_name", "user_name", "full_name", "real_name",
    "ssn", "rrn", "birth_date", "birthdate", "birthday", "birth",
    "phone", "phone_number", "mobile", "tel",
    "address", "building_no", "room_no", "dong", "ho", "detail_address",
    "email", "resident_id", "resident_ssn"
}

# 한국어 주민등록번호, 생년월일, 전화번호 패턴 정규식
PII_PATTERNS = [
    re.compile(r"\b\d{6}-[1-4]\d{6}\b"),     # 주민등록번호 (YYMMDD-GXXXXXX)
    re.compile(r"\b01[016789]-\d{3,4}-\d{4}\b"), # 휴대전화번호
    re.compile(r"\b\d{2,3}동\s*\d{3,4}호\b")   # 아파트 동호수 패턴
]

class ZeroPIISanitizationError(Exception):
    """클라우드 또는 외부 전송 데이터에 개인정보(PII)가 감지되었을 때 발생하는 보안 예외"""
    pass

class ZeroPIISanitizer:
    @staticmethod
    def audit_payload(payload: Dict[str, Any]) -> bool:
        """
        클라우드로 전송되는 딕셔너리 페이로드에 PII 키나 문자열 패턴이 존재하는지 전수 검사.
        위반 시 ZeroPIISanitizationError 발생.
        """
        def _recursive_check(data: Any, path: str = ""):
            if isinstance(data, dict):
                for k, v in data.items():
                    key_lower = k.lower().strip()
                    if key_lower in PII_KEY_BLACKLIST:
                        raise ZeroPIISanitizationError(
                            f"[보안 위반] 클라우드 전송 금지 PII 키워드 감지: '{k}' at path '{path}'"
                        )
                    _recursive_check(v, f"{path}.{k}" if path else k)
            elif isinstance(data, list):
                for idx, item in enumerate(data):
                    _recursive_check(item, f"{path}[{idx}]")
            elif isinstance(data, str):
                for pattern in PII_PATTERNS:
                    if pattern.search(data):
                        raise ZeroPIISanitizationError(
                            f"[보안 위반] 클라우드 전송 금지 개인정보 패턴 감지: '{data}' at path '{path}'"
                        )

        _recursive_check(payload)
        return True

    @staticmethod
    def sha256(data: str) -> str:
        """SHA-256 해시 헬퍼"""
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    @staticmethod
    def hmac_sha256(key: str, message: str) -> str:
        """HMAC-SHA256 암호학적 서명 생성 헬퍼"""
        return hmac.new(key.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).hexdigest()
