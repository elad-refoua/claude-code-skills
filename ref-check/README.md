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

## Requirements

```bash
pip install python-docx
pip install anthropic  # Optional: for --verify mode
```

## Usage

In Claude Code, say:
- "check references in my paper"
- "ref check"
- "verify references"

Or provide the `.docx` path directly.

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

## Optional: LLM Verification

Set `ANTHROPIC_API_KEY` to enable automatic Opus verification, which:
- Catches citations that regex missed
- Identifies false positives (noise words parsed as authors)
- Makes red-marked references safe to delete with high confidence

The skill also has a self-learning system that remembers patterns across papers.
