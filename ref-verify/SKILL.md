---
name: ref-verify
description: |
  Verify all references in an academic paper (.docx) for accuracy via web search.
  Spawns TWO rounds of Sonnet sub-agents (double control) to independently verify
  each reference against online sources. Produces a detailed Excel table,
  a Zotero-compatible RIS file, and a summary of issues found.

  TRIGGERS: "verify references", "check references accuracy", "תוודא הפניות",
  "בדוק הפניות", "reference verification", "are the references correct",
  "verify all refs", "export to zotero", "ris file", "zotero export"
---

# Reference Verification Skill (Double Control)

Verify every reference in an academic paper for factual accuracy using **two independent rounds** of web search sub-agents (double control). Produces:
- **Excel table** with all parsed APA fields + verification status from both agents
- **RIS file** for Zotero/Mendeley/EndNote import
- **Summary table** of issues found

**Architecture**: Python extraction → JSON + RIS + Excel → Sonnet sub-agents (Round 1) → update Excel → Sonnet sub-agents (Round 2) → update Excel → final summary

## How to Run — Follow These Steps Exactly

### Step 1: Get the file path

Ask the user for the .docx file path if not provided. Look in the current working directory for .docx files if needed.

### Step 2: Run the extraction script

```bash
py "C:/Users/user/.claude/skills/ref-verify/ref_verify.py" "<DOCX_PATH>"
```

This produces THREE files:
- `<paper>_REFS_TO_VERIFY.json` — batched references for sub-agents
- `<paper>_REFS.ris` — Zotero/Mendeley/EndNote import file
- `<paper>_REFS.xlsx` — detailed Excel table with all parsed fields + verification columns

Options: `--batch-size N` (default 10), `--ris-only` (skip JSON/Excel)

### Step 3: Read the JSON and prepare batches

Read `_REFS_TO_VERIFY.json` using the Read tool. Extract:
- `batches[]` — each has `batch_num`, `ref_start`, `ref_end`, `references[]`
- Each reference has `num`, `label`, `text`

### Step 4: ROUND 1 — Spawn Sonnet sub-agents (one per batch)

**YOU MUST DO THIS.** For each batch in the JSON, spawn a Sonnet sub-agent using the Task tool. This is the first verification pass.

```
Task tool parameters:
  description: "Verify refs {ref_start}-{ref_end} accuracy"
  subagent_type: general-purpose
  model: sonnet
  run_in_background: true
```

**Sub-agent prompt** — build this for each batch by inserting the actual references:

```
You are a reference verification agent (Round 1). For each of the academic
references below, search the web to verify that the reference is ACCURATE —
correct authors, year, title, journal/publisher, volume, issue, pages, and DOI.
Report any errors you find.

For each reference, output a JSON array of objects with these exact fields:
- "ref_num": [the reference number]
- "status": "CORRECT" / "ERROR" / "UNVERIFIABLE"
- "issues": "" if CORRECT, otherwise describe what's wrong and the correct value

Example output:
[
  {"ref_num": 1, "status": "CORRECT", "issues": ""},
  {"ref_num": 2, "status": "ERROR", "issues": "Year should be 1976, not 1979. Publisher is IUP, not Penguin."},
  {"ref_num": 3, "status": "UNVERIFIABLE", "issues": "No book found with this title/publisher online."}
]

Here are the references to verify:

REF{num}: {full reference text}
REF{num}: {full reference text}
...

Search the web for EACH reference individually. Be thorough — check every field.
Output ONLY the JSON array, no other text.
```

**Concurrency rules:**
- Launch up to 3 sub-agents in parallel (max concurrent agents limit)
- As each sub-agent completes, launch the next queued batch
- Track progress: show the user which batches are running, done, and queued

### Step 5: Collect Round 1 results and update Excel

As each sub-agent returns:
1. Parse the JSON array from its result
2. Merge all batch results into one `_AGENT1_FINDINGS.json` file
3. Run the Excel updater:

```bash
py "C:/Users/user/.claude/skills/ref-verify/ref_verify.py" --update-excel "<paper>_REFS.xlsx" "<paper>_AGENT1_FINDINGS.json" --agent 1
```

This fills in the "Agent 1 Status" and "Agent 1 Issues" columns in the Excel.

### Step 6: ROUND 2 — Spawn a SECOND set of Sonnet sub-agents (double control)

**YOU MUST DO THIS.** This is the independent second verification pass for double control. Spawn new sub-agents with a slightly different prompt to ensure independent verification:

