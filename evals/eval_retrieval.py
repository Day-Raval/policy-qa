"""Compare retrieval with and without saved rewrites: python evals/eval_retrieval.py.

Recall@5 is the mean fraction of gold sections retrieved per answerable question.
All-gold@5 counts questions where every required section is retrieved.
These measure retrieval, not whether a generated answer is correct.
"""
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "skills" / "policy-qa" / "scripts"))
from retrieve import retrieve  # noqa: E402


def evaluate(questions, rewrites):
    """Keep missing evidence and coverage mistakes visible by question ID."""
    recalls, complete, false_abstentions, false_coverage = [], [], [], []
    for q in questions:
        run = retrieve(HERE / "corpus", q["question"], rewrites.get(q["id"], []))
        found = {s["id"] for s in run["results"]}
        gold = set(q["gold_sections"])
        if q["answerable"]:
            recalls.append(len(gold & found) / len(gold))
            if gold <= found:
                complete.append(q["id"])
            if not run["covered"]:
                false_abstentions.append(q["id"])
        elif run["covered"]:
            false_coverage.append(q["id"])
    return {
        "recall@5": round(sum(recalls) / len(recalls), 3),
        "all_gold@5": f"{len(complete)}/{len(recalls)}",
        "missing_gold": [q["id"] for q in questions if q["answerable"] and q["id"] not in complete],
        "false_abstentions": false_abstentions,
        "false_coverage": false_coverage,
    }


def main():
    """Join fixtures by ID and fail early if the rewrite mapping is incomplete or malformed."""
    questions = json.loads((HERE / "questions.json").read_text(encoding="utf-8"))
    rewrites = json.loads((HERE / "rewrites.json").read_text(encoding="utf-8"))
    note = rewrites.pop("_note", "Hand-written rewrites may overestimate real-world performance.")
    ids = {q["id"] for q in questions}
    if len(ids) != len(questions) or set(rewrites) != ids:
        raise SystemExit("Question IDs must be unique and match rewrite IDs exactly.")
    if not all(isinstance(rs, list) and rs and
               all(isinstance(r, str) and r.strip() for r in rs) for rs in rewrites.values()):
        raise SystemExit("Each rewrite entry must be a non-empty list of non-blank strings.")
    print(json.dumps({"note": note, "without_rewrites": evaluate(questions, {}),
                      "with_saved_rewrites": evaluate(questions, rewrites)}, indent=2))


if __name__ == "__main__":
    main()
