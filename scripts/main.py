"""매입거래 부정·이상 탐지 엔진 — 진입점.

흐름: 설정 읽기 → 거래처 로딩 → 거래 합성 → 엔진 조립 → 실행 → 결과 출력
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from src import config
from src.loader import load_vendors
from src.rules.tolerance import PercentTolerance
from src.checkers.consistency import ConsistencyChecker
from src.detectors.duplicate import DuplicateDetector
from src.detectors.round_amount import RoundAmountDetector
from src.engine import MatchingEngine
from src.result import CheckResult
from src.report import ReportGenerator
from src.verifiers.api import APIVendorVerifier
from scripts.sample_data import build_sample_transactions


def main():
    # 1) 거래처 로딩 (공정위 실데이터)
    vendors = load_vendors(config.VENDORS_CSV)
    print(f"거래처 {len(vendors)}개 로딩 완료 "
          f"(정상 {sum(1 for v in vendors if v.status=='정상')}, "
          f"폐업 {sum(1 for v in vendors if v.status=='폐업')})")

    # 2) 거래 데이터 합성
    pos, grs, invs = build_sample_transactions(vendors)
    print(f"거래 합성: 발주 {len(pos)} / 입고 {len(grs)} / 청구 {len(invs)}\n")

    # 3) 엔진 조립
    checker = ConsistencyChecker(PercentTolerance(config.PRICE_TOLERANCE_PERCENT))
    detectors = [
        RoundAmountDetector(config.ROUND_SUSPICIOUS_AMOUNTS),
        DuplicateDetector(config.DUPLICATE_MAX_DAYS),
    ]
    engine = MatchingEngine(checker, detectors)

    # 4) 거래처 검증기 조립
    load_dotenv()
    api_verifier = APIVendorVerifier(os.getenv("NTS_SERVICE_KEY"))
    vendor_by_code = {v.vendor_code: v for v in vendors}

    # 5) 엔진 실행
    results = engine.run(invs, pos, grs)

    # 6) 거래처 실재성 검증 (국세청 API) — 엔진 판정 후 외부 재검증
    for invoice in invs:
        vendor = vendor_by_code[invoice.vendor_code]
        try:
            status = api_verifier.verify(vendor.business_number)
        except Exception:
            status = "검증불가"

        passed = status == "정상"
        vendor_check = CheckResult(
            check_type="거래처",
            passed=passed,
            reason="" if passed else f"거래처 상태: {status}",
        )
        results[invoice.invoice_number].checks.append(vendor_check)
        if not passed:
            results[invoice.invoice_number].status = "보류"

    # 7) 결과 출력
    print("=" * 55)
    print("판정 결과")
    print("=" * 55)
    normal_count = sum(1 for inv in invs if results[inv.invoice_number].status == "정상")
    hold_count = len(invs) - normal_count

    for invoice in invs:
        mr = results[invoice.invoice_number]
        reasons = ", ".join(mr.reasons) if mr.reasons else "-"
        print(f"  {mr.invoice_number:8s} [{mr.status}]  {reasons}")

    print("\n" + "-" * 55)
    print(f"총 {len(invs)}건  |  정상 {normal_count}  |  보류 {hold_count}")

    # 8) 엑셀 리포트 출력
    report = ReportGenerator(results, invs, vendor_by_code)
    print(f"\n엑셀 리포트 생성: {report.generate()}")
    print(f"원본 데이터 생성: {report.generate_source(pos, grs, invs)}")


if __name__ == "__main__":
    main()
