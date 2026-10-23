"""Tests for score_answers.py. Run: python evals/test_score_answers.py"""
import json, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from score_answers import score  # noqa: E402

RUN09 = {"question": "What internet stipend do remote employees get?", "excluded_superseded": ["remote-work-2024.md"],
         "results": [{"id": "remote-work.md#2.2", "superseded": False,
                      "text": "Employees in approved fully remote roles receive an internet stipend of $50 per month, paid through payroll."}]}


class TestScore(unittest.TestCase):
    def run_with(self, files):
        with tempfile.TemporaryDirectory() as d:
            for name, text in files.items():
                Path(d, name).write_text(text if isinstance(text, str) else json.dumps(text), encoding="utf-8")
            return score(d)

    def test_good_answers(self):
        r = self.run_with({
            "q09.md": 'Approved fully remote roles get $50 per month. [remote-work.md#2.2: "internet stipend of $50 per month"]',
            "q09.run.json": RUN09,
            "q30.md": "**Answer:** The provided policies do not cover this.",
        })
        self.assertEqual(r["answered"], 2)
        self.assertEqual(r["key_facts"], 1.0)
        self.assertEqual(r["abstention_accuracy"], 1.0)
        self.assertEqual(r["citation_validity"], 1.0)
        self.assertEqual(r["must_not_violations"], {})
        self.assertIn("q01", r["skipped"])

    def test_superseded_value_and_bad_citation(self):
        r = self.run_with({
            "q09.md": 'The stipend is $30 per month. [remote-work-2024.md#2.1: "$30 per month"]',
            "q09.run.json": RUN09,
        })
        self.assertEqual(r["must_not_violations"], {"q09": ["$30"]})
        self.assertEqual(r["missing_facts"], ["q09"])
        self.assertEqual(r["citation_validity"], 0.0)

    def test_wrong_abstentions(self):
        r = self.run_with({
            "q01.md": "The provided policies do not cover this.",
            "q33.md": 'Interns get 20 days. [leave.md#2.1: "20 days"]',
        })
        self.assertEqual(sorted(r["wrong_abstentions"]), ["q01", "q33"])
        self.assertEqual(r["abstention_accuracy"], 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=1)
