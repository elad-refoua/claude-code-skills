---
name: apa-manuscript
description: |
  Generate APA-style manuscripts from R analysis output with embedded statistics.
  Use when asked to write a paper, manuscript, or results section from existing R analysis tables.
  Outputs both Markdown and Word (via officer).
version: 3.0.0
---

# APA Manuscript from R Analysis Output (v3.0)

## Content Safety
- **Before editing any existing manuscript file**, create a timestamped backup (e.g., `manuscript_backup_20260214_1430.md`). This prevents irreversible content loss during revision.
- Never silently remove substantive paragraphs during reformatting or revision.

## Paper Organization for Revision
When organizing papers for manuscript revision:
1. **Extract references FIRST** — read the manuscript, build complete reference list BEFORE touching files
2. **Separate "cited" from "potential"** — `01_cited_in_manuscript/` (actually in References) vs `02_potential_additions/` (suggested to add). Never mix these categories.
3. **Naming:** `FirstAuthor_Year_ShortTopic.pdf`
4. **Verify** — launch a verification agent to compare organized folders against manuscript references before declaring done
5. **Common mistake:** treating reviewer-suggested papers as "already cited" — they go in potential additions

## When to Use

Trigger on:
- "write this as a paper/manuscript"
- "generate APA manuscript from the analysis"
- "write hypotheses, method, results, discussion"
- "I want the numbers to come from the code"
- Any request to produce academic manuscript text with embedded statistics

## Reference Files

Everything lives in `~/.claude/agents/writer/`:
- `rules/six-levels.md` -- all writing quality rules (6 levels, banned words, 17 anti-AI checks)
- `manuscript/domain-rules.md` -- psychology conventions, epistemic language, lab style, author format
- `manuscript/citation-guide.md` -- citation system, references.csv format, multi-style support
- `AGENT.md` -- the main writer agent
- `manuscript/profiles/` -- journal-specific YAML profiles

## Architecture: R Generates the Manuscript

The manuscript is generated FROM R code, not written manually. This ensures all statistics are embedded from actual analysis output.

```r
# Pattern: Load CSV tables -> Extract stats -> Build text with glue() -> Output md + docx
pacman::p_load(tidyverse, glue, officer, flextable)

# Load saved analysis tables
t01 <- read.csv(file.path(tables_dir, "Table_01_....csv"))

# Extract statistics into variables
or_val <- fmt_num(row$OR, 3)
p_val  <- fmt_p(row$p_value)

# Build manuscript sections with glue()
ms$results <- glue("
The association was significant (OR = {or_val}, 95% CI [{ci_lo}, {ci_hi}], p {p_val}).
")

# Output: Markdown via writeLines() + Word via officer::body_add_par()
```

### Helper Functions (always include)

```r
fmt_p <- function(p) {
  if (is.na(p)) return("")
  if (is.character(p)) { if (grepl("<", p)) return(p); p <- as.numeric(p) }
  if (p < .001) return("< .001")
  paste0("= ", sub("^0", "", sprintf("%.3f", p)))
}
fmt_num <- function(x, digits = 2) sprintf(paste0("%.", digits, "f"), x)
fmt_apa <- function(x, digits = 2) sub("^0\\.", ".", sprintf(paste0("%.", digits, "f"), x))
```

## Citation Architecture

Every manuscript uses a CSV-based citation system. Never hardcode citations -- always use citation functions.

```r
ref_style <- "apa7"  # Set once. Options: "apa7", "ama", "vancouver", "chicago"
refs <- read.csv(file.path(output_dir, "references.csv"), stringsAsFactors = FALSE)

cite(key)          # Narrative:     Smith (2017)
cite_p(keys)       # Parenthetical: (Smith, 2017; Jones et al., 2013)
cite_s(key)        # Possessive:    Smith's (2017)
```

Usage in glue() strings:

```r
ms$intro <- glue("
{cite_s('dweck2017')} framework posits nine basic psychological needs.
Prior work has shown cumulative stress effects {cite_p('evans2013')}.
")
```

Reference list output:

```r
validate_citations()  # Warns about uncited refs or missing keys
ms$references <- glue("## References\n\n{generate_references()}")
```

## Journal Adaptation

When a target journal is specified, load its profile from `~/.claude/agents/academic-writing/profiles/{name}.yaml`.

Key integration points in R script:

```r
# Load journal profile settings
profile <- yaml::read_yaml(file.path("~/.claude/agents/academic-writing/profiles", paste0(journal, ".yaml")))

# Set citation style from profile
ref_style <- profile$citation_style

# Enforce word counts after each section
check_word_count <- function(text, section, profile) {
  limit <- profile$word_limits[[section]]
  if (!is.null(limit) && str_count(text, "\\S+") > limit)
    warning(glue("{section}: {str_count(text, '\\S+')} words exceeds {limit} limit"))
}

# Structured abstract uses profile sections
abstract_sections <- profile$abstract_sections  # e.g., c("Importance", "Objective", ...)

# Section headings from profile
section_headings <- profile$section_headings
```

Available profiles: `apa7-default.yaml`, `jama-network-open.yaml`, `cyberpsychology.yaml`, `computers-human-behavior.yaml`.

## Supporting Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| `writer` | Opus | Writes manuscript sections |
| `paper-reader` | Haiku | Extracts data from papers for references.csv |
| `writer-reviewer` | Haiku | Validates output against self-review checks |

## Output Checklist

Before delivering, verify:
- [ ] All statistics embedded from code (no hardcoded numbers)
- [ ] All citations use cite()/cite_p()/cite_s() -- no hardcoded author-year strings
- [ ] References section auto-generated from references.csv
- [ ] validate_citations() reports 0 errors
- [ ] "Association" used throughout (not "relationship")
- [ ] Hypotheses describe plans, not findings
- [ ] Every results paragraph tagged (confirmatory/exploratory)
- [ ] Exploratory findings use hedged language
- [ ] Confirmatory findings use confident language
- [ ] Word version (officer) matches Markdown version
- [ ] Phase-based structure (not theatrical)
- [ ] Limitations acknowledge cross-sectional design first
- [ ] No HARD BAN words; SOFT BAN within limits
- [ ] Sentence length SD > 8
- [ ] No transition monotony
- [ ] No formulaic paragraph structure
- [ ] No echo conclusions
- [ ] No sweeping conclusions
- [ ] No false balance in epistemic tone
- [ ] Grammar precision verified
- [ ] Journal profile applied (if target journal specified)
- [ ] Word counts within journal limits (if limits specified)
- [ ] Abstract format matches journal (structured vs. unstructured)
