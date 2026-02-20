# ref-verify

Verify every reference in an academic paper (.docx) for factual accuracy using **double-control** web search sub-agents. Also exports a detailed Excel table and a Zotero-compatible RIS file.

## What it does

1. **Extracts** all references from a Word document's References section
2. **Parses** each reference into structured APA fields (authors, year, title, journal, volume, pages, DOI, publisher)
3. **Generates** a detailed Excel table with all parsed fields + verification status columns
4. **Spawns Sonnet sub-agents** (Round 1) — batches of ~10, independently web-search each reference
5. **Spawns Sonnet sub-agents** (Round 2) — independent second verification pass (double control)
6. **Updates Excel** with results from both rounds + computed final status
7. **Reports** a double-control summary table: agreements, disagreements, issues found
8. **Exports a .ris file** importable by Zotero, Mendeley, EndNote

## Architecture

```
Python (extraction + parsing) → JSON batches → Sonnet sub-agents Round 1 (WebSearch)
                               → Excel table      → update with Round 1 results
                               → RIS file          → Sonnet sub-agents Round 2 (WebSearch)
                                                   → update with Round 2 results
                                                   → Final Status (agreement check)
```

- **Python script** handles everything deterministic: docx parsing, APA field extraction, Excel generation, RIS generation, Excel updating
- **Claude Code** orchestrates: reads JSON, spawns sub-agents (2 rounds), collects results, updates Excel, presents summary
- **No API keys needed** in the script — sub-agents use Claude Code's own tools

## Why Double Control?

Single-agent verification can miss issues or produce false positives. Two independent rounds:
- **Catch errors** one agent missed
- **Confirm real issues** (both agents flag the same problem)
- **Identify ambiguous cases** (agents disagree = manual review needed)

## Installation

Copy the `ref-verify` folder to `~/.claude/skills/`:

```bash
cp -r ref-verify ~/.claude/skills/
```

Or on Windows:
```powershell
Copy-Item -Recurse ref-verify "$env:USERPROFILE\.claude\skills\"
```

Requires: `python-docx` and `openpyxl` (`pip install python-docx openpyxl`)

## Usage

Say any of these to Claude Code:
- "verify references in my paper"
- "check if all references are accurate"
- "export references to zotero"

Or in Hebrew:
- "תוודא את ההפניות במאמר"
- "בדוק הפניות"

Claude Code will automatically:
1. Run the extraction script (generates JSON + RIS + Excel)
2. Spawn Sonnet sub-agents Round 1 (3 parallel, ~10 refs each)
3. Collect Round 1 results, update Excel
4. Spawn Sonnet sub-agents Round 2 (independent double-check)
5. Collect Round 2 results, update Excel with final status
6. Present a double-control summary table with issues found

## Output Example

```
## Issues Found (Double Control)

| # | Reference       | Agent 1     | Agent 2     | Final  | Issue                              |
|---|-----------------|-------------|-------------|--------|------------------------------------|
| 3 | Beck (1979)     | ERROR       | ERROR       | ERROR  | Year should be 1976, publisher IUP |
| 13| Ferenczi (1932) | ERROR       | ERROR       | ERROR  | Published 1988, not 1932           |
| 54| Rachman (1972)  | UNVERIFIABLE| UNVERIFIABLE| REVIEW | No book found                      |
| 60| Shephard (2000) | CORRECT     | ERROR       | ERROR  | Agent 2 found publisher issue      |

Double-control verified: 66 of 74 correct (both agents agree).
```

## Excel Table

The `.xlsx` file includes all parsed APA fields plus verification columns:

| Column | Content |
|--------|---------|
| Authors, Year, Title, Type | Parsed APA fields |
| Journal, Volume, Issue, Pages | Journal details |
| Publisher, Editors, Edition, DOI | Book/chapter details |
| Full APA Text | Original reference text |
| Agent 1 Status / Issues | First verification round |
| Agent 2 Status / Issues | Second verification round |
| Final Status | CORRECT / ERROR / REVIEW |

Color-coded: green = CORRECT, red = ERROR, yellow = UNVERIFIABLE/REVIEW.

## RIS Export

The `.ris` file can be imported into:
- **Zotero**: File -> Import -> select .ris file
- **Mendeley**: File -> Import -> select .ris file
- **EndNote**: File -> Import -> select .ris file

Each RIS entry includes the original APA text in the notes field for reference.

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Instructions for Claude Code (the skill definition) |
| `ref_verify.py` | Python extraction + parsing + Excel + RIS export script |
