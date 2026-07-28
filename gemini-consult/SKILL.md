---
name: gemini-consult
description: "Consult with Gemini 3 Pro about your writing. Use for: writing feedback, style review, academic writing, Hebrew text editing."
user-invocable: true
---

# Gemini Consultant

Get a second opinion from Gemini 3 Pro.

## IMPORTANT: Only When Requested

Do NOT use this skill automatically. Only consult Gemini when the user EXPLICITLY asks:
- "תשאל את ג'מיני"
- "מה ג'מיני חושב?"
- "תתייעץ עם ג'מיני"
- "/gemini-consult"
- "ask Gemini"
- "consult Gemini"

## Workflow

When the user explicitly requests Gemini:

1. **I (Claude) analyze** what help the user needs
2. **I formulate** a focused, specific question for Gemini
3. **I run** the script and show both what I asked and what Gemini answered

## My Role

I don't just pass through the user's text. I:
- Understand the context and goal
- Decide what specific feedback would help
- Craft a targeted question for Gemini

## CRITICAL: Always Show Full Exchange

After running the script, I MUST show the user:
1. **What I sent to Gemini** (the exact prompt)
2. **What Gemini answered** (the full response)

The script outputs both - I present them clearly to the user. Never summarize or hide parts of the exchange.

## Command

```bash
cd ~/.claude/skills/gemini-consult/scripts && npx tsx consult.ts --profile [--hebrew] [--type TYPE] "MY FOCUSED QUESTION" --text "RELEVANT CONTEXT"
```

## Example Workflow

**User:** "מה דעתך על המשפט הזה: המחקר בוחן חרדה"

**My analysis:** User wants feedback on academic Hebrew writing. The sentence is short and might need expansion.

**What I ask Gemini:**
```bash
npx tsx consult.ts --profile --hebrew --type academic "האם המשפט הזה מספיק ספציפי לכתיבה אקדמית? מה חסר?" --text "המחקר בוחן חרדה"
```

**Then I show:** What I sent + Gemini's response

## Flags

| Flag | Use when |
|------|----------|
| `--profile` | Always (includes Elad's context) |
| `--hebrew` | Hebrew text |
| `--type academic` | Academic writing |
| `--type ideas` | Need ideas/brainstorming |
| `--type process` | Workflow review |
| `--type review` | Comprehensive feedback |
| `--brief` | Quick answer needed |
| `--file PATH` | Read context from a file instead of `--text` |

## Manuscript Review Pattern (Proven Workflow)

When using Gemini to review a full manuscript:

### 1. Extract clean text first
Use `read-docx` to extract visible text (including tracked-change insertions, excluding deletions) to a temp file.

### 2. Send with `--file` flag
```bash
cd ~/.claude/skills/gemini-consult/scripts && npx tsx consult.ts --profile --type review --file "path/to/extracted_text.txt" "REVIEW PROMPT HERE"
```

### 3. Embed feedback as Word comments (CRITICAL)
**Do NOT just show Gemini's response as text.** Always embed it as bubble comments on the manuscript:
- Author: `"Gemini Review"` (will appear as separate color-coded stream in Word)
- Anchor each comment to the specific text it critiques using `find_runs_containing()`
- Use `doc.add_comment(runs=runs, text=comment_text, author="Gemini Review")`

### 4. Comment format
Prefix each comment with severity:
- `GEMINI MAJOR #N (Topic):` for issues that could warrant rejection
- `GEMINI LINE:` for specific sentence-level concerns
- `GEMINI MINOR:` for fixable but non-blocking issues

### Example review prompt for TICS-level journal:
```
You are acting as a TOUGH but FAIR external reviewer for [JOURNAL] (IF ~[X]).
Review this manuscript with the rigor expected at this level.
DO NOT be polite - be honest and critical.
Structure: (1) MAJOR ISSUES (2) MINOR ISSUES (3) LINE-LEVEL CONCERNS (4) VERDICT
```

### Python pattern for adding comments:
```python
from docx import Document
AUTHOR = "Gemini Review"

def find_runs_containing(para, search_text):
    runs = para.runs
    if not runs: return []
    cum_text = ''
    run_spans = []
    for run in runs:
        start = len(cum_text)
        cum_text += run.text
        run_spans.append((start, len(cum_text), run))
    idx = cum_text.find(search_text)
    if idx < 0: return list(runs)[:3]
    end_idx = idx + len(search_text)
    return [r for s, e, r in run_spans if s < end_idx and e > idx] or list(runs)[:3]

doc = Document("manuscript.docx")
para = doc.paragraphs[N]
runs = find_runs_containing(para, "target text")
doc.add_comment(runs=runs, text="GEMINI MAJOR #1: ...", author=AUTHOR)
doc.save("manuscript.docx")
```
