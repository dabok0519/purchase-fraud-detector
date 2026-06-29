from src.result import CheckResult


class ConsistencyChecker:
    """3-Way Match 정합성 검사 (단가·수량).

    - 단가: PO(발주 약속) vs Invoice(청구) — PercentTolerance 또는 AbsoluteTolerance 적용
    - 수량: GR(입고) vs Invoice(청구) — 허용오차 없음, 초과 시 즉시 적발
    """

    def __init__(self, price_rule):
        self.price_rule = price_rule

    def check_price_values(self, po_price, invoice_price) -> CheckResult:
        """발주단가(기준) vs 청구단가(실제) 비교."""
        passed = self.price_rule.is_within(po_price, invoice_price)
        return CheckResult(
            check_type="단가",
            passed=passed,
            reason="" if passed else "단가차이",
            expected=po_price,
            actual=invoice_price,
        )

    def check_quantity_values(self, gr_qty, invoice_qty) -> CheckResult:
        """입고량(기준) vs 청구량(실제) 비교. 청구량이 입고량을 초과하면 적발."""
        passed = invoice_qty <= gr_qty
        return CheckResult(
            check_type="수량",
            passed=passed,
            reason="" if passed else "수량초과",
            expected=gr_qty,
            actual=invoice_qty,
        )
