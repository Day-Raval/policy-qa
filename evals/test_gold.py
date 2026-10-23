"""Checks the gold set against the corpus. Run: python evals/test_gold.py"""
import json, re, sys
from pathlib import Path

HERE = Path(__file__).parent
HEAD = re.compile(r"^#{2,3} (\d+(?:\.\d+)?) ")


def sections():
    out = {}
    for f in sorted((HERE / "corpus").glob("*.md")):
        sid = None
        for line in f.read_text(encoding="utf-8").splitlines():
            m = HEAD.match(line)
            if m:
                sid = f"{f.name}#{m.group(1)}"
                out[sid] = ""
            elif sid:
                out[sid] += line + "\n"
    return out


def main():
    secs = sections()
    qs = json.loads((HERE / "questions.json").read_text(encoding="utf-8"))
    errors = []
    assert len({q["id"] for q in qs}) == len(qs), "duplicate question ids"
    for q in qs:
        gold = " ".join(secs.get(s, "") for s in q["gold_sections"])
        errors += [f"{q['id']}: missing section {s}" for s in q["gold_sections"] if s not in secs]
        if q["answerable"] != bool(q["gold_sections"]):
            errors.append(f"{q['id']}: answerable flag does not match gold_sections")
        errors += [f"{q['id']}: no alternative of {alts} in gold text" for alts in q["key_facts"]
                   if not any(a.lower() in gold.lower() for a in alts)]
        errors += [f"{q['id']}: must_not '{b}' appears in gold text" for b in q["must_not"]
                   if b.lower() in gold.lower()]
    for e in errors:
        print("FAIL", e)
    print(f"{len(secs)} sections, {len(qs)} questions "
          f"({sum(q['answerable'] for q in qs)} answerable), {len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
