"""Grade saved answers against the gold questions. 

Usage: python evals/score_answers.py [answers-folder]   (default: evals/answers)

The folder holds one answer per question, named by ID: q01.md, q02.md, ...
If qNN.run.json (from retrieve.py --out) sits next to an answer, citations are checked too.
Questions with no answer file are skipped and listed.

Metrics:
  key_facts     share of key facts present (any listed wording counts), answerable questions
  must_not      answers that state a superseded or wrong value
  abstention    unanswerable questions answered "not covered / not mentioned", and
                answerable questions NOT wrongly refused
  citations     share of checked answers that pass check_citations.py
"""
import json, re, sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "skills" / "policy-qa" / "scripts"))
from check_citations import check  # noqa: E402

ABSTAIN = re.compile(r"do(?:es)? not (?:cover|mention)|not covered|not mentioned", re.I)


def score(folder):
    qs = json.loads((HERE / "questions.json").read_text(encoding="utf-8"))
    folder = Path(folder)
    rows, skipped = [], []
    for q in qs:
        f = folder / f"{q['id']}.md"
        if not f.exists():
            skipped.append(q["id"])
            continue
        ans = f.read_text(encoding="utf-8")
        low = ans.lower()
        row = {"id": q["id"], "answerable": q["answerable"], "abstained": bool(ABSTAIN.search(ans))}
        if q["answerable"]:
            row["facts_found"] = sum(any(a.lower() in low for a in alts) for alts in q["key_facts"])
            row["facts_total"] = len(q["key_facts"])
            row["must_not_hits"] = [b for b in q["must_not"] if b.lower() in low]
        run = folder / f"{q['id']}.run.json"
        if run.exists():
            rep = check(ans, json.loads(run.read_text(encoding="utf-8")))
            row["citations_ok"] = rep["ok"]
            row["citation_errors"] = rep["errors"]
        rows.append(row)

    ans_rows = [r for r in rows if r["answerable"]]
    facts = sum(r["facts_found"] for r in ans_rows), sum(r["facts_total"] for r in ans_rows)
    abst_right = sum(r["abstained"] != r["answerable"] for r in rows)
    cited = [r for r in rows if "citations_ok" in r]
    return {
        "answered": len(rows),
        "skipped": skipped,
        "key_facts": round(facts[0] / facts[1], 3) if facts[1] else None,
        "missing_facts": [r["id"] for r in ans_rows if r["facts_found"] < r["facts_total"]],
        "must_not_violations": {r["id"]: r["must_not_hits"] for r in ans_rows if r["must_not_hits"]},
        "abstention_accuracy": round(abst_right / len(rows), 3) if rows else None,
        "wrong_abstentions": [r["id"] for r in rows if r["abstained"] == r["answerable"]],
        "citation_validity": round(sum(r["citations_ok"] for r in cited) / len(cited), 3) if cited else None,
        "citation_failures": {r["id"]: r["citation_errors"] for r in cited if not r["citations_ok"]},
    }


def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else HERE / "answers"
    if not Path(folder).is_dir():
        sys.exit(f"No answers folder: {folder}. Save answers as q01.md, q02.md, ... there.")
    rep = score(folder)
    print(json.dumps(rep, indent=2, ensure_ascii=False))
    bad = rep["missing_facts"] or rep["must_not_violations"] or rep["wrong_abstentions"] or rep["citation_failures"]
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
