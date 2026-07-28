---
name: ai-prompting-optimizer
description: >
  Improve prompts before sending them to any AI tool.
  Applies the 10 practical prompting principles: role, task, context, materials,
  iterate, alternatives, verify, clarify, practical output, ethics.
  Use when crafting or reviewing prompts for ChatGPT, Gemini, Claude, or any LLM.
skills:
  - ai-thinking-framework
triggers:
  - optimize prompt
  - improve prompt
  - review my prompt
  - better prompt
  - prompt check
  - שפר פרומפט
  - תבדוק את הפרומפט
---

# Prompt Optimizer

Evaluate and improve prompts using the 10 practical principles from the AI Thinking Framework.

## When Triggered

When the user shares a prompt they want to send to an AI tool, or asks you to help craft one.

## Process

### Step 1: Score the prompt (1-5) on each principle

| # | Principle | Check |
|---|-----------|-------|
| P1 | Role & Style | Does it specify WHO the AI should be and what tone to use? |
| P2 | Task & Output | Is the task explicit? Is the expected output format defined? |
| P3 | Rich Context | Does it include background, goals, population, methodology? |
| P4 | Reference Materials | Are relevant documents, examples, or data attached/referenced? |
| P5 | Iterate & Refine | Is this part of an iterative process, or a one-shot attempt? |
| P6 | Alternatives | Does it ask for multiple approaches or just one? |
| P7 | Verify & Validate | Does it ask the AI to explain reasoning, cite sources, flag uncertainty? |
| P8 | Clarifying Questions | Does it invite the AI to ask questions before starting? |
| P9 | Practical Application | Is the output format matched to how it will actually be used? |
| P10 | Ethical Guardrails | Is sensitive data protected? Is AI role bounded appropriately? |

### Step 2: Identify the 2-3 weakest areas

Focus on what would make the biggest difference. Don't nitpick everything.

### Step 3: Suggest specific improvements

For each weak area, provide:
- **What's missing** (one sentence)
- **Suggested addition** (exact text to add to the prompt)

### Step 4: Offer a rewritten version

Present the improved prompt in a copyable format. Keep the user's voice and intent — just fill the gaps.

## Context Engineering Check

Beyond the 10 principles, verify the super-principle:

1. **Context** — Is the domain, question, and background clear?
2. **Constraints** — Are limits stated (time, scope, methodology, ethics)?
3. **Goal** — Is the final product defined (format, audience, purpose)?

If any pillar is missing, flag it.

## Output Format

```
## Prompt Score

| Principle | Score | Note |
|-----------|-------|------|
| P1 Role   | 4/5   | Good — specified "statistician" |
| P2 Task   | 2/5   | Vague — no output format specified |
| ...       |       |      |

## Top Improvements
1. [Principle]: [What to add]
2. [Principle]: [What to add]

## Improved Prompt
[Full rewritten prompt, ready to copy]
```

## Common Patterns

**Academic prompts** — usually missing P3 (context) and P4 (reference materials). Researchers assume the AI "knows" their field.

**Code prompts** — usually missing P2 (expected output format) and P9 (practical application). "Write code for X" without specifying language, framework, or how the output will be used.

**Writing prompts** — usually missing P1 (role/style) and P6 (alternatives). "Write about X" without tone guidance or requesting multiple drafts.

**Analysis prompts** — usually missing P3 (context about data structure) and P7 (verification). Sending data without a variable dictionary or asking AI to explain its choices.
