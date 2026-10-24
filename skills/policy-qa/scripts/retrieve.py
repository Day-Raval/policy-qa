"""Hybrid retrieval over policy sections: BM25 + character-trigram TF-IDF, fused with RRF.

Usage:
  python retrieve.py <policy-folder> "question" [--rewrite "other wording"]... [-k 5]
                     [--include-superseded] [--out run.json]

Each query (the question plus every rewrite) is ranked by both methods, and the
rankings are fused with Reciprocal Rank Fusion: score = sum of 1 / (60 + rank).
Superseded documents are left out unless --include-superseded is given.
"covered" is false when no query matches any section well enough (see
coverage below); the answer must then say the policies do not cover the question.
Headings with no text of their own (e.g. "## 2 Paid leave") are not returned;
their words are added to each child section instead.
"""
import argparse, json, math, re, sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from index import build_index  # noqa: E402

RRF_K = 60
# Abstention: coverage = IDF-weighted share of a query's content words found in one section.
# Words not in the corpus at all get the highest weight, so "dog" or "401k" sinks the score.
# Tuned on evals/: answerable questions (with rewrites) >= 0.70, out-of-scope ones <= 0.46.
MIN_COVERAGE = 0.55
NUMBER = re.compile(r"[$\d,.]+")

STOP = set("""a an and are as at be by can do does for from get go has have how i if in is it its
me much my need of on or our per should so than that the their there this to up was we what when
where which who will with would you your am any many each every all""".split())
WORD = re.compile(r"[a-z0-9$]+(?:[-'][a-z0-9]+)*")


