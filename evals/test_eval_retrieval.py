"""Check evaluation accounting: python -m unittest discover -s evals."""
import unittest
from unittest.mock import patch

from eval_retrieval import evaluate


class TestEvaluation(unittest.TestCase):
    def test_rewrites_partial_recall_and_coverage_errors(self):
        """Partial evidence must not count as complete, and coverage errors stay separate."""
        questions = [
            {"id": "a", "question": "two policies", "answerable": True,
             "gold_sections": ["one#1", "two#1"]},
            {"id": "b", "question": "unknown topic", "answerable": False,
             "gold_sections": []},
        ]
        with patch("eval_retrieval.retrieve", side_effect=[
            {"results": [{"id": "one#1"}], "covered": False},
            {"results": [], "covered": True},
        ]) as retrieve:
            report = evaluate(questions, {"a": ["alternate wording"]})
        self.assertEqual(retrieve.call_args_list[0].args[2], ["alternate wording"])
        self.assertEqual(retrieve.call_args_list[1].args[2], [])
        self.assertEqual(report, {
            "recall@5": 0.5, "all_gold@5": "0/1", "missing_gold": ["a"],
            "false_abstentions": ["a"], "false_coverage": ["b"],
        })


if __name__ == "__main__":
    unittest.main()
