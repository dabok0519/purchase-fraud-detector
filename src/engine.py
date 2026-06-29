"""3축 검증을 지휘하는 핵심 엔진.

3축 = (1) 거래 정합성  (2) 부정 패턴 탐지  (3) 거래처 실재성 검증
"""
from decimal import Decimal
from src.result import CheckResult, MatchResult


class MatchingEngine:

    def __init__(self, consistency_checker, detectors):
        """
        consistency_checker: ConsistencyChecker
        detectors: AnomalyDetector 리스트
        """
        self.checker = consistency_checker
        self.detectors = detectors

    def _empty_row(self) -> dict:
        return {
            "po_qty": Decimal('0'), "po_price": None,
            "gr_qty": Decimal('0'),
            "inv_qty": Decimal('0'), "inv_price": None,
        }

    def aggregate(self, invoice, purchase_orders, goods_receipts) -> dict:
        """청구 1건 기준으로 자재별 PO·GR·Invoice 수량/단가를 합산한다."""
        agg = {}

        # 1) 이 청구가 가리키는 PO만 추출 (1:N 지원)
        related_pos = [po for po in purchase_orders if po.po_number in invoice.po_numbers]

        # 2) PO 라인 합산
        for po in related_pos:
            for item in po.items:
                if item.material_code not in agg:
                    agg[item.material_code] = self._empty_row()
                agg[item.material_code]["po_qty"] += item.quantity
                agg[item.material_code]["po_price"] = item.unit_price

        # 3) GR 라인 합산
        related_po_numbers = {po.po_number for po in related_pos}
        for gr in goods_receipts:
            if gr.po_number in related_po_numbers:
                for item in gr.items:
                    if item.material_code not in agg:
                        agg[item.material_code] = self._empty_row()
                    agg[item.material_code]["gr_qty"] += item.quantity

        # 4) Invoice 라인 합산
        for item in invoice.items:
            if item.material_code not in agg:
                agg[item.material_code] = self._empty_row()
            agg[item.material_code]["inv_qty"] += item.quantity
            agg[item.material_code]["inv_price"] = item.unit_price

        return agg

    def check_invoice(self, invoice, purchase_orders, goods_receipts) -> list:
        """청구 1건의 정합성(단가·수량·입고유무)을 검사해 CheckResult 리스트 반환."""
        agg = self.aggregate(invoice, purchase_orders, goods_receipts)
        checks = []

        for material, row in agg.items():
            # (1) 입고기록 없음
            if row["inv_qty"] > 0 and row["gr_qty"] == 0:
                checks.append(CheckResult(
                    check_type="입고",
                    passed=False,
                    reason="입고기록 없음",
                    expected=Decimal('0'),
                    actual=row["inv_qty"],
                ))
                continue

            # (2) 단가 검사
            if row["po_price"] is not None and row["inv_price"] is not None:
                checks.append(self.checker.check_price_values(row["po_price"], row["inv_price"]))

            # (3) 수량 검사
            checks.append(self.checker.check_quantity_values(row["gr_qty"], row["inv_qty"]))

        return checks

    def run(self, invoices, purchase_orders, goods_receipts) -> dict:
        """전체 청구를 판정해 invoice_number → MatchResult 딕셔너리로 반환."""
        results = {}

        # 1) 정합성 검사
        for invoice in invoices:
            checks = self.check_invoice(invoice, purchase_orders, goods_receipts)
            results[invoice.invoice_number] = MatchResult(
                invoice_number=invoice.invoice_number,
                checks=checks,
            )

        # 2) 부정 패턴 탐지
        for detector in self.detectors:
            for cr in detector.detect(invoices):
                if cr.invoice_number in results:
                    results[cr.invoice_number].checks.append(cr)

        # 3) 최종 status 확정: 하나라도 적발이면 보류
        for mr in results.values():
            if any(not c.passed for c in mr.checks):
                mr.status = "보류"

        return results
