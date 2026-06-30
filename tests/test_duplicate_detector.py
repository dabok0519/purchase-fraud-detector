"""중복 청구 탐지기(DuplicateDetector) 단위 테스트.

같은 거래처 + 같은 금액 + 근접 일자(7일 이내) 조건을 각각 검증한다.
"""
from decimal import Decimal
from datetime import date
import pytest
from src.detectors.duplicate import DuplicateDetector
from src.models import Invoice, InvoiceItem


def make_invoice(number: str, vendor: str, amount: str, inv_date: date) -> Invoice:
    """테스트용 단일 라인 Invoice 생성 헬퍼."""
    item = InvoiceItem(
        material_code="MAT-001",
        quantity=Decimal("1"),
        unit_price=Decimal(amount),
    )
    inv = Invoice(
        invoice_number=number,
        vendor_code=vendor,
        invoice_date=inv_date,
        po_numbers=["PO-001"],
        items=[item],
    )
    return inv


class TestDuplicateDetector:
    def setup_method(self):
        self.detector = DuplicateDetector(max_days=7)

    def test_duplicate_detected(self):
        """같은 거래처 · 같은 금액 · 3일 차이 → 중복 탐지, 두 청구 모두 보류."""
        inv_a = make_invoice("INV-001", "V001", "500000", date(2026, 6, 1))
        inv_b = make_invoice("INV-002", "V001", "500000", date(2026, 6, 4))
        results = self.detector.detect([inv_a, inv_b])
        assert len(results) == 2
        assert all(r.passed is False for r in results)
        assert all(r.check_type == "중복" for r in results)

    def test_different_vendor_not_detected(self):
        """거래처 다르면 금액·일자 같아도 탐지 안 됨."""
        inv_a = make_invoice("INV-001", "V001", "500000", date(2026, 6, 1))
        inv_b = make_invoice("INV-002", "V002", "500000", date(2026, 6, 1))
        results = self.detector.detect([inv_a, inv_b])
        assert results == []

    def test_different_amount_not_detected(self):
        """금액 다르면 탐지 안 됨."""
        inv_a = make_invoice("INV-001", "V001", "500000", date(2026, 6, 1))
        inv_b = make_invoice("INV-002", "V001", "600000", date(2026, 6, 1))
        results = self.detector.detect([inv_a, inv_b])
        assert results == []

    def test_outside_day_window_not_detected(self):
        """8일 차이 → max_days=7 초과, 탐지 안 됨."""
        inv_a = make_invoice("INV-001", "V001", "500000", date(2026, 6, 1))
        inv_b = make_invoice("INV-002", "V001", "500000", date(2026, 6, 9))
        results = self.detector.detect([inv_a, inv_b])
        assert results == []

    def test_boundary_day_detected(self):
        """정확히 7일 차이 → 경계값, 탐지됨."""
        inv_a = make_invoice("INV-001", "V001", "500000", date(2026, 6, 1))
        inv_b = make_invoice("INV-002", "V001", "500000", date(2026, 6, 8))
        results = self.detector.detect([inv_a, inv_b])
        assert len(results) == 2

    def test_single_invoice_no_result(self):
        """청구 1건만 있으면 비교 대상 없어 결과 없음."""
        inv_a = make_invoice("INV-001", "V001", "500000", date(2026, 6, 1))
        results = self.detector.detect([inv_a])
        assert results == []
