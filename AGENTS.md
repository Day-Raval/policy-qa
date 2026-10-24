# Agent instructions

This repository contains one agent skill: `skills/policy-qa/`.

If your agent does not load SKILL.md skills automatically and the user asks what their company policy documents say, allow, require or cover:
1. Read `skills/policy-qa/SKILL.md` and follow its procedure exactly, including the citation check before every reply.
2. Resolve its `scripts/` and `references/` paths relative to `skills/policy-qa/`.
3. Never read `evals/` while answering: it holds the test questions and their answers.
4. Give no legal opinion: the skill only reports what the policies say.

For any other request, ignore this file.
