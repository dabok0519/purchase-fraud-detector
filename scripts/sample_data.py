"""합성 거래 데이터 생성 (9케이스).

거래처는 실데이터(vendors.csv)지만, 주문·입고·청구는
기업 내부 데이터라 공개되지 않으므로 실무 시나리오대로 합성한다.
"""
from decimal import Decimal
from datetime import date
from src.models import PurchaseOrder, POItem, GoodsReceipt, GRItem, Invoice, InvoiceItem


def build_sample_transactions(vendors):
    """거래처 리스트를 받아 거래(PO/GR/Invoice)를 생성해 반환.

    반환: (purchase_orders, goods_receipts, invoices)
    """
    normal_vendors = [v for v in vendors if v.status == "정상"]
    closed_vendors = [v for v in vendors if v.status == "폐업"]

    pos, grs, invs = [], [], []

    def add(no, vendor, po_items, gr_items, inv_items, inv_date=date(2025, 6, 10)):
        pos.append(PurchaseOrder(
            f"PO-{no}", vendor.vendor_code, date(2025, 6, 1),
            items=[POItem(m, Decimal(str(q)), Decimal(str(p))) for m, q, p in po_items]
        ))
        if gr_items is not None:
            grs.append(GoodsReceipt(
                f"GR-{no}", f"PO-{no}", date(2025, 6, 3),
                items=[GRItem(m, Decimal(str(q))) for m, q in gr_items]
            ))
        invs.append(Invoice(
            f"INV-{no}", vendor.vendor_code, inv_date,
            po_numbers=[f"PO-{no}"],
            items=[InvoiceItem(m, Decimal(str(q)), Decimal(str(p))) for m, q, p in inv_items]
        ))

    nv = lambda i: normal_vendors[i % len(normal_vendors)]
    cv = lambda i: closed_vendors[i % len(closed_vendors)]

    # 케이스1: 다 일치 → 정상
    add(1, nv(0), [("M1", 10, 1000)], [("M1", 10)], [("M1", 10, 1000)])
    # 케이스2: 단가 5%↑ (허용 3%) → 단가차이
    add(2, nv(1), [("M1", 10, 1100)], [("M1", 10)], [("M1", 10, 1155)])
    # 케이스3: 청구수량 > 입고수량 → 수량초과
    add(3, nv(2), [("M1", 10, 1200)], [("M1", 10)], [("M1", 12, 1200)])
    # 케이스4: 부분입고 후 전량청구 → 수량초과
    add(4, nv(3), [("M1", 10, 1300)], [("M1", 7)], [("M1", 10, 1300)])
    # 케이스5: 입고기록 없음
    add(5, nv(4), [("M1", 10, 1400)], None, [("M1", 10, 1400)])
    # 케이스6: 단가 1% (허용 3%) → 정상
    add(6, nv(5), [("M1", 10, 1500)], [("M1", 10)], [("M1", 10, 1515)])
    # 케이스7: 정확히 500만 → 라운드 금액
    add(7, nv(6), [("M1", 1, 5000000)], [("M1", 1)], [("M1", 1, 5000000)])
    # 케이스8: 같은 거래처·금액·근접일자 2건 → 중복 청구
    dup_vendor = nv(7)
    add("8a", dup_vendor, [("M1", 1, 3000)], [("M1", 1)], [("M1", 1, 3000)], date(2025, 6, 10))
    add("8b", dup_vendor, [("M1", 1, 3000)], [("M1", 1)], [("M1", 1, 3000)], date(2025, 6, 12))
    # 케이스9: 정합성 정상이지만 거래처 폐업 → 거래처 검증 축에서 적발
    add(9, cv(0), [("M1", 10, 2000)], [("M1", 10)], [("M1", 10, 2000)])

    return pos, grs, invs
