---
name: ref-check
description: |
  Cross-reference in-text citations against the references section in an academic paper (.docx).
  Outputs a color-coded Word document: green=matched, cyan=fuzzy match, yellow=citation missing from refs, red=ref not cited.
  Pipeline: Python regex + highlighting, then Claude Code sub-agents (Sonnet + Opus) verify results.

  TRIGGERS: "check references", "cross-reference citations", "ref check", "verify references",
  "match citations to references", "reference audit", "citations vs references",
  "בדוק הפניות", "בדיקת רפרנסים", "התאמת הפניות", "רפרנסים"
---

# Reference Checker

Cross-references every in-text citation against the reference list in an academic paper and produces a highlighted Word document, then verifies results with LLM sub-agents.

## Architecture

```
Python (regex + highlighting) → JSON output → Sonnet sub-agent (independent extraction) → Opus sub-agent (verification)
```

1. **Python**: Regex extraction, fuzzy matching, color-coded highlighting. No API keys needed.
2. **Sonnet sub-agent**: Independently reads body text and extracts all citations (catches what regex misses)
3. **Opus sub-agent**: Verifies remaining unmatched items, confirms red references are truly uncited

## Color Coding

| Location | Color | Meaning |
|----------|-------|---------|
| Body text | **Green highlight** | Citation exactly matches a reference |
| Body text | **Cyan highlight** | Citation fuzzy-matches a reference (year suffix a/b) |
| Body text | **Yellow highlight** | Citation NOT found in references |
| References | **Green highlight** | Reference IS cited in text |
| References | **Cyan highlight** | Reference fuzzy-matches a citation |
| References | **Red highlight** | Reference NOT cited in text |

## Table Support

The script extracts text from **both paragraphs and table cells** in the body of the document. This ensures citations inside Word tables are found and highlighted correctly.

## Comment Bubbles

Comments come from two sources:

### 1. Script comments (`--comments` flag)
The Python script adds **factual** bubble comments for clear-cut issues:

| Color | Comment |
|-------|---------|
| Yellow (body) | "Citation not found in reference list" |
| Red (refs) | "Reference not cited in body text" |

Cyan (fuzzy match) items do NOT get script-generated comments — they require contextual advice.

### 2. LLM comments (`--add-comments`, Step 8)
After the Opus sub-agent verifies results, it generates **contextual advice** comments that are injected via `--add-comments`. These include:
- Fuzzy match advice (e.g., which year suffix a/b/c to use)
- Cross-match explanations (citation ↔ reference with different years)
- False positive notes
- Other issues found during verification

This separation ensures factual comments are fast (regex) while advisory comments benefit from LLM judgment.

## How to Run

### Step 1: Get the file path
Ask the user for the .docx file path if not provided.

### Step 2: Run the Python script

```bash
py "C:/Users/user/.claude/skills/ref-check/ref_check.py" "<INPUT_FILE_PATH>" --comments
```

Requires: `python-docx >= 1.1.2` (`py -m pip install python-docx`)

The `--comments` flag adds bubble comment annotations to the output document. Omit it for highlighting-only output.

This outputs:
- `<filename>_REF_CHECK.docx` — color-coded Word document (with bubble comments if `--comments`)
- `<filename>_RESULTS.json` — structured data for sub-agents (body text including tables, ref text, matched/unmatched lists)

### Step 3: Read the JSON output

Use the Read tool to read the generated `_RESULTS.json`. Note:
- `body_text` and `ref_text` — full text for sub-agents
- `unmatched_citations` — yellow items (citations missing from refs)
- `uncited_references` — red items (refs not cited in text)
- `matched_citations` — green items
- `fuzzy_matches` — cyan items

### Step 4: Spawn Sonnet sub-agent for independent extraction

Use the **Task tool** with:
- `subagent_type`: `"general-purpose"`
- `model`: `"sonnet"`
- `description`: `"Extract all citations"`

**Sub-agent prompt** (fill in body_text from JSON):

```
You are an expert APA citation parser. Extract ALL in-text citations from this academic paper body text.

=== BODY TEXT ===
{body_text from _RESULTS.json}

=== INSTRUCTIONS ===
Find every citation. Look for ALL patterns:
- Parenthetical: (Author, Year), (Author & Author2, Year)
- Multi-citation: (Author, Year; Author2, Year2)
- Narrative: Author (Year), Author et al. (Year)
- Possessive: Author's (Year), Author's concept (Year)
- First name + possessive: Otto Kernberg's ... (1975, 1984, 2004)
- Bracket: Author [Year], [Author, Year; Author2, Year2]
- Prefixes: (e.g., Author, Year), (see Author, Year)
- "And colleagues": Author and colleagues (Year)
- "As cited in": (as cited in Author, Year)
- Year ranges: Author (Year1, Year2, Year3)
- Slash years: Author (1924/1986)
- Author inheritance: (Gelso, 2009; 2014) - both are Gelso

For each citation, extract:
1. First author SURNAME only (last name, capitalized)
2. Year (4 digits, optionally with letter suffix)

Rules:
- "et al." → first author only
- "Author & Author2" → first author only
- Skip noise: "Cognitive", "Therapy", "Self"
- Possessive: "Winnicott's" → "Winnicott"
- First names: "Otto Kernberg" → "Kernberg"
- Hyphenated names stay: "Kabat-Zinn"
- Each (surname, year) pair only ONCE

Return ONLY valid JSON:
{
  "citations": [
    {"surname": "Author", "year": "2024", "context": "3-5 word snippet"}
  ]
}
```

