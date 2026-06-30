"""허용오차 Strategy 단위 테스트.

PercentTolerance · AbsoluteTolerance 두 구현체 모두,
경계값(허용 한계 정확히 일치), 초과, expected==0 엣지케이스를 검증한다.
"""
from decimal import Decimal
import pytest
from src.rules.tolerance import PercentTolerance, AbsoluteTolerance


class TestPercentTolerance:
    def setup_method(self):
        # 3% 허용
        self.rule = PercentTolerance(Decimal("3"))

    def test_exact_match_passes(self):
        """기준값과 동일 → 통과."""
        assert self.rule.is_within(Decimal("1000"), Decimal("1000")) is True

    def test_within_tolerance_passes(self):
        """3% 이내 → 통과. 1000 기준 최대 허용 1030."""
        assert self.rule.is_within(Decimal("1000"), Decimal("1030")) is True

    def test_boundary_passes(self):
        """정확히 경계값(3%) → 통과."""
        assert self.rule.is_within(Decimal("1000"), Decimal("1030")) is True

    def test_exceeds_tolerance_fails(self):
        """3% 초과 → 실패. 1031은 한계 초과."""
        assert self.rule.is_within(Decimal("1000"), Decimal("1031")) is False

    def test_expected_zero_actual_zero_passes(self):
        """expected == 0 이고 actual == 0 → 통과 (ZeroDivision 방어)."""
        assert self.rule.is_within(Decimal("0"), Decimal("0")) is True

    def test_expected_zero_actual_nonzero_fails(self):
        """expected == 0 이고 actual != 0 → 실패."""
        assert self.rule.is_within(Decimal("0"), Decimal("1")) is False

    def test_lower_than_expected_passes(self):
        """기준보다 낮아도 3% 이내면 통과. 970은 -3%."""
        assert self.rule.is_within(Decimal("1000"), Decimal("970")) is True

    def test_lower_than_expected_fails(self):
        """기준보다 낮고 3% 초과 → 실패."""
        assert self.rule.is_within(Decimal("1000"), Decimal("969")) is False


class TestAbsoluteTolerance:
    def setup_method(self):
        # 100원 허용
        self.rule = AbsoluteTolerance(Decimal("100"))

    def test_exact_match_passes(self):
        assert self.rule.is_within(Decimal("5000"), Decimal("5000")) is True

    def test_within_tolerance_passes(self):
        assert self.rule.is_within(Decimal("5000"), Decimal("5100")) is True

    def test_boundary_passes(self):
        """정확히 100원 차이 → 통과."""
        assert self.rule.is_within(Decimal("5000"), Decimal("5100")) is True

    def test_exceeds_tolerance_fails(self):
        """101원 차이 → 실패."""
        assert self.rule.is_within(Decimal("5000"), Decimal("5101")) is False

    def test_negative_direction_passes(self):
        assert self.rule.is_within(Decimal("5000"), Decimal("4900")) is True

    def test_negative_direction_fails(self):
        assert self.rule.is_within(Decimal("5000"), Decimal("4899")) is False
