from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal


@dataclass
class Material:
    """자재 마스터. 품목 기본 정보를 담는 그릇."""
    material_code: str
    name: str


@dataclass
class Vendor:
    """거래처 마스터."""
    vendor_code: str
    business_number: str
    name: str
    status: str = "미확인"

    VALID_STATUSES = ["정상", "폐업", "휴업", "검증불가", "미확인"]

    def __post_init__(self):
        if self.status not in self.VALID_STATUSES:
            raise ValueError(f"잘못된 status 값: {self.status}")


@dataclass
class POItem:
    """발주서 내의 개별 라인 아이템."""
    material_code: str
    quantity: Decimal
    unit_price: Decimal

    @property
    def amount(self) -> Decimal:
        return self.quantity * self.unit_price


@dataclass
class PurchaseOrder:
    """발주 헤더 + 라인 모델."""
    po_number: str
    vendor_code: str
    order_date: date
    items: list[POItem] = field(default_factory=list)


@dataclass
class GRItem:
    """입고 라인. 실제 입고 수량을 기록."""
    material_code: str
    quantity: Decimal


@dataclass
class GoodsReceipt:
    """입고 헤더 + 라인 모델."""
    gr_number: str
    po_number: str
    receipt_date: date
    items: list[GRItem] = field(default_factory=list)


@dataclass
class InvoiceItem:
    """청구 라인. 실제 청구 수량과 단가를 기록."""
    material_code: str
    quantity: Decimal
    unit_price: Decimal

    @property
    def amount(self) -> Decimal:
        return self.quantity * self.unit_price


@dataclass
class Invoice:
    """청구 헤더 + 라인 모델. 청구 1건이 PO 여러 건을 묶을 수 있다(1:N)."""
    invoice_number: str
    vendor_code: str
    invoice_date: date
    po_numbers: list[str] = field(default_factory=list)
    items: list[InvoiceItem] = field(default_factory=list)

    @property
    def total_amount(self) -> Decimal:
        return sum(item.amount for item in self.items)
