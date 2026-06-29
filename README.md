# purchase-fraud-detector

ERP가 통과시킨 매입거래를 **3축 병렬 검증**으로 재검증해 부정·이상을 잡아내는 외부 감사 분석 도구입니다.

---

## 프로젝트 소개

SAP·GRC 모듈을 갖춘 대기업과 달리, 영림원·더존·이카운트를 사용하는 중소·중견 기업은 **부정 패턴 탐지나 외부 공공 API 거래처 검증** 같은 상위 감사 레이어를 갖추기 어렵습니다.

이 프로젝트는 **SAP Clean Core의 Side-by-Side 외부 확장 패턴**에 따라, ERP에서 추출한 거래 데이터에 다중 신호 분석 레이어를 얹는 구조입니다. ERP 종류와 무관하게 이미 통과된 거래를 **독립적으로 재검증**합니다.

---

## 주요 기능 (3축 병렬 검증)

### ① 거래 정합성 검증 (3-Way Match)
PO(발주) · GR(입고) · Invoice(청구)의 수량·단가를 자동 대조합니다.

- **단가 검사:** 발주 단가 대비 청구 단가가 허용오차(기본 3%)를 벗어나면 적발
- **수량 검사:** 청구 수량이 입고 수량을 초과하면 적발
- **입고기록 검사:** 입고 없이 청구만 도착한 건 적발
- 청구 1건이 PO 여러 건을 묶는 **1:N 매칭**, 부분입고·분할청구 지원

허용오차는 Strategy 패턴(`PercentTolerance` / `AbsoluteTolerance`)으로 교체 가능합니다.

### ② 부정 패턴 탐지
- **중복 청구 탐지:** 같은 거래처가 7일 이내에 같은 금액을 두 번 청구하면 적발
- **라운드 금액 탐지:** 결재 한도 회피가 의심되는 금액(정확히 500만 원 등)이면 적발

### ③ 거래처 실재성 검증
**국세청 사업자등록 상태조회 API**를 실시간 호출해 폐업·휴업 거래처를 적발합니다.

---

## 판정 흐름

```
1. 입력      거래처 마스터(공정위 실데이터) + 거래 3종(합성)
       │
2. 전처리    데이터 로딩 · PO 기준 집계 (1:N · 부분입고 · 분할청구)
       │
3. 검증·탐지 [정합성] [부정 패턴] [거래처 실재성: 국세청 API]  ← 3축
       │
4. 판정      통합 판정 · 사유 자동 분류 (하나라도 적발 → 보류)
       │
5. 출력      엑셀 리포트 (판정결과 · 요약 통계 + 원본 데이터)
```

---

## 프로젝트 구조

```
purchase-fraud-detector/
├── src/                        # 핵심 패키지
│   ├── models.py               # 도메인 모델 (PO·GR·Invoice·Vendor)
│   ├── config.py               # 검사 기준 설정값
│   ├── loader.py               # CSV → 도메인 객체 변환
│   ├── result.py               # CheckResult · MatchResult
│   ├── engine.py               # 3축 검증 엔진
│   ├── report.py               # 엑셀 리포트 생성
│   ├── rules/
│   │   └── tolerance.py        # 허용오차 Strategy (Percent / Absolute)
│   ├── checkers/
│   │   └── consistency.py      # 3-Way Match 정합성 검사
│   ├── detectors/
│   │   ├── base.py             # AnomalyDetector 추상 클래스
│   │   ├── duplicate.py        # 중복 청구 탐지
│   │   └── round_amount.py     # 라운드 금액 탐지
│   └── verifiers/
│       ├── base.py             # VendorVerifier 추상 클래스
│       └── api.py              # 국세청 API 검증기
├── scripts/
│   ├── main.py                 # 실행 진입점
│   └── sample_data.py          # 합성 거래 데이터 생성 (9케이스)
├── data/
│   └── sample/
│       └── vendors.csv         # 샘플 거래처 데이터
├── output/                     # 생성 리포트 (gitignore)
├── tests/                      # 테스트 (추후 추가)
├── .env.example                # API 키 환경변수 템플릿
├── requirements.txt
└── README.md
```

---

## 빠른 시작

```bash
# 1. 클론
git clone https://github.com/dabok0519/purchase-fraud-detector.git
cd purchase-fraud-detector

# 2. 의존성 설치
pip install -r requirements.txt

# 3. API 키 설정 (선택)
cp .env.example .env
# .env 파일에 NTS_SERVICE_KEY=발급받은키 입력

# 4. 실행
python scripts/main.py
```

> API 키가 없어도 정합성·부정 패턴 검증은 정상 동작합니다. 거래처 검증만 '검증불가'로 처리됩니다.

---

## 설계 원칙

- **결정론적 코어 우선:** 외부 의존성 없이 합성 데이터만으로 모든 판정이 동작
- **확장 가능한 검증 구조:** 검사·탐지 클래스가 서로 독립적이라 새 신호 추가가 쉬움
- **외부 의존성 격리:** 거래처 검증을 추상 인터페이스 + 폴백으로 설계해 견고성 확보

---

## 기술 스택

- **Python** — OOP 설계 (dataclass, ABC/abstractmethod, Strategy 패턴, 의존성 주입)
- **requests** — 국세청 API 호출
- **openpyxl** — 엑셀 리포트 출력
- **python-dotenv** — API 키 환경변수 분리