```
You are a reference verification agent (Round 2 — independent double-check).
For each of the academic references below, search the web INDEPENDENTLY to verify
accuracy. Check: authors (all of them, correct initials), year (original vs reprint),
title (exact wording), journal/publisher, volume, issue, pages, DOI.

Pay special attention to:
- Original publication year vs. reprint/translation year
- Correct publisher for the specific edition cited
- All author initials (not just surname)
- Chapter references: verify the book title AND editors

For each reference, output a JSON array:
[
  {"ref_num": 1, "status": "CORRECT", "issues": ""},
  {"ref_num": 2, "status": "ERROR", "issues": "Specific description of what's wrong"}
]

References to verify:

REF{num}: {full reference text}
...

Search the web for EACH reference. Output ONLY the JSON array.
```

Same concurrency rules as Round 1.

### Step 7: Collect Round 2 results and update Excel

1. Merge Round 2 results into `_AGENT2_FINDINGS.json`
2. Update Excel:

```bash
py "C:/Users/user/.claude/skills/ref-verify/ref_verify.py" --update-excel "<paper>_REFS.xlsx" "<paper>_AGENT2_FINDINGS.json" --agent 2
```

This fills "Agent 2 Status" / "Agent 2 Issues" columns AND computes the "Final Status":
- Both agree → Final = their shared status
- Either says ERROR → Final = ERROR
- Disagreement → Final = REVIEW (needs manual check)

### Step 8: Present final summary table

When ALL agents are done, present a complete summary:

**First, show only the issues (where Final Status is not CORRECT):**

```markdown
## Issues Found (Double Control)

| # | Reference | Agent 1 | Agent 2 | Final | Issue |
|---|-----------|---------|---------|-------|-------|
| 3 | Beck (1979) | ERROR | ERROR | ERROR | Year should be 1976, publisher IUP |
| 13 | Ferenczi (1932) | ERROR | ERROR | ERROR | Published 1988, not 1932 |
| 54 | Rachman (1972) | UNVERIFIABLE | UNVERIFIABLE | REVIEW | No book found |
| 60 | Shephard (2001) | CORRECT | ERROR | ERROR | Agent 2 found publisher discrepancy |
```

**Then the clean count:**
```
Double-control verified: 66 of 74 correct (both agents agree).
Issues requiring attention: 8
```

**Classify issues by agreement:**
1. **Both agree ERROR** — high confidence there's a real mistake
2. **Both agree UNVERIFIABLE** — reference genuinely hard to find online
3. **Agents disagree** — needs manual review, one agent may have found something the other missed

### Step 9: Mention output files

Tell the user:
> **Excel**: `<paper>_REFS.xlsx` — detailed table with all fields + both verification rounds + final status
> **RIS**: `<paper>_REFS.ris` — ready to import into Zotero: **File → Import → select the .ris file**

## Excel Table Columns

| Column | Content |
|--------|---------|
| # | Reference number |
| Authors | Parsed author names |
| Year | Publication year |
| Title | Work title |
| Type | journal / book / chapter / edited_book |
| Journal | Journal name (if applicable) |
| Volume, Issue, Pages | Journal details |
| Publisher | Publisher name |
| Editors | Editor names (for chapters/edited books) |
| Edition | Edition info |
| DOI | Digital Object Identifier |
| Full APA Text | Original reference text |
| Agent 1 Status | CORRECT / ERROR / UNVERIFIABLE |
| Agent 1 Issues | Details from first verification round |
| Agent 2 Status | CORRECT / ERROR / UNVERIFIABLE |
| Agent 2 Issues | Details from second verification round |
| Final Status | CORRECT / ERROR / REVIEW (computed after both rounds) |

## Why Double Control?

Single-agent verification can miss issues or produce false positives. Two independent rounds:
- Catch errors one agent missed
- Confirm real issues (both agents flag the same problem)
- Identify ambiguous cases (agents disagree → manual review)

## Example Session

User: "verify references in my paper"

1. Identify the .docx file
2. Run `py ref_verify.py "paper.docx"` → 74 refs → JSON + RIS + Excel
3. Read JSON → 8 batches of 10
4. **Round 1**: Spawn batches 1-3 in parallel, then 4-6, then 7-8
5. Collect Round 1 results → save `_AGENT1_FINDINGS.json` → update Excel (agent 1)
6. **Round 2**: Spawn batches 1-3 in parallel (different prompt), then 4-6, then 7-8
7. Collect Round 2 results → save `_AGENT2_FINDINGS.json` → update Excel (agent 2)
8. Excel now has Final Status computed
9. Show double-control summary: "8 issues found, both agents agreed on 6, 2 need review"
10. Mention Excel + RIS files
