# Policy Q&A

An agent skill that answers questions about your company's policy documents, **where every sentence cites a numbered section with an exact quote, and a script checks every quote and number before the answer is shown**.

Ask an LLM "how much leave do contractors get?" with a stack of policies attached and it usually answers fluently. It fails quietly: it quotes last year's policy, stops at the general rule and misses the contractor exception two sections later, or fills a gap with what "most companies" do. This skill makes those failures visible. Bundled Python scripts (standard library only) find the relevant sections, exclude superseded documents, and check the model's answer sentence by sentence. Anything that can't be matched to the policy text is rewritten or removed, and questions the policies don't cover get "not covered" instead of a guess.

## What you get

- A direct answer first, then supporting details, then sources with document titles and effective dates
- A `[section: "exact quote"]` citation on every sentence, checked against the retrieved section text
- Every number (days, dollars, hours) checked against the sentence's own quotes
- Superseded policies excluded, unless you ask what an older version said
- Exceptions, location- and role-dependent values, and answers that span two documents
- "The provided policies do not cover this." for gaps, with the closest sections checked
- No legal opinion: legal questions get the policy facts and a pointer to an employment lawyer

Example, from the synthetic policies in `evals/corpus/`:

```
Q: Can contractors expense a home-office chair?

**Answer:** No, contractors cannot expense a home-office chair, because travel costs are the only expenses contractors may claim. [expenses.md#6.1: "No other expenses are reimbursable for contractors."]

**Details**
- The home-office equipment allowance, which includes chairs, is for full-time employees. [expenses.md#4.2: "Home-office equipment up to $300 per year is reimbursable for full-time employees. This includes chairs, desks and monitors."]

**Sources:** expenses.md#6.1 (Expense Policy, 2026-01-01), expenses.md#4.2 (Expense Policy, 2026-01-01)
```

## How it works

```
question ──► model writes 2-3 rewrites in policy words
                │
                ▼
         retrieve.py  (BM25 + character trigrams, fused with RRF; superseded docs excluded)
                │
        covered? ──no──► "The provided policies do not cover this." + closest sections
                │ yes
                ▼
         model answers from retrieved text only ──► check_citations.py ──ok──► reply, unchanged
                ▲                                         │ errors
                └──── fix only the flagged sentences ─────┤ (max 3 runs)
                                                          └── still failing → drop them + "Needs review"
```

`check_citations.py` checks every sentence:

| Check | Catches | Example message |
|---|---|---|
| Citation present | A claim with no source | `no citation` |
| Section retrieved | A citation to a section the search never returned | `travel.md#3.1: section not in run.json results` |
| Quote verbatim | A paraphrase presented as a quote | `quote not found in section: "Paris lodging is capped at $260 a night"` |
| Numbers | A number that isn't in the sentence's quotes | `numbers not in quotes: 250` |
| Superseded | Citing an outdated policy without saying so | `remote-work-2024.md#2.1: superseded document` |
| Metadata | Sources lines that don't match the retrieved sections | `invalid source metadata` |

Only a short allowlist of lines may appear without a citation ("not covered", "do not mention", the not-advice line and a few others), so an uncited claim can't slip through by sounding like a disclaimer.

## Requirements

- Python 3.9 or newer (`python3 --version`). No packages to install.
- Policies as `.md` or `.txt` files with numbered headings, for example `## 2 Paid leave` and `### 2.1 Annual paid leave`. Section IDs are built from them (`leave.md#2.1`).
- To mark an outdated document, put `SUPERSEDED` in a line before its first heading.

## Install

Works in Claude Code, Claude.ai, OpenAI Codex, Gemini CLI, Cursor and GitHub Copilot. The skill uses the open SKILL.md format, so any compatible agent can load it.

**Any agent (script)**: from the repo root, run `./install.sh` to install into every agent found in your home folder, `./install.sh --all` for all five, or `./install.sh claude codex` for specific ones.

**Any agent (manual install)**:

