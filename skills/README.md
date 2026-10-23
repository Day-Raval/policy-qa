# Skills

Agent skills for answering questions from company policy documents.

## Available skills

| Skill | Use it for | Runtime |
| --- | --- | --- |
| [Policy Q&A](policy-qa/) | Find policy evidence, check exceptions, and write answers with exact section quotes. | Python 3.9+; standard library only |

## Start here

1. Read the [Policy Q&A overview](policy-qa/) for capabilities and a runnable example.
2. Follow the [agent instructions](../SKILL.md) when answering policy questions.
3. Prepare documents using the [policy format guide](policy-qa/references/).

## Repository layout

```text
skills/
|-- README.md
`-- policy-qa/
    |-- README.md
    |-- references/     Policy format and evidence conventions
    `-- scripts/        Indexing, retrieval, and regression tests
```

The executable agent instructions currently live in the repository-root
[`SKILL.md`](../SKILL.md). Keep the repository together when using these guides;
the nested skill folder alone does not include those instructions or the evaluation fixtures.
