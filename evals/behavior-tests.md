# Accuracy, trigger and behavior tests

Run in Claude.ai, each test in a new chat with the 7 files from `evals/corpus/` attached (including the superseded
`remote-work-2024.md`) and the skill uploaded as a zip that contains no test questions or answers. Results for v1.0.0, 2026-10-24.

## Accuracy: 33 gold questions

Four batches of 8-9 questions, each in a new chat, prompted with `/policy-qa` and the question text only.
Claude saved each checked answer and its retrieval run to `evals/answers/`; `python evals/score_answers.py` scores them.

| Metric | Result |
|---|---|
| Key facts in answers (27 answerable questions) | **1.000** |
| Superseded or wrong values stated (`must_not`) | **0** |
| Abstention accuracy (6 unanswerable, 27 answerable) | **1.000** |
| Answers passing `check_citations.py` | **33/33** |

Traps covered: policy wording that differs from the question (time off, USB stick, coffee shop, vendor), a superseded
policy with different numbers, exceptions in a later section, values that depend on city or role, an answer that needs
two documents, and six questions the policies don't cover. The hardest, q33 ("Do interns get paid leave?"), is marked
covered by retrieval because the leave sections match strongly; the answer rules made the skill reply "The policies do
not mention interns."

## Retrieval (no model)

`python evals/eval_retrieval.py`, gold sections in the top 5:

| Run | Recall@5 | Wrongly "not covered" | Wrongly "covered" |
|---|---|---|---|
| Question only | 27/27 | 8 (reworded questions) | q33 |
| Question + saved sample rewrites | 27/27 | 0 | q33 |

The sample rewrites in `evals/rewrites.json` were written by someone who had read the corpus, so the second row is an
upper bound. In real runs the model writes its own rewrites.

## Triggering (no `/policy-qa`)

| # | Prompt | Result |
|---|---|---|
| 1 | Am I allowed to expense a parking ticket? | Triggered, cites `expenses.md#1.3` |
| 2 | What does our expense policy say about receipts? | Triggered, cites `expenses.md#1.2` |
| 3 | Is it ok to book my own hotel outside the travel portal? | Triggered, cites `travel.md#1.2` |
| 4 | Do I have to tell anyone if I join another company's board? | Triggered, cites `code-of-conduct.md#2.1` |
| 5 | How many sick days do we get? | Triggered, cites `leave.md#3.1` |
| 6 | Write a remote work policy for my startup. | Not triggered (correct): drafted a policy instead, twice |

## Behavior

| # | Test | Result | Notes |
|---|---|---|---|
| B1 | "My manager refused my parental leave. Can I sue the company?" | Pass after fix | First run skipped the skill (the description excluded "legal advice") and cited outside law. Now: cited policy facts only, no legal opinion, ends with the not-advice and employment-lawyer lines |
| B2 | "What was the internet stipend under the 2024 remote work policy?" | Pass after fix | First run skipped the skill (the description said "ignores superseded policies"). Now: reruns with `--include-superseded`, labels $30 as superseded, gives the current $50 |
| B3 | Answer shown matches answer checked | Pass after fix | Twice the model checked a draft, then split a sentence for display, leaving it uncited. SKILL.md now says to send `answer.md` exactly as checked; follow-up check output was `ok: true` for the shown text |
| B4 | Pasted policy text without numbered headings | Pass | Not triggered without `/policy-qa` (no files attached). With `/policy-qa` it asked for numbered sections and labelled the pasted value as unchecked |

## Issues found and fixed during testing

1. Answer-rules examples used Sources and Ask-HR lines the strict checker rejects; the docs now list the exact accepted lines and all 7 examples pass.
2. The checker rejected the `Needs review` line that SKILL.md asks for; it is now on the allowlist.
3. Quick lookups answered without the skill; the description now says to use it even when the answer looks obvious.
4. Legal and old-policy questions skipped the skill because of description wording (B1, B2).
5. The checked answer was reworded before display (B3).
6. Early SKILL.md examples matched gold questions word for word; they were replaced with neutral examples so the test set stays unseen.
