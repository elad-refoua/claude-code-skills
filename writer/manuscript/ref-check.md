# Reference Checker

Cross-references every in-text citation against the reference list in an academic paper (.docx).

**Trigger keywords**: "check references", "cross-reference citations", "ref check", "reference audit", "בדוק הפניות"

---

## Architecture

```
Python (regex + highlighting) → JSON output → Sonnet sub-agent (independent extraction) → Opus sub-agent (verification)
```

## Color Coding

| Location | Color | Meaning |
|----------|-------|---------|
| Body text | **Green** | Citation exactly matches a reference |
| Body text | **Cyan** | Citation fuzzy-matches a reference |
| Body text | **Yellow** | Citation NOT found in references |
| References | **Green** | Reference IS cited in text |
| References | **Cyan** | Reference fuzzy-matches a citation |
| References | **Red** | Reference NOT cited in text |

## Pipeline (9 Steps)

### Step 1: Get file path
Ask user for .docx path if not provided.

### Step 2: Run Python script
```bash
py "<SET_YOUR_PATH>/skills/ref-check/ref_check.py" "<INPUT_FILE_PATH>" --comments
```
Outputs: `_REF_CHECK.docx` (color-coded) + `_RESULTS.json` (data for sub-agents)

### Step 3: Read JSON output
Read `_RESULTS.json`. Extract: body_text, ref_text, matched/unmatched/fuzzy lists.

### Step 4: Spawn Sonnet sub-agent for independent extraction
Extract ALL in-text citations independently (catches what regex misses).
Task tool: `subagent_type: "general-purpose"`, `model: "sonnet"`

### Step 5: Compare Sonnet vs regex results
- Sonnet-only citations = regex missed these
- Merged set = union of both
- Rescue references from red if Sonnet found citations regex missed

### Step 6: Spawn Opus sub-agent for verification
Verify remaining unmatched items. Check for: missed citations, false positives, cross-matches, red verification, fuzzy match advice.

### Step 7: Report results
Show counts (green/cyan/yellow/red), Sonnet findings, Opus verification summary.

### Step 8: Add unified comments (optional)
```bash
py "<SET_YOUR_PATH>/skills/ref-check/ref_check.py" --add-comments "<filename>_REF_CHECK.docx" "<findings.json>"
```
Strips previous ref-check comments, merges factual status + Opus findings into ONE comment per item, mirrors cross-references.

### Step 9: Save learnings (optional)
```bash
py "<SET_YOUR_PATH>/skills/ref-check/ref_check.py" --save-learnings "<findings.json>"
```
Persists cross-matches and noise words for future runs.

## Notes
- Python script: no API keys needed
- Original file NEVER modified
- Install: `py -m pip install python-docx` (>= 1.1.2)
- Tables: citations in Word tables extracted automatically
- Self-learning system via `learned_patterns.json`
