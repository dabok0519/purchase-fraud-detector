from decimal import Decimal
from src.detectors.base import AnomalyDetector
from src.result import CheckResult


class DuplicateDetector(AnomalyDetector):
    """중복 청구 탐지.

    아래 세 조건이 모두 맞으면 중복으로 간주:
      1. 같은 거래처 (vendor_code 일치)
      2. 같은 총액 (total_amount 일치)
      3. 근접한 일자 (두 청구 날짜 차이가 max_days 이내)

    중복은 두 청구 모두 보류가 되어야 하므로 a·b 각각 CheckResult를 생성한다.
    """

    def __init__(self, max_days: int):
        self.max_days = max_days

    def detect(self, invoices) -> list:
        results = []
        for i in range(len(invoices)):
            for j in range(i + 1, len(invoices)):
                a, b = invoices[i], invoices[j]
                same_vendor = a.vendor_code == b.vendor_code
                same_amount = a.total_amount == b.total_amount
                day_gap = abs((a.invoice_date - b.invoice_date).days)
                if same_vendor and same_amount and day_gap <= self.max_days:
                    reason = f"중복 청구 의심: {a.invoice_number}와 {b.invoice_number}"
                    for num in (a.invoice_number, b.invoice_number):
                        results.append(CheckResult(
                            check_type="중복",
                            passed=False,
                            reason=reason,
                            expected=Decimal('0'),
                            actual=b.total_amount,
                            invoice_number=num,
                        ))
        return results
