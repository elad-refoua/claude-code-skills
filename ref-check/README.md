# ref-check

Cross-reference every in-text citation against the reference list in an academic paper (.docx) and produce a color-coded Word document.

## What It Does

Scans your paper and highlights citations and references:

| Location | Color | Meaning |
|----------|-------|---------|
| Body text | **Green** | Citation matches a reference |
| Body text | **Cyan** | Fuzzy match (e.g., year suffix a/b) |
| Body text | **Yellow** | Citation NOT found in references |
| References | **Green** | Reference is cited in text |
| References | **Cyan** | Fuzzy match to a citation |
| References | **Red** | Reference NOT cited in text |

## Architecture

```
Python (regex + highlighting) -> JSON output -> Sonnet sub-agent (independent extraction) -> Opus sub-agent (verification)
```

1. **Python script**: Regex extraction, fuzzy matching, color-coded highlighting. No API keys needed.
2. **Sonnet sub-agent**: Claude Code spawns a Sonnet agent that independently extracts all citations (catches what regex misses).
3. **Opus sub-agent**: Claude Code spawns an Opus agent to verify remaining unmatched items, confirming red references are truly uncited.

## Requirements

```bash
pip install "python-docx>=1.2.0"
```

Version 1.2.0 or later is needed for comment bubbles (`--comments`, `--add-comments`); on older versions no comments are added and no error is shown.

No API keys needed in the script. Claude Code handles LLM verification via sub-agents.

## Usage

In Claude Code, say:
- "check references in my paper"
- "ref check"
- "verify references"

Or provide the `.docx` path directly.

## Output

- `<filename>_REF_CHECK.docx` - Color-coded Word document with legend
- `<filename>_RESULTS.json` - Structured data for Claude Code sub-agents

## Citation Patterns Supported

- Parenthetical: `(Author, Year)`, `(Author, Year; Author2, Year2)`
- Narrative: `Author (Year)`, `Author et al. (Year)`, `Author (e.g., Year)`
- Possessive: `Author's ... (Year)` with nearest-Author matching
- First name + possessive: `Otto Kernberg's approach (1975, 1984)`
- Bracket: `Sullivan [1953]`, `[Author1, Year; Author2, Year]`
- Author inheritance: `(Gelso, 2009; 2014)` - bare year inherits previous author
- "And colleagues": `Stiles and colleagues (2009; Kramer & Stiles, 2015)`
- Hyphenated names: `Kabat-Zinn (1990)`
- Year suffixes: `Freud (1912a)` fuzzy-matches `Freud (1912)`

## Self-Learning System

The skill remembers patterns across papers via `learned_patterns.json`:
- **Noise words**: False positives identified by sub-agents are filtered in future runs
- **Cross-matches**: Known citation-reference pairs with different years are auto-resolved

The file is created locally on the first `--save-learnings` run and is never committed. Its entries describe the manuscripts you checked, so keep it out of version control (add `ref-check/learned_patterns.json` to `.gitignore`) and do not copy it back into a shared repo.
