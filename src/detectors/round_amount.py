from decimal import Decimal
from src.detectors.base import AnomalyDetector
from src.result import CheckResult


class RoundAmountDetector(AnomalyDetector):
    """라운드 금액 탐지.

    정상 거래는 단가×수량이라 금액이 지저분하지만(예: 16,211원),
    결재 한도를 피하려는 조작이면 깔끔한 숫자가 나온다(예: 정확히 5,000,000원).
    의심 금액 목록은 config.py에서 주입받는다.
    """

    def __init__(self, suspicious_amounts: list):
        self.suspicious_amounts = suspicious_amounts

    def detect(self, invoices) -> list:
        results = []
        for invoice in invoices:
            total = invoice.total_amount
            if total in self.suspicious_amounts:
                results.append(CheckResult(
                    check_type="라운드",
                    passed=False,
                    reason="라운드 금액(한도 회피 의심)",
                    expected=Decimal('0'),
                    actual=total,
                    invoice_number=invoice.invoice_number,
                ))
        return results
