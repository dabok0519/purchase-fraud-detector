"""거래처 실재성 검증의 추상 뼈대.

모든 거래처 검증기는 이 인터페이스를 상속해 verify()를 구현한다.
AnomalyDetector(추상)를 detect()로 통일한 것과 같은 Strategy 패턴.
"""
from abc import ABC, abstractmethod


class VendorVerifier(ABC):
    """거래처 검증기 인터페이스.

    반환값은 Vendor.VALID_STATUSES 중 하나:
        "정상" / "폐업" / "휴업" / "검증불가"
    """

    @abstractmethod
    def verify(self, business_number: str) -> str:
        """사업자번호(하이픈 없는 10자리)를 받아 상태 문자열을 반환."""
        ...
