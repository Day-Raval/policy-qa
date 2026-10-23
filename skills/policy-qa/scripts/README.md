# Script guide

[Skill overview](../) · [Policy format](../references/) · [Agent instructions](../../../SKILL.md)

Standard-library Python tools for indexing and retrieving numbered policy sections.
All commands below run from the repository root with Python 3.9+.

## Index policies

```bash
python skills/policy-qa/scripts/index.py evals/corpus --out sections.index.json
```

[`index.py`](index.py) reads `.md` and `.txt` files directly inside the folder.
It extracts section IDs, headings, body text, document titles, effective dates,
and superseded flags. Duplicate section IDs and inputs with no numbered sections
are rejected. Without `--out`, JSON is written to stdout; the summary goes to stderr.

## Retrieve evidence

```bash
python skills/policy-qa/scripts/retrieve.py evals/corpus "How much annual paid leave do full-time employees earn?" --rewrite "annual paid leave days per calendar year" -k 5 --out run.json
```

[`retrieve.py`](retrieve.py) builds its index from the policy folder on each run;
it does not consume the saved index JSON.

| Argument | Behavior |
| --- | --- |
| `folder` | Folder containing numbered policy documents. |
| `question` | Original question, quoted as one argument. |
| `--rewrite` | Additional query wording; repeat for multiple rewrites. |
| `-k` | Maximum results returned; default `5`. Use a positive integer. |
| `--include-superseded` | Include old policies for explicit historical questions. |
| `--out` | Write JSON to a file; otherwise print JSON to stdout. |

Rewrites are supplied by the caller. Retrieval does not load `evals/rewrites.json` automatically.

## Read the result

| JSON field | Meaning |
| --- | --- |
| `question`, `queries` | Original question and search variants used. |
| `covered` | Whether the best query/section coverage meets the threshold. |
| `coverage` | Best coverage value, matching section ID, and threshold (`0.55`). |
| `excluded_superseded` | Documents omitted because they are marked superseded. |
| `results` | Ranked sections with source metadata, exact body text, and fused scores. |

BM25 and character-trigram TF-IDF rankings are fused across all queries. Coverage
is calculated separately from ranking. Scores are ranking values, not confidence
probabilities. Even when `covered` is true, the agent must check whether the returned
text answers the user's specific question.

Empty parent headings contribute context to child sections but are not returned
as evidence. Supply at least one non-empty, eligible section for retrieval.

## Regression checks

```bash
python skills/policy-qa/scripts/test_retrieve.py
python evals/test_gold.py
python evals/test_eval_retrieval.py
python evals/eval_retrieval.py
```

The [retrieval tests](test_retrieve.py) check retrieval behavior. Gold validation
checks the answer-key fixtures; the evaluator measures evidence retrieval and
coverage mistakes. None of these commands grades an agent's generated prose.
