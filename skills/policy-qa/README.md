# Policy Q&A

Answer company policy questions with traceable evidence from the supplied documents.

[Agent instructions](../../SKILL.md) · [Script guide](scripts/) · [Policy format](references/) · [Evaluation fixtures](../../evals/)

## What it does

- Retrieves numbered policy sections using BM25 and character-trigram matching, combined with Reciprocal Rank Fusion.
- Accepts alternate query wording to bridge everyday language and policy terminology.
- Excludes documents marked `SUPERSEDED` by default.
- Reports a coverage signal so the agent can abstain when evidence is missing.
- Instructs the agent to cite exact quotes, check role and location exceptions, and avoid unsupported answers.

The Python scripts retrieve evidence. The agent supplies query rewrites and writes
the final answer using the [citation rules](../../SKILL.md). The scripts do not generate answers.

## Quick start

Requires Python 3.9 or later. No package installation or API key is needed to run the scripts.
Run these commands from the repository root:

```bash
python skills/policy-qa/scripts/index.py evals/corpus
python skills/policy-qa/scripts/retrieve.py evals/corpus "How much annual paid leave do full-time employees earn?" --rewrite "annual paid leave days per calendar year" -k 5
```

The included corpus is fictional test data. For your own policies, replace
`evals/corpus` with a folder of UTF-8 Markdown or text files following the
[policy format guide](references/).

## Answer workflow

1. Locate the user's policy documents and confirm they have numbered sections.
2. Write two or three query rewrites while preserving the user's role, location, and other specifics.
3. Retrieve evidence and inspect `covered`, `excluded_superseded`, and `results`.
4. Check exceptions and gather all sections needed for the answer.
5. Answer with exact section quotes, or say the policies do not cover the question.

Example citation using the fictional leave policy:

> Full-time employees earn 20 days of paid leave per calendar year. [leave.md#2.1: "Full-time employees earn 20 days of paid leave per calendar year"]

## Documentation

| Location | Contents |
| --- | --- |
| [Skill instructions](../../SKILL.md) | Workflow, citation rules, and handling questions the policies do not cover. |
| [Scripts](scripts/) | Policy indexing, hybrid retrieval, and retrieval tests. |
| [Policy format](references/) | Supported documents, section IDs, dates, and superseded markers. |
| [Evaluation](../../evals/) | Evaluation fixtures and runners. |

## Validation

Run from the repository root:

```bash
python skills/policy-qa/scripts/test_retrieve.py
python evals/test_gold.py
python evals/test_eval_retrieval.py
python evals/eval_retrieval.py
```

The evaluator compares retrieval with and without saved, hand-written rewrites.
It reports recall@5, all-gold@5, missing evidence, false abstentions, and false
coverage. These checks measure fixtures and retrieval; they do not validate generated answers.

## Limits

Coverage is a lexical heuristic, not proof that a question is answerable. A retrieved
section may omit the group or exception the user asks about; inspect the evidence
before answering. Five results is the current default, not an established optimum.

Only `.md` and `.txt` files directly inside the supplied folder are read. PDF,
Word, OCR, and recursive folder ingestion are not implemented. Retrieval runs
locally; any handling of documents by an agent depends on the host you use.
