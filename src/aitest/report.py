from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Sequence

from .core import EvaluationResult


@dataclass(frozen=True)
class Report:
    results: Sequence[EvaluationResult]

    @property
    def passed(self) -> bool:
        return all(result.passed for result in self.results)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def passed_count(self) -> int:
        return sum(result.passed for result in self.results)

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "total": self.total,
            "passed_count": self.passed_count,
            "failed_count": self.total - self.passed_count,
            "results": [result.to_dict() for result in self.results],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
