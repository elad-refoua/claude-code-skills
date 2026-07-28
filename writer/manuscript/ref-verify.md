# Reference Verification (Double Control)

Verify ALL references for factual accuracy using two independent rounds of web search.

**Trigger keywords**: "verify references", "check references accuracy", "reference verification", "export to zotero", "ris file"

---

## Architecture

```
Python extraction → JSON + RIS + Excel → Sonnet Round 1 → Excel update → Sonnet Round 2 → Excel update → Final summary
```

## Outputs
- **Excel table**: all parsed APA fields + verification status from both agents
- **RIS file**: Zotero/Mendeley/EndNote import
- **Summary**: issues found with double-control agreement

## Pipeline (9 Steps)

### Step 1: Get file path

### Step 2: Run extraction script
```bash
py "<SET_YOUR_PATH>/skills/ref-verify/ref_verify.py" "<DOCX_PATH>"
```
Outputs: `_REFS_TO_VERIFY.json`, `_REFS.ris`, `_REFS.xlsx`

### Step 3: Read JSON, prepare batches

### Step 4: ROUND 1 — Spawn Sonnet sub-agents (one per batch)
Task tool: `subagent_type: "general-purpose"`, `model: "sonnet"`, `run_in_background: true`
Max 3 parallel. Each verifies: authors, year, title, journal, volume, issue, pages, DOI.

### Step 5: Collect Round 1, update Excel
```bash
py ref_verify.py --update-excel "<paper>_REFS.xlsx" "<paper>_AGENT1_FINDINGS.json" --agent 1
```

### Step 6: ROUND 2 — Spawn SECOND set of Sonnet sub-agents
Different prompt emphasizing: original vs reprint year, all author initials, chapter book titles, correct publisher edition.

### Step 7: Collect Round 2, update Excel
```bash
py ref_verify.py --update-excel "<paper>_REFS.xlsx" "<paper>_AGENT2_FINDINGS.json" --agent 2
```
Computes Final Status: Both agree → shared status. Either ERROR → ERROR. Disagreement → REVIEW.

### Step 8: Apply fixes as tracked changes (optional)
Use OOXML tracked changes on document. Items needing author decision get bubble comments instead.

### Step 9: Present final summary
Show issues table (where Final ≠ CORRECT), clean count, classify by agreement level.

## Excel Columns
#, Authors, Year, Title, Type, Journal, Volume, Issue, Pages, Publisher, Editors, Edition, DOI, Full APA Text, Agent 1 Status, Agent 1 Issues, Agent 2 Status, Agent 2 Issues, Final Status

## Why Double Control?
- Catch errors one agent missed
- Confirm real issues (both flag same problem)
- Identify ambiguous cases (agents disagree → manual review)
