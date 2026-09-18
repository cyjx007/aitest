"""aitest: a tiny harness for AI regression tests."""

from .core import Case, EvaluationResult, Evaluator, ModelAdapter

__all__ = ["Case", "EvaluationResult", "Evaluator", "ModelAdapter"]
__version__ = "0.1.0"
