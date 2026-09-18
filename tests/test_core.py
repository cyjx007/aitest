import unittest

from aitest.core import Case, Evaluator


class FakeAdapter:
    def __init__(self, output: str):
        self.output = output

    def generate(self, prompt: str) -> str:
        return self.output


class EvaluatorTests(unittest.TestCase):
    def test_contains_and_forbidden_text(self):
        case = Case(
            id="greeting",
            input="hello",
            expected_contains=["hello"],
            expected_not_contains=["error"],
        )
        result = Evaluator(FakeAdapter("Hello there")).run_case(case)
        self.assertTrue(result.passed)
        self.assertEqual(result.failures, [])

    def test_reports_missing_text(self):
        case = Case(id="answer", input="x", expected_contains=["42"])
        result = Evaluator(FakeAdapter("41")).run_case(case)
        self.assertFalse(result.passed)
        self.assertIn("42", result.failures[0])

    def test_exact_output(self):
        case = Case(id="exact", input="x", exact="yes")
        self.assertTrue(Evaluator(FakeAdapter("yes")).run_case(case).passed)
        self.assertFalse(Evaluator(FakeAdapter("no")).run_case(case).passed)


if __name__ == "__main__":
    unittest.main()
