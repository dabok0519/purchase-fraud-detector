"""데이터 입력 계층: CSV를 읽어 도메인 객체로 변환한다."""
import csv
import src.config as config
from src.models import Vendor


def load_vendors(csv_path):
    """공정위 거래처 CSV를 읽어 Vendor 객체 리스트로 반환.

    CSV 컬럼: 상호 / 사업자등록번호 / 업소상태
    - 인코딩은 UTF-8-sig (한글 CSV의 BOM 처리)
    - vendor_code는 행 순서로 자동 생성 (V001, V002, ...)
    """
    vendors = []
    with open(csv_path, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            status = config.VENDOR_STATUS_MAP.get(row['업소상태'], "미확인")
            vendors.append(Vendor(
                vendor_code=f"V{i:03d}",
                business_number=row['사업자등록번호'],
                name=row['상호'],
                status=status,
            ))
    return vendors
