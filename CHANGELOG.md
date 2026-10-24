# Changelog

## 1.0.0 (2026-10-24)
- First public release.
- `scripts/index.py`: splits `.md` and `.txt` policies into numbered sections (`leave.md#2.1`), reads titles and effective dates, marks documents labelled SUPERSEDED, rejects duplicate section IDs.
- `scripts/retrieve.py`: hybrid retrieval (BM25 plus character-trigram TF-IDF, fused with Reciprocal Rank Fusion) over the question and the model's 2-3 rewrites. Superseded documents are excluded unless `--include-superseded` is given. An IDF-weighted coverage score marks questions the policies don't cover.
- `scripts/check_citations.py`: every sentence needs a `[section: "exact quote"]` citation to a retrieved section; quotes must appear verbatim; every number must appear in the sentence's quotes or the question; superseded sections only when asked for and labelled. Uncited lines are limited to a fixed allowlist, and Sources lines must match `run.json`.
- SKILL.md: rewrite, retrieve, answer, check (at most 3 runs, then a `Needs review` line), reply with the checked text unchanged. "Not covered" and "do not mention" replies for gaps. Legal questions get policy facts only, no legal opinion.
- `references/answer-rules.md`: 12 rules and 7 worked examples from a separate fictional company, each passing the checker.
- `evals/`: 7 synthetic policies (one superseded), 33 gold questions with planted traps, retrieval and answer scorers, and the Claude.ai answers for all 33 questions.
- Tested in Claude.ai: 33/33 questions with key facts, abstention and citation validity all 1.000; recall@5 27/27; 5/5 held-out trigger prompts. Full record in `evals/behavior-tests.md`.
- Works in Claude Code, Claude.ai, Codex, Gemini CLI, Cursor and GitHub Copilot via `install.sh`, plus an `AGENTS.md` fallback.
