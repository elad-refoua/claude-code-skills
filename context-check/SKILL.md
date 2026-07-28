---
name: context-check
description: "Gather project context before starting complex work. Use when beginning a multi-step task, switching projects, or when the request scope is unclear. Triggers: 'context check', 'start working on', 'new task', 'help me with a project'."
---

# Context Check - Verify Scope Before Acting

When invoked, gather these 4 pieces of context BEFORE doing any work.
Use AskUserQuestion to ask all questions efficiently in one prompt.

## Step 1: Identify the Project

- Confirm the current working directory is correct for this task
- Read the project's CLAUDE.md if it exists
- If no CLAUDE.md, ask: "One-line description of this project?"

## Step 2: Clarify the Specific Goal

Ask: **"What's the specific outcome you want?"**

Guide by task type:
- **R analysis:** Which variables? Which statistical tests? Which comparison groups?
- **Manuscript work:** Which section? Drafting new or revising existing? Which reviewer comments?
- **Data work:** Which data file (exact path)? Which subset of rows/columns?
- **Simulation:** Which bot prompt? Which scenarios? How many runs?
- **Code fix:** What's broken? What's the expected behavior?

Do NOT accept vague answers like "analyze the results" — ask for specifics.

## Step 3: Locate Source Files

Ask: **"Which files should I work with?"**

Then READ every source file mentioned before starting work:
- Data files (.csv, .sav, .RData) — verify columns exist
- Papers (.docx, .pdf) — verify content matches what user described
- Scripts (.R, .py) — verify current state before modifying
- Questionnaires/instruments — verify exact item wordings

**CRITICAL:** If the user references a questionnaire or instrument by name (e.g., "ECR-AI", "PHQ-9"), locate and READ the actual file. Never quote items from memory.

## Step 4: Define Expected Output

Ask: **"What should exist when this is done?"**

Clarify:
- **Format:** R script + Results.md? Word document? HTML? PowerPoint?
- **Location:** Same folder? New dated output folder?
- **Language:** Hebrew or English? (default: ask)
- **Scope:** Just this analysis, or a full pipeline with narrative?

## Step 5: Save Context Summary

Write a brief `_context.md` file in the working directory:

```markdown
# Session Context
- **Project:** [name]
- **Goal:** [specific outcome]
- **Source files:** [paths]
- **Output:** [format, location, language]
- **Date:** [today]
```

This file prevents context loss during long sessions. Delete it when the task is complete.

## Rules

- Do NOT proceed with any work until all 4 questions are answered
- If the user gives a vague answer, ask for specifics — don't guess
- READ every source file BEFORE starting analysis or writing
- This skill complements CLAUDE.md verification rules — it doesn't replace them
