---
name: ref-check
description: |
  Cross-reference in-text citations against the references section in an academic paper (.docx).
  Outputs a color-coded Word document: green=matched, cyan=fuzzy match, yellow=citation missing from refs, red=ref not cited.

  TRIGGERS: "check references", "cross-reference citations", "ref check", "verify references",
  "match citations to references", "reference audit", "citations vs references",
  "בדוק הפניות", "בדיקת רפרנסים", "התאמת הפניות", "רפרנסים"
---

# Reference Checker

Cross-references every in-text citation against the reference list in an academic paper and produces a highlighted Word document.

## Color Coding

| Location | Color | Meaning |
|----------|-------|---------|
| Body text | **Green highlight** | Citation exactly matches a reference |
| Body text | **Cyan highlight** | Citation fuzzy-matches a reference (year suffix a/b) |
| Body text | **Yellow highlight** | Citation NOT found in references |
| References | **Green highlight** | Reference IS cited in text |
| References | **Cyan highlight** | Reference fuzzy-matches a citation |
| References | **Red highlight** | Reference NOT cited in text |

## How to Run

### Step 1: Get the file path
Ask the user for the .docx file path if not provided.

### Step 2: Run the Python script

```bash
py "C:/Users/user/.claude/skills/ref-check/ref_check.py" "<INPUT_FILE_PATH>"
```

Opus verification runs automatically when `ANTHROPIC_API_KEY` is set.
To skip Opus (regex only): add `--no-verify` flag.

Requires: `python-docx` (`py -m pip install python-docx`)
For Opus: `anthropic` (`py -m pip install anthropic`) + `ANTHROPIC_API_KEY` env var

### Step 3: Report results
Show the user:
- Count of exact matches (green) and fuzzy matches (cyan)
- Count of citations missing from references (yellow) - list them
- Count of uncited references (red) - list them
- If `--verify` was used: Opus's findings (missed citations, false positives, cross-matches)
- If learned patterns were applied: which cross-matches were auto-resolved
- Path to the output file

## Important Notes
- The output file is saved as `<original_name>_REF_CHECK.docx` in the same folder
- The original file is NEVER modified
- A color legend is inserted at the top of the output document
- Hebrew/Unicode-safe (handles curly quotes, unicode hyphens)
- Requires: `python-docx` (`py -m pip install python-docx`)
- For `--verify`: `anthropic` (`py -m pip install anthropic`) + `ANTHROPIC_API_KEY` env var

## Self-Learning System

The skill learns from Opus verification runs and applies learnings to future papers:

**What it learns (conservative, no over-generalization):**
- **Noise words**: Words Opus identifies as false positives (e.g., "cognitive" parsed as an author name) are added to the noise filter for ALL future papers
- **Cross-matches**: When Opus matches a yellow citation to a red reference (e.g., year typo, edition difference), the specific (author, cite_year, ref_year) triplet is saved. On future runs, if the SAME author+year combination appears unmatched, it's auto-resolved as cyan

**Storage**: `learned_patterns.json` in the skill folder (auto-created on first `--verify` run)

**Safety**: Cross-matches only fire when BOTH the citation AND reference exist in the current paper. No broad regex patterns are auto-generated.

## Citation Patterns Supported
- Parenthetical: `(Author, Year)`, `(Author, Year; Author2, Year2)`
- Author inheritance: `(Gelso, 2009; 2014)` - second year inherits Gelso
- Narrative: `Author (Year)`, `Author et al. (Year)`, `Bion (e.g., 1962)`
- Possessive: `Author's ... (Year1, Year2; OtherAuthor, Year)` (nearest-Author matching)
- First name + possessive: `Otto Kernberg's transference-focused approach (1975, 1984, 2004)`
- Bracket single: `Sullivan [1953]`, `Young, Klosko, & Weishaar [2003]`
- Bracket multi: `[Author1, Year; Author2, Year]`
- "And colleagues": `Stiles and colleagues (2009; Kramer & Stiles, 2015)`
- Lowercase citations: `stiles (2009)` normalized to `Stiles`
- Hyphenated names: `Kabat-Zinn (1990)` preserved correctly
- Year suffixes: `Freud (1912a)` fuzzy-matches `Freud (1912)` in refs

## Edge Cases
- Multiple years for one author: "Kohut (1971, 1977, 1984)" - splits into 3 citations
- Semicolon-separated: "(Beck, 1967; Ellis, 1962)" - splits into 2
- Year with letter suffix: "Freud (1912a)" - exact match or fuzzy match to "Freud (1912)"
- Duplicate refs with same year: auto-assigns a/b suffixes
- Prefixes like "e.g.," "see", "cf." are cleaned before matching
- Noise words (therapy, cognitive, etc.) filtered out to reduce false positives