1. On the [repository page](https://github.com/Day-Raval/policy-qa), choose **Code > Download ZIP** and extract it.
2. Copy the entire `skills/policy-qa/` folder into your agent's skills folder below. Keep its name and contents together.
3. Start a new chat in the agent.

On Windows, `~` means your Windows user folder (for example, `C:\Users\<you>`).

| Agent | Skills folder |
|---|---|
| Claude Code | `~/.claude/skills/` |
| OpenAI Codex | `~/.agents/skills/` |
| Gemini CLI | `~/.gemini/skills/` |
| Cursor | `~/.cursor/skills/` |
| GitHub Copilot | `~/.copilot/skills/` |

**Claude Code plugin** (gets updates with `claude plugin update`):
```
claude plugin marketplace add Day-Raval/policy-qa
claude plugin install policy-qa@policy-qa
```

**Claude.ai**: zip the `skills/policy-qa/` folder and upload it under Settings > Capabilities > Skills. Code execution must be on, because the skill runs Python scripts.

**Agents without skill support**: open this repo in the agent. `AGENTS.md` tells it to follow `skills/policy-qa/SKILL.md`.

## Use

Attach your policy files and ask:
```
Am I allowed to expense a parking ticket?
What was the internet stipend under the 2024 remote work policy?
Do contractors get paid leave?
```
For the most reliable results, start the message with `/policy-qa`.

To run the scripts without an agent:
```
python3 skills/policy-qa/scripts/retrieve.py policies "How much paid leave do I get?" --rewrite "annual paid leave days" --out run.json
python3 skills/policy-qa/scripts/check_citations.py answer.md run.json
```

## Try it with sample data

`evals/corpus/` holds seven synthetic policies for a fictional company, Quillmark Systems: leave, remote work (current and a superseded 2024 version), expenses, travel, IT security and code of conduct. `evals/questions.json` has 33 gold questions with planted traps: wording that differs from the policy, the superseded policy's old numbers, exceptions in later sections, values that depend on city or role, a two-document answer and six questions the policies don't cover.

```
python3 evals/eval_retrieval.py        # recall@5 and "not covered" accuracy, with and without rewrites
python3 evals/score_answers.py         # scores the saved answers in evals/answers/
```

The test questions and answers live outside the skill folder on purpose: an agent running the skill never has the answer key in reach.

## Results

Tested in Claude.ai (v1.0.0), each run in a fresh chat with the skill uploaded without any test data:

| Test | Result |
|---|---|
| 33 gold questions (27 answerable, 6 not covered) | **Key facts 1.000, abstention 1.000, 33/33 answers pass the citation check, 0 superseded values** |
| Retrieval, gold sections in top 5 | **27/27**, with and without rewrites |
| Triggering without `/policy-qa` | 5/5 held-out policy questions; stays out of "write a policy" requests (2/2) |
| Legal question ("Can I sue?") | Policy facts only, no legal opinion, points to an employment lawyer |
| Old-policy question | Labels the 2024 value as superseded and gives the current one |

Testing found and fixed 6 issues before release, including two description wordings that made the skill skip legal and old-policy questions, and a model habit of rewording an answer after it passed the check. Full record: `evals/behavior-tests.md`.

## Privacy and safety

- **Synthetic data only in this repo.** Every policy here is fictional and marked `SYNTHETIC`; CI fails if a corpus file lacks that banner. Never commit real company policies.
- **No additional services.** The bundled scripts make no network calls. The skill has no MCP servers or developer-operated backend receiving documents.
- **Working files.** The skill copies the supplied policies into a working folder and writes its search results (`run.json`) and draft answer (`answer.md`) there so the scripts can check them. Files are processed in the chosen agent's execution environment, which may be local or hosted.
- **Platform retention.** The chosen agent still processes the documents and answers. Chat messages, uploads and outputs remain subject to that platform's privacy and retention settings and policies.
- **Internal policies may be confidential.** Use them only in an environment you are authorized to use.
- **Not legal or HR advice.** The skill reports what the documents say. It does not interpret law or decide disputes.

## Limits

- Policies must be `.md` or `.txt` with numbered headings. PDF or Word files have to be converted to text first, keeping the heading numbers.
- Retrieval is lexical (no embeddings). Questions worded very differently from the policy depend on the model's rewrites.
- The "not covered" threshold (0.55) was tuned on 33 questions; other policy sets may need a different value in `retrieve.py`.
- `check_citations.py` proves a quote is in the cited section, not that the quote supports the sentence. That's what the gold questions and `score_answers.py` are for.
- Numbers written as words ("three days") are not checked.
- Triggering is decided by the model and can vary. Starting with `/policy-qa` always loads the skill. To confirm an answer, ask "Show me the check output for the answer as shown."

## Troubleshooting

| Problem | Fix |
|---|---|
| `No numbered sections found` | Add numbered headings (`## 1 Scope`, `### 1.1 Eligibility`) to each policy file |
| `Duplicate section IDs` | Two headings in one file share a number; renumber them in the source document |
| An old value appears in an answer | Put `SUPERSEDED` in a line before the first heading of the outdated file |
| Too many "not covered" replies | Lower `MIN_COVERAGE` in `scripts/retrieve.py` and re-run `evals/eval_retrieval.py` |
| `python3: command not found` | Install Python 3.9+ (on Windows, use `py` in place of `python3`) |
| Claude.ai can't run the scripts | Turn on code execution under Settings > Capabilities |
| Skill doesn't load | Start a new chat with the policies attached, or call it directly with `/policy-qa` |
| Other issues | Open an issue: https://github.com/Day-Raval/policy-qa/issues |

## Testing

```
python3 skills/policy-qa/scripts/test_retrieve.py
python3 skills/policy-qa/scripts/test_check_citations.py
python3 evals/test_gold.py
python3 evals/test_score_answers.py
```
They check the indexer and retriever, every checker rule (including attempts to slip claims past it), that every gold fact exists in the corpus, and the answer scorer. CI runs them on Python 3.9 and 3.12, along with the retrieval gate and the saved-answer scores.

## Repository layout

```
skills/policy-qa/            the skill (this is what gets installed or zipped)
├── SKILL.md
├── references/answer-rules.md
└── scripts/index.py, retrieve.py, check_citations.py, test_retrieve.py, test_check_citations.py
evals/                       test data and tests (never installed)
├── corpus/                  7 synthetic policies, one superseded
├── questions.json, rewrites.json
├── answers/                 Claude.ai answers and retrieval runs for all 33 questions
├── eval_retrieval.py, score_answers.py, test_gold.py, test_score_answers.py
└── behavior-tests.md
```

## Security

See [SECURITY.md](SECURITY.md) to report a vulnerability.

## License

MIT
