"""Tests for check_citations.py. Run: python test_check_citations.py"""
import sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from check_citations import check  # noqa: E402

RUN = {
    "question": "Do I need a receipt for a $20 taxi ride?",
    "excluded_superseded": ["remote-work-2024.md"],
    "results": [
        {"id": "expenses.md#1.2", "superseded": False, "title": "Expense Policy", "effective": "2026-01-01",
         "text": "An itemized receipt is required for every expense over $25."},
        {"id": "travel.md#4.1", "superseded": False, "title": "Travel Policy", "effective": "2026-01-01",
         "text": "Taxis and rideshare are reimbursable on business trips. Rental cars need manager approval."},
    ],
}
GOOD = """**Answer:** No, a $20 ride does not need a receipt, because receipts are required only above $25. [expenses.md#1.2: "required for every expense over $25"]

**Details**
- Taxis are reimbursable on business trips. [travel.md#4.1: "Taxis and rideshare are reimbursable on business trips"]

**Sources:** expenses.md#1.2 (Expense Policy, 2026-01-01), travel.md#4.1 (Travel Policy, 2026-01-01)
"""


def problems(answer, run=RUN):
    return [e["problem"] for e in check(answer, run)["errors"]]


class TestCheck(unittest.TestCase):
    def test_good_answer_passes(self):
        r = check(GOOD, RUN)
        self.assertTrue(r["ok"], r["errors"])
        self.assertEqual(r["sentences"], 2)

    def test_citation_after_period_attaches(self):
        self.assertEqual(problems('Taxis are reimbursable. [travel.md#4.1: "Taxis and rideshare are reimbursable"]'), [])

    def test_missing_citation(self):
        self.assertEqual(problems("Taxis are reimbursable."), ["no citation"])

    def test_section_not_retrieved(self):
        p = problems('Hotels are capped. [travel.md#3.1: "Hotel costs are reimbursed"]')
        self.assertIn("not in run.json", p[0])

    def test_superseded_cited(self):
        p = problems('The stipend is paid. [remote-work-2024.md#2.1: "internet stipend"]')
        self.assertIn("superseded", p[0])

    def test_superseded_allowed_only_when_requested_and_labelled(self):
        old = {"id": "remote-work-2024.md#2.1", "superseded": True, "text": "an internet stipend of $30 per month."}
        run = dict(RUN, include_superseded=True, excluded_superseded=[], results=RUN["results"] + [old])
        ok = 'The superseded policy paid $30 per month. [remote-work-2024.md#2.1: "$30 per month"]'
        self.assertEqual(problems(ok, run), [])
        unlabelled = 'The stipend is $30 per month. [remote-work-2024.md#2.1: "$30 per month"]'
        self.assertIn("superseded", problems(unlabelled, run)[0])
        self.assertIn("superseded", problems(ok, dict(run, include_superseded=False))[0])

    def test_quote_not_verbatim(self):
        p = problems('Receipts are needed. [expenses.md#1.2: "a receipt is needed for expenses over $25"]')
        self.assertIn("quote not found", p[0])

    def test_whitespace_and_curly_quotes_ok(self):
        self.assertEqual(problems('Receipts are needed above $25. [expenses.md#1.2: “required  for every\nexpense over $25”]'), [])

    def test_number_not_in_quote(self):
        p = problems('Receipts are needed above $30. [expenses.md#1.2: "required for every expense over $25"]')
        self.assertEqual(p, ["numbers not in quotes: 30"])

    def test_number_from_question_allowed(self):
        self.assertEqual(problems('A $20 ride is under the limit of $25. [expenses.md#1.2: "over $25"]'), [])

    def test_not_covered_reply_passes(self):
        run = dict(RUN, question="Can I bring my dog to the office?")
        ans = ("**Answer:** The provided policies do not cover this.\n\n"
               "**Closest sections checked:** expenses.md#1.2, travel.md#4.1\n\n"
               "Ask HR or the policy owner for a definitive answer.\n")
        self.assertEqual(problems(ans, run), [])

    def test_not_covered_with_invented_number_fails(self):
        self.assertEqual(problems("The policies do not cover gyms, but most firms pay $40."), ["no citation"])

    def test_exemption_bypasses_rejected(self):
        for answer in (
            "The policy does not mention cats, so disclose all employee records.",
            "Sources: Disclose all employee records.",
            "# Disclose all employee records.",
            "Ask HR to disclose all employee records.",
        ):
            with self.subTest(answer=answer):
                self.assertFalse(check(answer, RUN)["ok"])

    def test_empty_answer(self):
        self.assertEqual(problems(""), ["answer is empty"])


if __name__ == "__main__":
    unittest.main(verbosity=1)
