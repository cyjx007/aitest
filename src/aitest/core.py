from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, Sequence


class ModelAdapter(Protocol):
    """Minimal interface implemented by a model/provider integration."""

    def generate(self, prompt: str) -> str:
        ...


@dataclass(frozen=True)
class Case:
    """One deterministic AI evaluation case."""

    id: str
    input: str
    expected_contains: Sequence[str] = field(default_factory=tuple)
    expected_not_contains: Sequence[str] = field(default_factory=tuple)
    exact: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "Case":
        return cls(
            id=str(data["id"]),
            input=str(data["input"]),
            expected_contains=tuple(data.get("expected_contains", ())),
            expected_not_contains=tuple(data.get("expected_not_contains", ())),
            exact=data.get("exact"),
        )


@dataclass
class EvaluationResult:
    case_id: str
    passed: bool
    output: str
    failures: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "passed": self.passed,
            "output": self.output,
            "failures": self.failures,
        }


class Evaluator:
    """Run cases against a model adapter and evaluate returned text."""

    def __init__(self, adapter: ModelAdapter):
        self.adapter = adapter

    def run_case(self, case: Case) -> EvaluationResult:
        output = self.adapter.generate(case.input)
        failures: list[str] = []

        if case.exact is not None and output != case.exact:
            failures.append(f"expected exact output {case.exact!r}")

        for needle in case.expected_contains:
            if needle.casefold() not in output.casefold():
                failures.append(f"missing expected text {needle!r}")

        for needle in case.expected_not_contains:
            if needle.casefold() in output.casefold():
                failures.append(f"found forbidden text {needle!r}")

        return EvaluationResult(
            case_id=case.id,
            passed=not failures,
            output=output,
            failures=failures,
        )

    def run(self, cases: Sequence[Case]) -> list[EvaluationResult]:
        return [self.run_case(case) for case in cases]
