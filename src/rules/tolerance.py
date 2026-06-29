from abc import ABC, abstractmethod
from decimal import Decimal


class ToleranceRule(ABC):
    """허용오차 판정 인터페이스 (Strategy 패턴).

    검증기는 이 룰에게 is_within(기준값, 실제값)만 물어본다.
    단가든 금액이든 동일한 인터페이스로 교체 가능.
    """

    @abstractmethod
    def is_within(self, expected: Decimal, actual: Decimal) -> bool:
        ...


class PercentTolerance(ToleranceRule):
    """퍼센트 기준 허용. 예: 3% → PercentTolerance(Decimal('3'))"""

    def __init__(self, percent: Decimal):
        self.percent = percent

    def is_within(self, expected: Decimal, actual: Decimal) -> bool:
        if expected == 0:
            return actual == 0
        diff = abs(actual - expected)
        limit = abs(expected) * self.percent / Decimal('100')
        return diff <= limit


class AbsoluteTolerance(ToleranceRule):
    """절대값 기준 허용. 예: 100원 → AbsoluteTolerance(Decimal('100'))"""

    def __init__(self, amount: Decimal):
        self.amount = amount

    def is_within(self, expected: Decimal, actual: Decimal) -> bool:
        return abs(actual - expected) <= self.amount
