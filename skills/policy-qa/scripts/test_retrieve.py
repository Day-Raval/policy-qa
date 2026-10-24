"""Tests for index.py and retrieve.py. Run: python test_retrieve.py"""
import sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from index import build_index  # noqa: E402
from unittest.mock import patch
from retrieve import retrieve  # noqa: E402

DOCS = {
    "leave.md": """# Leave Policy
Effective date: 2026-01-01

## 1 Paid leave

### 1.1 Annual paid leave
Full-time employees earn 20 days of paid leave per year.

### 1.2 Carryover
Up to 5 unused days may be carried over until March 31.

## 2 Contractors

### 2.1 Contractor leave
Contractors are not eligible for paid leave.
""",
    "remote.md": """# Remote Work
Effective date: 2026-01-01

## 1 Stipend
Fully remote employees receive an internet stipend of $50 per month.
""",
    "remote-old.md": """# Remote Work (old)
Effective date: 2024-01-01. SUPERSEDED on 2026-01-01.

## 1 Stipend
Remote employees receive an internet stipend of $30 per month.
""",
    "notes.csv": "ignored, not a policy file\n",
}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        for name, text in DOCS.items():
            (self.dir / name).write_text(text, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()


class TestIndex(Base):
    def test_ids_titles_dates(self):
        secs = {s["id"]: s for s in build_index(self.dir)}
        self.assertIn("leave.md#1.1", secs)
        self.assertIn("remote.md#1", secs)
        self.assertNotIn("notes.csv#1", secs)
        self.assertEqual(secs["leave.md#2.1"]["title"], "Leave Policy")
        self.assertEqual(secs["leave.md#1.1"]["effective"], "2026-01-01")
        self.assertIn("20 days", secs["leave.md#1.1"]["text"])
        self.assertEqual(secs["leave.md#1"]["text"], "")

    def test_superseded_flag(self):
        secs = {s["id"]: s for s in build_index(self.dir)}
        self.assertTrue(secs["remote-old.md#1"]["superseded"])
        self.assertFalse(secs["remote.md#1"]["superseded"])

    def test_duplicate_ids_rejected(self):
        (self.dir / "dup.md").write_text("## 1 A\nx\n## 1 B\ny\n", encoding="utf-8")
        with self.assertRaises(SystemExit):
            build_index(self.dir)

    def test_policy_directory_rejected(self):
        (self.dir / "directory.md").mkdir()
        with self.assertRaises(SystemExit):
            build_index(self.dir)

    def test_reparse_file_rejected(self):
        from types import SimpleNamespace
        import stat
        with patch.object(Path, "lstat", return_value=SimpleNamespace(
                st_mode=stat.S_IFREG, st_file_attributes=0x400)):
            with self.assertRaises(SystemExit):
                build_index(self.dir)

    def test_oversized_file_rejected(self):
        with patch("index.MAX_FILE_BYTES", 10):
            with self.assertRaises(SystemExit):
                build_index(self.dir)

    def test_no_sections_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "a.md").write_text("no headings here\n", encoding="utf-8")
            with self.assertRaises(SystemExit):
                build_index(d)


class TestRetrieve(Base):
    def ids(self, run):
        return [h["id"] for h in run["results"]]

    def test_direct_match_first(self):
        run = retrieve(self.dir, "How many days of paid leave do full-time employees get?")
        self.assertEqual(self.ids(run)[0], "leave.md#1.1")
        self.assertTrue(run["covered"])

    def test_rewrite_rescues_synonym(self):
        raw = retrieve(self.dir, "How much vacation can I take?")
        self.assertFalse(raw["covered"])
        run = retrieve(self.dir, "How much vacation can I take?", ["annual paid leave days"])
        self.assertTrue(run["covered"])
        self.assertEqual(self.ids(run)[0], "leave.md#1.1")

    def test_superseded_excluded_by_default(self):
        run = retrieve(self.dir, "internet stipend")
        self.assertNotIn("remote-old.md#1", self.ids(run))
        self.assertEqual(run["excluded_superseded"], ["remote-old.md"])
        run = retrieve(self.dir, "internet stipend", include_superseded=True)
        self.assertIn("remote-old.md#1", self.ids(run))

    def test_empty_parent_heading_not_returned_but_searchable(self):
        run = retrieve(self.dir, "contractors")
        self.assertNotIn("leave.md#2", self.ids(run))
        self.assertEqual(self.ids(run)[0], "leave.md#2.1")

    def test_out_of_scope_not_covered(self):
        for q in ("Can I bring my dog to work?", "What is the 401(k) match?", "dental insurance plans"):
            self.assertFalse(retrieve(self.dir, q)["covered"], q)

    def test_amounts_do_not_count_toward_coverage(self):
        run = retrieve(self.dir, "Is there a $50 gym stipend?")
        self.assertLess(run["coverage"]["best"], 0.55)

    def test_invalid_query_limits(self):
        for options in ({"k": 0}, {"k": 51}, {"rewrites": ["x"] * 6}):
            with self.assertRaises(SystemExit):
                retrieve(self.dir, "leave", **options)
        with self.assertRaises(SystemExit):
            retrieve(self.dir, "x" * 4001)

    def test_all_superseded_rejected_cleanly(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / "old.md").write_text("SUPERSEDED\n## 1 Old\nLeave policy", encoding="utf-8")
            with self.assertRaisesRegex(SystemExit, "No searchable"):
                retrieve(folder, "leave")

    def test_k_limits_results(self):
        self.assertLessEqual(len(retrieve(self.dir, "leave", k=2)["results"]), 2)


if __name__ == "__main__":
    unittest.main(verbosity=1)
