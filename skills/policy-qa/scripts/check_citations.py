"""Check every sentence of a policy answer against the retrieval run

Usage: python check_citations.py <answer.md> <run.json>

A citation looks like [leave.md#2.1: "exact words from that section"].
Each sentence must pass:
  1. it has at least one citation (unless it only says the policies do not cover or
     mention something, or is a Sources / Closest sections / advice line);
  2. every cited section was retrieved in run.json;
  3. no cited section is from a superseded document;
  4. every quote appears in its section's text (ignoring whitespace and quote style);
  5. every number in the sentence appears in its quotes or in the user's question.
Prints a JSON report. Exit code 0 = all pass, 1 = problems found.
"""
import json, re, sys
from pathlib import Path

CITE = re.compile(r"\[([^\[\]\s:]+#[\d.]*\d):\s*[\"“]([^\"”]+)[\"”]\]")
NUM = re.compile(r"\d[\d,]*(?:[.:]\d+)?")
SPLIT = re.compile(r"(?<=[.!?])\s+")
NO_CLAIM = re.compile(r"do(?:es)? not (?:cover|mention)|not covered|not legal or HR advice"
                      r"|^ask HR|^closest sections|^sources:", re.I)
CITE_ONLY = re.compile(r"^(?:\s*⟦\d+⟧[.,;]?)+\s*$")


def norm(s):
    s = s.replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'")
    return re.sub(r"\s+", " ", s).strip()


def numbers(s):
    return {n.replace(",", "") for n in NUM.findall(s)}


def sentences(answer):
    """Yield (sentence text without citations, [(section id, quote)])."""
    cites = []

    def hold(m):
        cites.append((m.group(1), m.group(2)))
        return f"⟦{len(cites) - 1}⟧"

    for line in CITE.sub(hold, answer).splitlines():  # replace citations first: a quote may wrap lines
        line = re.sub(r"^\s*(?:[-*+]|\d+\.)\s+", "", line).replace("**", "").strip()
        if not line or line.startswith(("#", "```")) or line.lower() in ("details", "answer:"):
            continue
        parts = []
        for frag in SPLIT.split(line):
            if parts and CITE_ONLY.match(frag):  # "20 days. [cite]" -> cite belongs to the previous sentence
                parts[-1] += " " + frag
            else:
                parts.append(frag)
        for p in parts:
            ids = [int(i) for i in re.findall(r"⟦(\d+)⟧", p)]
            text = re.sub(r"\s*⟦\d+⟧", "", p).strip()
            if text:
                yield text, [cites[i] for i in ids]


def check(answer, run):
    secs = {h["id"]: h for h in run["results"]}
    old_docs = set(run.get("excluded_superseded", []))
    asked = numbers(run.get("question", ""))
    errors, n = [], 0
    for text, cites in sentences(answer):
        n += 1
        label = text if len(text) <= 90 else text[:87] + "..."
        if not cites:
            if not NO_CLAIM.search(text) or (numbers(text) - asked and not re.match(r"(?i)closest|sources", text)):
                errors.append({"sentence": label, "problem": "no citation"})
            continue
        quotes = ""
        for sid, quote in cites:
            sec = secs.get(sid)
            if sec is None:
                why = "superseded document" if sid.split("#")[0] in old_docs else "section not in run.json results"
                errors.append({"sentence": label, "problem": f"{sid}: {why}"})
                continue
            if sec.get("superseded"):
                errors.append({"sentence": label, "problem": f"{sid}: superseded document"})
            if norm(quote) not in norm(sec["text"]):
                errors.append({"sentence": label, "problem": f"{sid}: quote not found in section: \"{quote}\""})
            quotes += " " + quote
        missing = numbers(text) - numbers(quotes) - asked
        if missing:
            errors.append({"sentence": label, "problem": f"numbers not in quotes: {', '.join(sorted(missing))}"})
    if n == 0:
        errors.append({"sentence": "", "problem": "answer is empty"})
    return {"ok": not errors, "sentences": n, "errors": errors}


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    answer = Path(sys.argv[1]).read_text(encoding="utf-8")
    run = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    report = check(answer, run)
    print(json.dumps(report, indent=1, ensure_ascii=False))
    sys.exit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
