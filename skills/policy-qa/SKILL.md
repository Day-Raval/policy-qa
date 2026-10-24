---
name: policy-qa
description: Answers questions about a set of company policy documents (HR, leave, expenses, travel, IT security, code of conduct) using only those documents. Every sentence cites a numbered section with an exact quote, superseded policies are ignored, and questions the policies do not cover get "not covered" instead of a guess. Use when given policy files and asked what a policy says, allows or requires. Do not use for legal advice, for questions with no policy files, or for writing or editing policies.
---

# Policy Q&A

Answer questions from the user's policy documents only, with a checkable citation on every sentence.
Scripts use the Python standard library only (3.9+). `<skill>` below means this skill's folder.
Read `<skill>/references/answer-rules.md` before writing your first answer in a conversation.

## 1. Find the policies

- Copy the user's policy files (`.md` or `.txt`) into a new working folder, for example `policies/`, so other uploads are not searched. In Claude.ai, uploaded files are usually in `/mnt/user-data/uploads/`.
- If the user pasted policy text, save each policy as its own `.md` file in that folder.
- If a policy is a PDF or Word file, extract its text to a `.md` file and keep the heading numbers exactly as written.
- Sections must have numbered headings such as `## 2 Paid leave` and `### 2.1 Annual paid leave`. If a file has none, tell the user which file and ask for a version with numbered headings. Do not renumber the user's policies yourself.
- Never invent policy text. Never use general knowledge about "typical" company policies.

## 2. Rewrite the question

Write 2 or 3 short rewrites that use the words a policy would use, for example:
- "my boss" → "line manager approval"
- "WFH" → "working from home remote work"
- "rideshare to the airport" → "ground transport taxis reimbursement"

Keep the user's specifics (role, city, amount, contract type) in at least one rewrite.

## 3. Retrieve

```bash
python <skill>/scripts/retrieve.py policies "<question>" --rewrite "<rewrite 1>" --rewrite "<rewrite 2>" -k 5 --out run.json
```

Read `run.json`. Use only the `text` of the sections in `results`.

- `excluded_superseded` lists outdated documents. Never cite them. Only if the user asks what an older policy said, rerun with `--include-superseded` (see answer-rules.md, rule 8).
- If `covered` is `false`, go to step 6 ("not covered").
- For several questions in one message, run retrieval once per question (`run-1.json`, `run-2.json`, ...).

## 4. Answer

Before writing, check every retrieved section for:
- **Exceptions** in other sections (contractors, part-time staff, specific roles).
- **Values that change by location or role.** Give the value that matches the user's case.
- **Groups the question names that no section mentions.** Say the policies do not mention that group, and do not apply the general rule to them.
- **Questions that need two documents.** Cite both.
- **Two current policies that disagree.** Quote both and say they conflict.

Format:

```
**Answer:** <one or two sentences that answer the question directly> [<section id>: "<exact quote>"]

**Details**
- <one supporting fact per bullet> [<section id>: "<exact quote>"]

**Sources:** <section id> (<document title>, <effective date>), <section id> (<document title>, <effective date>)
```

Citation rules:
- Every sentence ends with at least one citation in the form `[leave.md#2.1: "exact words from that section"]`.
- The quote is copied character for character from the section text: a short span, not the whole section.
- Every number in a sentence (days, dollars, hours, dates) appears in that sentence's quotes, or in the user's question.
- If a fact is not in a retrieved section, leave it out.
- The only sentences allowed without a citation, and the exact Sources and Closest-sections formats, are listed in answer-rules.md under "Lines the checker accepts without a citation". Copy them exactly.

## 5. Check citations

Save the answer to `answer.md` and run:

```bash
python <skill>/scripts/check_citations.py answer.md run.json
```

- If `ok` is `true`, give the user the answer.
- Otherwise fix each listed sentence: copy the quote exactly from the section text, cite only sections in `run.json`, and remove any number that is not in a quote. Then run the check again.
- Run the check at most 3 times. If it still fails, delete the failing sentences and add the line: `Needs review: some statements could not be matched to the policy text.`
- Never show the user an answer whose check failed without that line.

## 6. Not covered

If `covered` is `false`, or the retrieved sections do not answer the question:

```
**Answer:** The provided policies do not cover this.

**Closest sections checked:** <section id> <heading>, <section id> <heading>, <section id> <heading>

Ask HR or the policy owner for a definitive answer.
```

Do not guess or fill gaps with typical practice.

## 7. Limits

- When the user asks what they are entitled to or what they should do, add this exact line: `This is a reading of the documents provided, not legal or HR advice.`
- Do not show `run.json` or the check output to the user unless they ask. Show the final answer only.