def stem(w):
    """Strip one common suffix to match word variants without a language dependency."""
    for suf in ("ing", "ed", "es", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            return w[: -len(suf)]
    return w


def words(text):
    """Use the same lowercase, stop-word filtering and stemming for queries and policies."""
    return [stem(w) for w in WORD.findall(text.lower()) if w not in STOP]


def trigrams(text):
    """Compare three-character fragments to catch similar spellings; spaces preserve word edges."""
    out = []
    for w in WORD.findall(text.lower()):
        if w in STOP:
            continue
        p = f" {w} "
        out += [p[i:i + 3] for i in range(len(p) - 2)]
    return out


class Index:
    def __init__(self, sections):
        """Prepare word and character statistics once for all queries in this retrieval run."""
        self.secs = sections
        docs = [f"{s['title']} {s.get('parents', '')} {s['heading']} {s['text']}" for s in sections]
        self.tok = [words(d) for d in docs]
        self.tf = [Counter(t) for t in self.tok]
        self.avg = sum(map(len, self.tok)) / len(self.tok)
        n = len(docs)
        df = Counter(w for t in self.tok for w in set(t))
        self.idf = {w: math.log(1 + (n - c + 0.5) / (c + 0.5)) for w, c in df.items()}
        grams = [Counter(trigrams(d)) for d in docs]
        gdf = Counter(g for c in grams for g in c)
        self.gidf = {g: math.log((1 + n) / (1 + c)) + 1 for g, c in gdf.items()}
        self.gvec = [self._norm(c) for c in grams]
        self.maxidf = max(self.idf.values())

    def _norm(self, counts):
        """Weight rare fragments more heavily and normalize length for cosine comparison."""
        v = {g: c * self.gidf.get(g, 0) for g, c in counts.items()}
        z = math.sqrt(sum(x * x for x in v.values())) or 1
        return {g: x / z for g, x in v.items()}

    def bm25(self, q, k1=1.5, b=0.75):
        """Score keyword matches, limiting repeated-word gains and accounting for section length."""
        terms = words(q)
        out = []
        for i, tf in enumerate(self.tf):
            s = 0.0
            for w in terms:
                if w in tf:
                    f = tf[w]
                    s += self.idf[w] * f * (k1 + 1) / (f + k1 * (1 - b + b * len(self.tok[i]) / self.avg))
            out.append(s)
        return out

    def cosine(self, q):
        """Score shared character fragments, giving partial credit for similar word forms."""
        qv = self._norm(Counter(trigrams(q)))
        return [sum(x * d.get(g, 0) for g, x in qv.items()) for d in self.gvec]

    def coverage(self, q, i):
        """Estimate topic overlap with one section, penalizing query words absent from the corpus."""
        terms = {w for w in words(q) if not NUMBER.fullmatch(w)}  # amounts in a question are values, not topics
        toks = set(self.tok[i])
        total = got = 0.0
        for t in terms:
            wt = self.idf.get(t, self.maxidf)
            total += wt
            if t in toks or (len(t) >= 4 and any(x.startswith(t) for x in toks)):  # "ride" ~ "rideshare"
                got += wt
        return got / total if total else 0.0


def ranks(scores):
    """Convert positive scores to one-based ranks so different scoring methods can be combined."""
    order = sorted((i for i, s in enumerate(scores) if s > 0), key=lambda i: -scores[i])
    return {i: r for r, i in enumerate(order, 1)}


def retrieve(folder, question, rewrites=(), k=5, include_superseded=False):
    """Rank sections using the question and caller-supplied rewrites; report coverage separately.

    Rewrites are search alternatives, not answers; this function does not load rewrites.json.
    Coverage uses the best single query/section match, not the combined ranking score.
    """
    if not isinstance(k, int) or isinstance(k, bool) or not 1 <= k <= 50:
        raise SystemExit("k must be between 1 and 50")
    if not isinstance(question, str) or not question.strip() or len(question) > 4000:
        raise SystemExit("Question must contain 1 to 4000 characters")
    rewrites = list(rewrites)
    if len(rewrites) > 5 or any(not isinstance(r, str) or len(r) > 4000 for r in rewrites):
        raise SystemExit("Use at most 5 rewrites of at most 4000 characters each")
    allsecs = build_index(folder)
    parents = {(s["doc"], s["number"]): s["heading"] for s in allsecs if not s["text"]}
    for s in allsecs:
        parts = s["number"].split(".")
        s["parents"] = " ".join(parents.get((s["doc"], ".".join(parts[:i])), "")
                                for i in range(1, len(parts))).strip()
    secs = [s for s in allsecs if s["text"] and (include_superseded or not s["superseded"])]
    if not secs or not any(words(s["text"] + " " + s["heading"]) for s in secs):
        raise SystemExit("No searchable current policy sections remain")
    idx = Index(secs)
    queries = [question] + [r for r in rewrites if r.strip()]
    fused, best_cov, best_at = Counter(), 0.0, None
    for q in queries:
        b, c = idx.bm25(q), idx.cosine(q)
        for rk in (ranks(b), ranks(c)):
            for i, r in rk.items():
                fused[i] += 1 / (RRF_K + r)
        for i in range(len(secs)):
            cv = idx.coverage(q, i)
            if cv > best_cov:
                best_cov, best_at = cv, secs[i]["id"]
    covered = best_cov >= MIN_COVERAGE
    hits = [{key: secs[i][key] for key in ("id", "doc", "title", "heading", "effective", "superseded", "text")}
            | {"score": round(s, 5)} for i, s in fused.most_common(k)]
    return {
        "question": question,
        "queries": queries,
        "covered": covered,
        "coverage": {"best": round(best_cov, 3), "section": best_at, "threshold": MIN_COVERAGE},
        "excluded_superseded": sorted({s["doc"] for s in allsecs if s["superseded"]}) if not include_superseded else [],
        "results": hits,
    }


def main():
    """Accept repeated --rewrite phrases and emit the retrieval evidence as JSON."""
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder")
    ap.add_argument("question")
    ap.add_argument("--rewrite", action="append", default=[])
    ap.add_argument("-k", type=int, default=5)
    ap.add_argument("--include-superseded", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args()
    run = retrieve(a.folder, a.question, a.rewrite, a.k, a.include_superseded)
    text = json.dumps(run, indent=1, ensure_ascii=False)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
        print(f"covered={run['covered']}; top: {', '.join(h['id'] for h in run['results'])}")
    else:
        print(text)


if __name__ == "__main__":
    main()
