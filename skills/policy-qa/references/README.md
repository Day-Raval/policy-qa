# Policy format and evidence conventions

[Skill overview](../) · [Script guide](../scripts/) · [Agent instructions](../../../SKILL.md)

Use this guide to prepare documents for retrieval. The authoritative answer-writing
workflow remains in the root `SKILL.md`.

## Supported input

Place UTF-8 `.md` or `.txt` policy files directly inside one folder. Subfolders are
not scanned. Policies need numbered Markdown headings, even when the extension is `.txt`.

```markdown
# Leave Policy

Effective date: 2026-01-01

## 1 Scope
This policy covers full-time employees.

## 2 Paid leave

### 2.1 Annual paid leave
Full-time employees earn 20 days of paid leave per calendar year.
```

This example is fictional. Preserve the numbering and wording in real source
documents; ask for a numbered version when headings are missing.

## Parsing conventions

| Element | Convention |
| --- | --- |
| Document title | A `# Title` heading before the first numbered section; defaults to the filename stem. |
| Section heading | Markdown levels 2–6 followed by a number and heading text, such as `## 2 Paid leave` or `### 2.1 Annual paid leave`. |
| Section ID | Filename plus section number, for example `leave.md#2.1`. Numbers must be unique within each file. |
| Section body | Text after a numbered heading and before the next numbered heading. |
| Effective date | `Effective date: YYYY-MM-DD` in the preamble; absent dates are recorded as `null`. |
| Superseded policy | Literal uppercase `SUPERSEDED` anywhere before the first numbered section. |

An effective date is metadata; it does not automatically select the newest policy.
Use the superseded marker to exclude outdated documents from normal retrieval.

## Historical policies

Mark an old policy in its preamble:

```markdown
# Leave Policy (previous version)

SUPERSEDED
Effective date: 2024-01-01

## 1 Scope
Previous policy text goes here.
```

Normal retrieval excludes its sections. Use `--include-superseded` only when
answering a question about previous policy, and label historical evidence clearly.

## Evidence rules

- Cite a section ID and copy the supporting quote exactly from its body text.
- Check role, employment type, location, dates, and exceptions before applying a rule.
- Retrieve evidence from both documents when a question combines policies.
- Say the policies do not cover the question when the required evidence is absent.

The [fictional evaluation corpus](../../../evals/corpus/) contains complete input
examples. It is test material, not a source of real company policy.
