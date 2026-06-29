"""국세청 사업자등록 상태조회 API 기반 거래처 검증기.

API 키는 생성자로 주입받는다 (.env 분리 원칙).
API 호출 실패 시 '검증불가'로 폴백하여 코어가 죽지 않게 한다.
"""
import requests
from src.verifiers.base import VendorVerifier


class APIVendorVerifier(VendorVerifier):
    """국세청 공공 API로 사업자 상태를 조회하는 검증기."""

    URL = "https://api.odcloud.kr/api/nts-businessman/v1/status"

    # 국세청 API 상태 문자열 → 내부 표기 매핑
    STATUS_MAP = {
        "계속사업자": "정상",
        "휴업자": "휴업",
        "폐업자": "폐업",
    }

    def __init__(self, service_key: str, timeout: int = 5):
        self.service_key = service_key
        self.timeout = timeout

    def verify(self, business_number: str) -> str:
        """사업자번호 1건을 조회해 상태 문자열을 반환."""
        try:
            res = requests.post(
                self.URL,
                params={"serviceKey": self.service_key},
                json={"b_no": [business_number]},
                headers={"Content-Type": "application/json"},
                timeout=self.timeout,
            )
            if res.status_code != 200:
                return "검증불가"
            items = res.json().get("data", [])
            if not items:
                return "검증불가"
            return self.STATUS_MAP.get(items[0]["b_stt"], "검증불가")
        except Exception:
            return "검증불가"
