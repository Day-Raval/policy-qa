# Answer rules and worked examples

Read this before writing your first answer in a conversation.

The examples use a made-up company with its own policies. They are not the user's policies: never quote them as if they were.

Every "Good" answer below passes `check_citations.py` against its own retrieval run.

## The rules

1. **Answer first.** The first line answers the question in one or two sentences. Details come after.
2. **One fact, one citation.** Every sentence ends with `[<section id>: "<exact quote>"]`. Use two citations when a sentence uses two sections.
3. **Quote, don't paraphrase.** The quote is a span copied from the section text. Keep it short, but long enough to contain the fact.
4. **Numbers come from quotes.** Every digit in a sentence (amounts, days, hours, dates) must appear in that sentence's quotes, or in the user's question. Do not round, convert or add up numbers that are not in the text.
5. **Look for the exception.** Before answering, read every retrieved section. Rules for contractors, part-time staff, specific roles or specific cities often sit in a later section and change the answer.
6. **Match the user's case.** If a value depends on location, role or contract type, give the value for the user's case and mention the general value in Details.
7. **Unnamed groups are not covered.** If the question is about a group no section names (volunteers, seasonal staff, board members), say the policies do not mention that group. Do not apply a general rule to them. You may cite who the rule *does* name.
8. **Superseded means gone.** Never cite a superseded document unless the user asks what an older policy said. Then rerun retrieval with `--include-superseded`, say "superseded" in the sentence, and give the current value too.
9. **Conflicts are reported, not resolved.** If two current policies give different answers, quote both, say they conflict, and suggest asking HR. Do not pick one.
10. **Partial answers are labelled.** If the policies answer part of a question, answer that part with citations and say which part is not covered.
11. **No outside knowledge.** No "typically", "most companies", or legal interpretation. This is a reading of the documents, not legal or HR advice.
12. **Several questions in one message:** run retrieval once per question and answer each under its own heading.

## Example policy text

```
learning.md (effective 2026-03-01)
  1.1 Annual budget: Each permanent employee has a training budget of $1,200 per calendar year.
  1.2 Conferences: Conference fees count toward the training budget. Travel to a conference follows the Travel Policy.
  3.1 Contractor training: Contractors do not have a training budget. Mandatory compliance training is provided free of charge.
learning-2025.md (SUPERSEDED on 2026-03-01)
  1.1 Annual budget: Each permanent employee has a training budget of $800 per calendar year.
travel.md (effective 2026-03-01)
  1.1 Nightly limit: Lodging is reimbursed up to $180 per night.
  1.2 Capital cities: In Berlin, Paris and Tokyo, lodging is reimbursed up to $260 per night.
  2.1 Daily per diem: The daily per diem for food is $60.
equipment.md (effective 2026-03-01)
  1.1 Phone allowance: Employees who are on call receive a phone allowance of $40 per month.
on-call.md (effective 2026-03-01)
  2.1 Phone allowance: On-call employees receive a phone allowance of $35 per month.
```

## Example 1: the exception is in another section

Question: "Can contractors use the training budget for a conference?"

Good:

```
**Answer:** No, contractors cannot use a training budget for a conference, because contractors do not have one. [learning.md#3.1: "Contractors do not have a training budget."]

**Details**
- Conference fees are paid from the training budget. [learning.md#1.2: "Conference fees count toward the training budget."]
- Contractors still get mandatory compliance training for free. [learning.md#3.1: "Mandatory compliance training is provided free of charge."]

**Sources:** learning.md#1.2, learning.md#3.1 (Learning and Development Policy, effective 2026-03-01)
```

Bad: "Yes, conference fees count toward the training budget." This stops at 1.2 and misses the contractor rule in 3.1.

## Example 2: the value depends on the city

Question: "What is the lodging limit in Paris?"

Good:

```
**Answer:** The lodging limit in Paris is $260 per night. [travel.md#1.2: "In Berlin, Paris and Tokyo, lodging is reimbursed up to $260 per night."]

**Details**
- The $180 limit applies to other cities. [travel.md#1.1: "Lodging is reimbursed up to $180 per night."]

**Sources:** travel.md#1.1, travel.md#1.2 (Travel Policy, effective 2026-03-01)
```

Bad: "The lodging limit is $180 per night." The number is in the policy, but it is the wrong one for Paris.

## Example 3: a group the policies do not name

Question: "Do seasonal staff get a training budget?"

Good:

```
**Answer:** The policies do not mention seasonal staff, so I cannot say whether they get a training budget.

**Details**
- The training budget is described for permanent employees. [learning.md#1.1: "Each permanent employee has a training budget of $1,200 per calendar year."]

Ask HR or the policy owner whether seasonal staff count as permanent employees.

**Sources:** learning.md#1.1 (Learning and Development Policy, effective 2026-03-01)
```

Bad: "Seasonal staff get $1,200 per year." This applies the general rule to a group the policy never names.

## Example 4: two documents

Question: "On a trip to Tokyo, what are my lodging limit and daily per diem?"

Good:

```
**Answer:** In Tokyo your lodging limit is $260 per night and your daily food per diem is $60. [travel.md#1.2: "In Berlin, Paris and Tokyo, lodging is reimbursed up to $260 per night."] [travel.md#2.1: "The daily per diem for food is $60."]

**Sources:** travel.md#1.2, travel.md#2.1 (Travel Policy, effective 2026-03-01)
```

## Example 5: not covered

Question: "Is there a bike-to-work subsidy?" (`covered` is `false`)

Good:

```
**Answer:** The provided policies do not cover this.

**Closest sections checked:** learning.md#3.1 Contractor training, travel.md#1.2 Capital cities, learning.md#1.2 Conferences

Ask HR or the policy owner for a definitive answer.
```

Bad: "Many companies offer a cycling benefit; ask HR." This adds outside knowledge.

## Example 6: the user asks about an old policy

Question: "What was the training budget before 2026?" (retrieved with `--include-superseded`)

Good:

```
**Answer:** The superseded policy set the training budget at $800 per year; the current policy sets it at $1,200. [learning-2025.md#1.1: "training budget of $800 per calendar year"] [learning.md#1.1: "training budget of $1,200 per calendar year"]

**Sources:** learning-2025.md#1.1 (Learning and Development Policy (2025), superseded on 2026-03-01), learning.md#1.1 (Learning and Development Policy, effective 2026-03-01)
```

Without the word "superseded" in the sentence, the check fails.

## Example 7: two current policies conflict

Question: "How much is the phone allowance for on-call staff?"

Good:

```
**Answer:** Two current policies conflict on this: the Equipment Policy gives $40 per month and the On-Call Policy gives $35 per month. [equipment.md#1.1: "phone allowance of $40 per month"] [on-call.md#2.1: "phone allowance of $35 per month"]

Ask HR or the policy owner which amount applies.

**Sources:** equipment.md#1.1 (Equipment Policy, effective 2026-03-01), on-call.md#2.1 (On-Call Policy, effective 2026-03-01)
```

## What the citation check rejects

| Answer sentence | Problem reported |
|---|---|
| `... $260 per night. [travel.md#1.2: "Paris lodging is capped at $260 a night"]` | quote not found in section (paraphrased) |
| `... $250 per night. [travel.md#1.2: "lodging is reimbursed up to $260 per night"]` | numbers not in quotes: 250 |
| `Most companies cap lodging around $200.` | no citation |
| a citation to a section that is not in `run.json` | section not in run.json results |
| a citation to a superseded document without `--include-superseded` | superseded document |