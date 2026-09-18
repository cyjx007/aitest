import unittest

from aitest.core import EvaluationResult
from aitest.report import Report


class ReportTests(unittest.TestCase):
    def test_report_summary(self):
        report = Report([
            EvaluationResult("one", True, "ok"),
            EvaluationResult("two", False, "bad", ["missing"]),
        ])
        self.assertFalse(report.passed)
        self.assertEqual(report.total, 2)
        self.assertEqual(report.passed_count, 1)
        self.assertEqual(report.to_dict()["failed_count"], 1)
