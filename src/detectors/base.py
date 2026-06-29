from abc import ABC, abstractmethod


class AnomalyDetector(ABC):
    """부정 패턴 탐지기의 공통 뼈대 (추상 클래스).

    모든 탐지기는 detect()를 구현해 동일한 인터페이스를 따른다.
    (ConsistencyChecker의 check_*와 대칭되는 구조)
    """

    @abstractmethod
    def detect(self, invoices) -> list:
        """청구 리스트 전체를 받아, 적발된 건을 CheckResult 리스트로 반환."""
        ...
