"""Split policy files into numbered sections

Usage: python index.py <policy-folder> [--out sections.index.json]

A section starts at a heading like "## 2 Paid leave" or "### 2.1 Annual paid leave".
Its ID is "<file name>#<number>", e.g. "leave.md#2.1".
A document is marked superseded when a line before its first section contains "SUPERSEDED".
"""
import argparse, json, re, sys
from pathlib import Path

HEAD = re.compile(r"^(#{2,6})\s+(\d+(?:\.\d+)*)\.?\s+(.+?)\s*$")
TITLE = re.compile(r"^#\s+(.+?)\s*$")
DATE = re.compile(r"effective(?: date)?:?\s*(\d{4}-\d{2}-\d{2})", re.I)
EXTS = {".md", ".txt"}


def parse_file(path):
    """Keep numbered sections separate so answers can cite a precise policy location."""
    title, effective, superseded, sections, cur = path.stem, None, False, [], None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = HEAD.match(line)
        if m:
            cur = {"id": f"{path.name}#{m.group(2)}", "doc": path.name, "number": m.group(2),
                   "heading": m.group(3), "text": ""}
            sections.append(cur)
            continue
        if cur is None:  # preamble: title, effective date, superseded marker
            t = TITLE.match(line)
            if t:
                title = t.group(1)
            d = DATE.search(line)
            if d and not effective:
                effective = d.group(1)
            if "SUPERSEDED" in line:
                superseded = True
        else:
            cur["text"] += line + "\n"
    for s in sections:
        s["text"] = s["text"].strip()
        s.update(title=title, effective=effective, superseded=superseded)
    return sections


def build_index(folder):
    """Read policy files directly in this folder and reject ambiguous citation IDs."""
    folder = Path(folder)
    if not folder.is_dir():
        raise SystemExit(f"Not a folder: {folder}")
    secs = [s for f in sorted(folder.iterdir()) if f.suffix.lower() in EXTS for s in parse_file(f)]
    ids = [s["id"] for s in secs]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        raise SystemExit(f"Duplicate section IDs (fix the numbering): {', '.join(dupes)}")
    if not secs:
        raise SystemExit(f"No numbered sections found in {folder} (.md or .txt with '## 1 Heading').")
    return secs


def main():
    """Write the index as JSON; send the summary to stderr to keep stdout parseable."""
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder")
    ap.add_argument("--out")
    a = ap.parse_args()
    secs = build_index(a.folder)
    text = json.dumps(secs, indent=1, ensure_ascii=False)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
    else:
        print(text)
    docs = sorted({s["doc"] for s in secs})
    old = sorted({s["doc"] for s in secs if s["superseded"]})
    print(f"{len(secs)} sections from {len(docs)} files; superseded: {', '.join(old) or 'none'}", file=sys.stderr)


if __name__ == "__main__":
    main()
