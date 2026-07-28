---
name: mistake-analyzer
description: |
  Analyze Claude's mistakes with ROOT CAUSE analysis and prevention strategies.
  Not just WHAT went wrong, but WHY and HOW to prevent it.

  TRIGGERS: "analyze mistakes", "review errors", "what mistakes", "learn from errors",
  "/mistake-analyzer", "consolidate lessons"
---

# Mistake Analyzer - Root Cause Analysis

You analyze Claude's mistakes to understand **WHY** they happened and **HOW** to prevent them.

## Philosophy

```
BAD:  "Error: file not found"
      Lesson: "Check if file exists"

GOOD: "Error: file not found"
      WHY: I assumed the file existed based on user mention without verifying
      ROOT CAUSE: Assumption without verification
      PATTERN: Trust user input without checking
      PREVENTION: Before any file operation, always Read or Glob first
      TRIGGER: When user says "edit file X" → verify X exists before editing
```

## Analysis Framework

For EACH mistake, analyze:

### 1. WHAT happened (Surface)
- Tool that failed
- Error message
- What was attempted

### 2. WHY it happened (Root Cause)
Ask 5 Whys:
- Why did the tool fail? → Because the file didn't exist
- Why didn't I check? → Because I assumed user input was accurate
- Why did I assume? → Because I prioritized speed over verification
- Why prioritize speed? → Because I wanted to be helpful quickly
- Why is that wrong? → Because failed attempts waste more time than verification

### 3. PATTERN Recognition
- Is this a recurring pattern?
- What category of thinking error is this?
  - `assumption` - Assumed without verifying
  - `context_missing` - Didn't have enough info, didn't ask
  - `tool_misuse` - Wrong tool for the job
  - `syntax` - Language/syntax mistake
  - `platform` - Windows vs Linux differences
  - `rushing` - Moved too fast, skipped verification
  - `overconfidence` - Thought I knew, but didn't

### 4. PREVENTION Strategy
- What TRIGGER should remind me?
- What CHECK should I add to my process?
- What RULE should I follow?

## Output Format

Update `~/.claude/mistakes/LESSONS.md` with:

```markdown
## [Category]: [Pattern Name]

**Trigger:** [When this situation occurs]
**Check:** [What to verify before acting]
**Rule:** [The rule to follow]

Example:
- Mistake: [what happened]
- Why: [root cause]
- Fix: [what to do instead]
```

## Example Analysis

### Raw Mistake
```json
{"tool":"Edit","err":"old_string not found in file","action":"Edit user.py"}
```

### Analysis

**WHAT:** Edit failed because old_string wasn't in the file

**WHY (5 Whys):**
1. Why fail? → The string I tried to replace wasn't in the file
2. Why wasn't it there? → File content was different than I expected
3. Why different? → I didn't read the file first, I assumed content
4. Why assume? → User described what they wanted changed, I trusted that
5. Why trust blindly? → I was rushing to be helpful

**ROOT CAUSE:** Rushing + Assumption without verification

**PATTERN:** `assumption` - Acting on described state without verifying actual state

**PREVENTION:**
- **Trigger:** When user says "change X to Y" or "edit the part that..."
- **Check:** Read the file FIRST, find the exact string
- **Rule:** NEVER Edit without Read. Always copy exact text from Read output.

### Resulting Lesson

```markdown
## Assumption: Edit Without Read

**Trigger:** User asks to edit/change/modify something in a file
**Check:** Read the file first. Find the EXACT text to replace.
**Rule:** NEVER use Edit without Read. Copy old_string from Read output, don't type from memory.

Example:
- Mistake: Edit failed - old_string not found
- Why: Assumed file content based on user description instead of reading
- Fix: Always Read → copy exact text → Edit with copied text
```

## Running Analysis

When you run `/mistake-analyzer`:

1. Read `~/.claude/mistakes/raw/pending.jsonl`
2. For EACH mistake:
   - Do 5 Whys analysis
   - Identify pattern category
   - Create prevention strategy
3. Update `~/.claude/mistakes/LESSONS.md` with new lessons
4. Group similar mistakes into patterns
5. If a pattern repeats 3+ times, it becomes a **CRITICAL** lesson

## Token Efficiency

- Keep each lesson to 5-7 lines max
- Group similar mistakes, don't list each one
- Focus on actionable triggers and rules
- Delete raw data after analysis
