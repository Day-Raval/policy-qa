---
name: policy-qa
description: Answers questions about a set of company policy documents (HR, leave, expenses, travel, IT security, code of conduct) using only those documents. Every sentence cites a numbered section with an exact quote, superseded policies are ignored, and questions the policies do not cover get "not covered" instead of a guess. Use when given policy files and asked what a policy says, allows or requires. Do not use for legal advice, for questions with no policy files, or for writing or editing policies.
---

# Policy Q&A

Answer questions from the user's policy documents only, with a checkable citation on every sentence.
Scripts use the Python standard library only (3.9+). `<skill>` below means this skill's folder.

## 1. Find the policies

- Use the folder of policy files the user gives (`.md` or `.txt`). If they pasted policy text, save each policy as its own `.md` file in a new working folder.
- Sections must have numbered headings such as `## 2 Paid leave` and `### 2.1 Annual paid leave`. If a file has none, tell the user which file and ask for a version with numbered headings. Do not renumber the user's policies yourself.
- Never invent policy text. Never use general knowledge about "typical" company policies.

## 2. Rewrite the question

Write 2 or 3 short rewrites that use the words a policy would use, for example:
- "time off" → "annual paid leave days"
- "USB stick" → "USB storage devices"
- "coffee shop" → "public Wi-Fi VPN"

Keep the user's specifics (role, city, amount, contract type) in at least one rewrite.

## 3. Retrieve

```bash
python <skill>/scripts/retrieve.py <policy-folder> "<question>" --rewrite "<rewrite 1>" --rewrite "<rewrite 2>" -k 5 --out run.json
```

Read `run.json`. Use only the `text` of the sections in `results`.

- `excluded_superseded` lists outdated documents. Never cite them. Only if the user asks what an older policy said, rerun with `--include-superseded` and label those sections as superseded.
- If `covered` is `false`, go to step 5 ("not covered").

## 4. Answer

Before writing, check the retrieved sections for:
- **Exceptions** in other sections (contractors, part-time staff, roles such as "Directors and above").
- **Values that change by location or role** (high-cost cities, seniority). Give the value that matches the user's case.
- **Groups the question names that no section mentions** (for example "interns"). Then say the policies do not mention that group, and do not apply the general rule to them.
- **Questions that need two documents** (for example a hotel cap and a meal allowance). Cite both.

Format:

```
**Answer:** <one or two sentences that answer the question directly> [<section id>: "<exact quote>"]

**Details**
- <one supporting fact per bullet> [<section id>: "<exact quote>"]

**Sources:** <section ids, with document titles and effective dates>
```

Citation rules:
- Every sentence ends with at least one citation in the form `[leave.md#2.1: "exact words from that section"]`.
- The quote is copied character for character from the section text: a short span, not the whole section.
- Every number in a sentence (days, dollars, hours, dates) appears in that sentence's quotes.
- If a fact is not in a retrieved section, leave it out.

## 5. Not covered

If `covered` is `false`, or the retrieved sections do not answer the question:

```
**Answer:** The provided policies do not cover this.

**Closest sections checked:** <up to 3 section ids and headings from run.json>

Ask HR or the policy owner for a definitive answer.
```

Do not guess or fill gaps with typical practice.

## 6. Limits

State these when relevant, briefly:
- This is a reading of the documents provided, not legal or HR advice.
- If two current policies conflict, show both quotes and say they conflict. Do not pick one.