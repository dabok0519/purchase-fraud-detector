from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class CheckResult:
    """검사 한 건의 결과. Checker나 Detector가 검사할 때마다 하나씩 만든다."""
    check_type: str         # "단가" / "수량" / "입고" / "중복" / "라운드" / "거래처"
    passed: bool            # True=정상, False=적발
    reason: str = ""        # 적발 사유 (통과면 빈 문자열)
    expected: Decimal = Decimal('0')
    actual: Decimal = Decimal('0')
    invoice_number: str = ""   # 탐지기가 채움


@dataclass
class MatchResult:
    """청구(Invoice) 한 건에 대한 최종 판정."""
    invoice_number: str
    status: str = "정상"
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def reasons(self) -> list[str]:
        """적발된 검사들의 사유만 모아서 반환."""
        return [c.reason for c in self.checks if not c.passed]