### Step 5: Compare Sonnet vs regex results

After Sonnet returns, compare its citation set with the regex `citation_set` from the JSON:
1. **Sonnet-only citations** = found by Sonnet but not regex (regex missed these)
2. **Regex-only citations** = found by regex but not Sonnet (keep these too)
3. **Merged set** = union of both

For each Sonnet-only citation, check if it matches any `uncited_references`. If yes, that reference is NOT truly uncited (rescue from red).

Report the Sonnet comparison to the user.

### Step 6: Spawn Opus sub-agent for verification

If there are unmatched citations or uncited references remaining after Sonnet merge, spawn an **Opus sub-agent**:

- `subagent_type`: `"general-purpose"`
- `model`: `"opus"`
- `description`: `"Verify reference matching"`

**Sub-agent prompt** (fill in from JSON + Sonnet comparison):

```
You are an expert APA citation checker. A regex tool + Sonnet independently cross-referenced citations vs. references. I need you to verify the remaining unmatched items.

=== FULL BODY TEXT ===
{body_text}

=== FULL REFERENCE LIST ===
{ref_text}

=== CURRENT STATE ===

MATCHED (GREEN): {matched_citations list}
FUZZY (CYAN): {fuzzy_matches list}
UNMATCHED CITATIONS (YELLOW): {unmatched_citations list}
UNCITED REFERENCES (RED): {uncited_references list}

=== YOUR TASKS ===

1. **MISSED CITATIONS**: Any citations in the text that were missed? Look for unusual formats.
2. **FALSE POSITIVES**: Any YELLOW items that are NOT real citations?
3. **CROSS-MATCHES**: Can any YELLOW citation match a RED reference? (year typos, editions, spelling)
4. **RED VERIFICATION (CRITICAL)**: For EACH red reference, is it cited ANYWHERE in ANY form?
5. **FUZZY MATCH ADVICE**: For each CYAN item, write a specific comment explaining the year mismatch and advising which year/suffix to use (e.g., "Cited as Freud (1912) but reference list has Freud (1912a) and Freud (1912b) — verify which edition is intended").
6. **OTHER ISSUES**: Duplicates, formatting problems, year inconsistencies.

Return ONLY valid JSON:
{
  "missed_citations": [{"citation": "Author (Year)", "location": "context", "reference_exists": true/false}],
  "false_positives": ["citation1"],
  "cross_matches": [{"citation": "Author (Year)", "reference": "Author (Year)", "reason": "explanation"}],
  "confirmed_uncited_refs": ["ref1"],
  "possibly_cited_refs": [{"reference": "Author (Year)", "evidence": "how cited"}],
  "fuzzy_comments": [{"citation": "Author (Year)", "comment": "Specific advice about the year mismatch"}],
  "other_issues": ["issue1"]
}
```

### Step 7: Report results

Show the user:
- **Regex results**: counts of green, cyan, yellow, red
- **Sonnet findings**: citations Sonnet found that regex missed, and which matched refs
- **Opus verification**: missed citations, false positives, cross-matches, confirmed uncited
- Path to output files

### Step 8: Add Opus findings as comments (optional)

After Opus returns its JSON results, inject its findings as bubble comments into the highlighted document:

```bash
py "C:/Users/user/.claude/skills/ref-check/ref_check.py" --add-comments "<filename>_REF_CHECK.docx" "<findings.json>"
```

The findings JSON should have this structure (matching the Opus output from Step 6):
```json
{
  "cross_matches": [{"citation": "Author (Year)", "reference": "Author (Year)", "reason": "..."}],
  "false_positives": ["citation1"],
  "possibly_cited_refs": [{"reference": "Author (Year)", "evidence": "..."}],
  "fuzzy_comments": [{"citation": "Author (Year)", "comment": "Specific advice about the year mismatch"}],
  "other_issues": ["issue1"]
}
```

This adds comments authored "ref-check (Opus)" to the matching text spans in the document. The document is saved in-place.

## Important Notes
- The Python script does regex + highlighting only, NO API calls needed
- Sub-agents (Sonnet + Opus) are spawned by Claude Code via the Task tool
- The original file is NEVER modified
- Output: `_REF_CHECK.docx` (highlighted) + `_RESULTS.json` (data for sub-agents)
- Install: `py -m pip install python-docx` (requires >= 1.1.2 for comment support)
- **Tables**: Citations inside Word tables are extracted and highlighted automatically
- **Comments**: Use `--comments` flag to add bubble comment annotations explaining each issue

## Self-Learning System

The script loads `learned_patterns.json` from the skill folder:
- **Noise words**: previously identified false positives, filtered during regex extraction
- **Cross-matches**: known citation-reference pairs with different years, auto-resolved as cyan

Claude Code can update this file after sub-agent verification to save learnings for future runs.

## Citation Patterns (Regex)
- Parenthetical: `(Author, Year)`, `(Author, Year; Author2, Year2)`
- Author inheritance: `(Gelso, 2009; 2014)`
- Narrative: `Author (Year)`, `Author et al. (Year)`, `Bion (e.g., 1962)`
- Possessive: `Author's ... (Year)` (nearest-Author matching)
- First name + possessive: `Otto Kernberg's ... (1975, 1984, 2004)`
- Bracket: `Sullivan [1953]`, `[Author1, Year; Author2, Year]`
- "And colleagues": `Stiles and colleagues (2009)`
- Year suffixes: `Freud (1912a)` fuzzy-matches `Freud (1912)`
