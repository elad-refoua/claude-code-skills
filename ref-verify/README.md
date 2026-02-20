# ref-verify

Verify every reference in an academic paper (.docx) for factual accuracy using web search sub-agents. Also exports a Zotero-compatible RIS file.

## What it does

1. **Extracts** all references from a Word document's References section
2. **Parses** each reference into structured APA fields (authors, year, title, journal, volume, pages, DOI, publisher)
3. **Spawns Sonnet sub-agents** (batches of ~10) that independently web-search each reference to verify accuracy
4. **Reports** a summary table: CORRECT / ERROR / UNVERIFIABLE for every reference
5. **Exports a .ris file** importable by Zotero, Mendeley, EndNote

## Architecture

```
Python (extraction + parsing) → JSON batches → Sonnet sub-agents (WebSearch) → Summary table
                               → RIS file (Zotero export)
```

- **Python script** handles everything deterministic: docx parsing, APA field extraction, RIS generation
- **Claude Code** orchestrates: reads JSON, spawns sub-agents, collects results, presents summary
- **No API keys needed** in the script — sub-agents use Claude Code's own tools

## Installation

Copy the `ref-verify` folder to `~/.claude/skills/`:

```bash
cp -r ref-verify ~/.claude/skills/
```

Or on Windows:
```powershell
Copy-Item -Recurse ref-verify "$env:USERPROFILE\.claude\skills\"
```

Requires: `python-docx` (`pip install python-docx`)

## Usage

Say any of these to Claude Code:
- "verify references in my paper"
- "check if all references are accurate"
- "export references to zotero"

Or in Hebrew:
- "תוודא את ההפניות במאמר"
- "בדוק הפניות"

Claude Code will automatically:
1. Run the extraction script
2. Spawn Sonnet sub-agents (3 parallel, ~10 refs each)
3. Collect and compile verification results
4. Present a summary table with issues found
5. Mention the RIS file for Zotero import

## Output Example

```
## Issues Found (8 of 74 references)

| # | Reference      | Status       | Issue                                    |
|---|----------------|--------------|------------------------------------------|
| 3 | Beck (1979)    | ERROR        | Year should be 1976, publisher IUP       |
| 13| Ferenczi (1932)| ERROR        | Publication year is 1988, not 1932       |
| 39| Klein (1932)   | ERROR        | Publisher should be Hogarth Press         |
| 54| Rachman (1972) | UNVERIFIABLE | No book found with this title/publisher  |

Clean references: 66 of 74 verified correct.
```

## RIS Export

The `.ris` file can be imported into:
- **Zotero**: File → Import → select .ris file
- **Mendeley**: File → Import → select .ris file
- **EndNote**: File → Import → select .ris file

Each RIS entry includes the original APA text in the notes field for reference.

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Instructions for Claude Code (the skill definition) |
| `ref_verify.py` | Python extraction + parsing + RIS export script |
