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

### Standalone mode (`--comments` flag only)
When running without Opus, the script adds **factual** bubble comments:

| Color | Comment |
|-------|---------|
| Yellow (body) | "Citation not found in reference list" |
| Red (refs) | "Reference not cited in body text" |

### Full pipeline mode (`--add-comments`, Step 8)
When the Opus sub-agent has verified results, `--add-comments` creates **unified comments** that:
1. **Strip** all previous ref-check comments (preserves author's own comments)
2. **Merge** factual status + Opus findings into ONE comment per citation/reference
3. **Mirror** cross-references: a body citation comment also appears on its matching reference entry

Example unified comment on "Beck (1976)" in body:
> Not found in reference list
> ---
> Cross-match: Beck (1976) ↔ Beck (1979)
> Same book — originally 1976, reference list has 1979 reprint.

The same cross-match info also appears on "Beck (1979)" in the reference list.

Comment types merged per item: factual status, cross-match explanations, fuzzy match advice, false positive notes, possibly-cited evidence, and other issues.

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
  "false_positives": [{"text": "Author (Year)", "reason": "why not a real citation"}],
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
- **Opus verification**: summarize each category from the JSON output
- Path to output files

**Opus output keys and how to use them:**

| Key | Claude Code action |
|-----|--------------------|
| `missed_citations` | Report to user (citations regex+Sonnet both missed) |
| `confirmed_uncited_refs` | Report to user (truly uncited references) |
| `cross_matches` | Report + inject as comments via Step 8 |
| `false_positives` | Report + inject as comments via Step 8 |
| `fuzzy_comments` | Inject as comments via Step 8 |
| `possibly_cited_refs` | Report + inject as comments via Step 8 |
| `other_issues` | Report + inject as comments via Step 8 |

### Step 8: Add unified comments (optional)

After Opus returns its JSON results, inject **unified** bubble comments into the highlighted document. This replaces all previous ref-check comments with merged ones that combine factual status + Opus findings:

```bash
py "C:/Users/user/.claude/skills/ref-check/ref_check.py" --add-comments "<filename>_REF_CHECK.docx" "<findings.json>"
```

The script automatically:
1. **Strips** all existing ref-check comments (preserves author's own comments)
2. **Reads** `_RESULTS.json` for factual status (which items are yellow/red)
3. **Merges** all info into ONE comment per citation/reference
4. **Mirrors** cross-reference comments on both body citation AND reference entry

The findings JSON should have this structure (matching the Opus output from Step 6):
```json
{
  "cross_matches": [{"citation": "Author (Year)", "reference": "Author (Year)", "reason": "..."}],
  "false_positives": [{"text": "Author (Year)", "reason": "..."}],
  "possibly_cited_refs": [{"reference": "Author (Year)", "evidence": "..."}],
  "fuzzy_comments": [{"citation": "Author (Year)", "comment": "Specific advice about the year mismatch"}],
  "other_issues": ["issue1"]
}
```

The document is saved in-place. Running `--add-comments` multiple times is safe — it strips and rebuilds each time.

### Step 9: Save learnings for future runs (optional)

After Opus returns its findings, persist cross-matches and noise words so future runs auto-resolve them:

```bash
py "C:/Users/user/.claude/skills/ref-check/ref_check.py" --save-learnings "<findings.json>"
```

This extracts from the Opus findings JSON:
- `cross_matches` → saved as learned cross-match patterns (auto-resolved as cyan on next run)
- `false_positives` → single-word surnames saved as noise words (filtered during regex extraction on next run)

Learnings merge into `learned_patterns.json` without duplicates.

## Important Notes
- The Python script does regex + highlighting only, NO API calls needed
- Sub-agents (Sonnet + Opus) are spawned by Claude Code via the Task tool
- The original file is NEVER modified
- Output: `_REF_CHECK.docx` (highlighted) + `_RESULTS.json` (data for sub-agents)
- Install: `py -m pip install python-docx` (requires >= 1.1.2 for comment support)
- **Tables**: Citations inside Word tables are extracted and highlighted automatically
- **Comments**: Use `--comments` flag to add bubble comment annotations explaining each issue

## Self-Learning System

The script uses `learned_patterns.json` (in the skill folder) to improve across runs.

**Lifecycle**: Load on startup → apply during regex → Opus verifies → save learnings → next run benefits.

### Data stored
- **Noise words**: false positive surnames (e.g., "Cognitive") — filtered out during regex extraction
- **Cross-matches**: citation-reference pairs with different years (e.g., cited as 1953, ref has 1940) — auto-resolved as cyan

### CLI commands
- **Load** (automatic): On every run, `load_learned_patterns()` reads the file. Console shows `[LEARN] Loaded N noise words, M cross-matches from memory`.
- **Save** (Step 9): `py ref_check.py --save-learnings <findings.json>` extracts patterns from Opus output and merges into the file.

### Conservative learning
- Noise words generalize across papers (a false positive in one paper is likely false in all)
- Cross-matches only fire when BOTH the citation AND the reference exist in the current paper

## Citation Patterns (Regex)
- Parenthetical: `(Author, Year)`, `(Author, Year; Author2, Year2)`
- Author inheritance: `(Gelso, 2009; 2014)`
- Narrative: `Author (Year)`, `Author et al. (Year)`, `Bion (e.g., 1962)`
- Possessive: `Author's ... (Year)` (nearest-Author matching)
- First name + possessive: `Otto Kernberg's ... (1975, 1984, 2004)`
- Bracket: `Sullivan [1953]`, `[Author1, Year; Author2, Year]`
- "And colleagues": `Stiles and colleagues (2009)`
- Year suffixes: `Freud (1912a)` fuzzy-matches `Freud (1912)`
