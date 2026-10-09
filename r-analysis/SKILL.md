---
name: r-analysis
description: "R statistical analysis with an opinionated, review-friendly coding style. Use when performing R analysis - includes file headers, code style (no loops, no custom functions), multilevel models, sjPlot output, and visualization guidelines."
---

# R Statistical Analysis Skill

This skill is the **style reference for review-friendly R**: code written so that the person who
owns the analysis can read it top to bottom, once, and sign off. The 12-rule constitution below is
the canon; everything after it is the operational detail that implements it. The canonical OWNER of
this style is the **r-coder** agent (`r-coder/AGENT.md` in this repo) -- for any paper / pipeline /
analysis R, use r-coder or load its full stack, write to the constitution, and pass its lint gate
before delivering.

**Two rules that live elsewhere but bite hardest here:** **normalize column names in the first
cleaning step of a new study** -- strip Qualtrics ChoiceID suffixes and other export artifacts,
because a name becomes unaffordable to change once results are frozen; and **never interpret a blank
cell before enumerating what writes NA in the stage that produced the file** -- a masked value and an
unanswered one look identical. Full guidance in the `qualtrics-cleaning` skill and `r-coder/AGENT.md`
(both in this repo).

## THE R STYLE CONSTITUTION (canon -- read first)

1. **Linear narrative.** A script reads top to bottom like prose: numbered `## Step N ----` sections
   in the exact order a human follows the logic. NO loops, NO custom functions -- write each step out
   explicitly. If you reach for a `for`/`while` or a `function(){}`, restructure until you don't need it.
2. **Clarity absolutism.** Code is written to be READ by the reviewer, not only to run. Explicit over
   clever. Semantic keys and names (`id_canonical`, item codes), never bare row/column indices or magic
   positions. `lowercase_with_underscores`; tidyverse pipes; one idea per line.
3. **Config is pure data.** All paths, IDs, item lists, and thresholds live in `config.R` -- data only,
   zero logic. Every constant carries a provenance comment naming its source
   (`# analysis plan sec X.Y + decision record NNN`). `run_clean.R` sources `config.R` and carries the
   narrative.
4. **Freeze the inputs.** Pull raw data once into a read-only `data/raw_frozen_<date>/` with a
   `MANIFEST.json` (row counts + sha256). Analyze only from the freeze, never from a live/moving
   export, and never hand-edit data in Excel.
5. **Per-step saves.** Every step writes its result to `step_outputs/<name>_after_step_N.rds` (+ `.csv`)
   and the next step reads that file, so any step is independently inspectable and re-runnable. Use
   cascading `source()` so running a late step regenerates the earlier ones. KEEP item-level data
   alongside scales -- never delete items.
6. **Per-step checks + a checks-checklist.** Every step writes a PASS/FAIL assertion to
   `step_checks/step_N_*.txt` -- keep gate (rows kept <= rows in), row reconciliation
   (raw = kept + sum of logged drop reasons), final invariant (e.g. wide<->long agree cell-for-cell).
   A failed assert `stop()`s the run. Ship a `CHECKS_CHECKLIST.md` (template in this repo at
   `r-coder/templates/CHECKS_CHECKLIST_TEMPLATE.md`): Part A = what the code already verified,
   Part B = the ordered path a human walks to sign-off.
7. **Numbers come from code, never memory.** Every number in `Results.md` / the manuscript is
   glue-injected from the pipeline; none is hand-typed. Regenerate the write-up from the run --
   do not transcribe.
8. **Deterministic verification.** Checks are code (asserts, diffs, counts, hashes), not eyeballing
   and not an LLM's say-so. Surface EVERY number mismatch and investigate. Refactor a pipeline step
   only behind a parallel-output, cell-by-cell diff (`_v2` file + compare script) before replacing
   the original.
9. **ASCII-only in comments and `cat()` strings.** On Hebrew Windows (CP1255) non-Hebrew Unicode
   renders as garbage; use `-`, `<-`, `->`, `>=`, `OK`, `...`. Hebrew text is fine under
   `Sys.setlocale("LC_ALL","Hebrew")`; match Hebrew literals in data via `charToRaw` byte signatures,
   not literal strings.
10. **Standard header + stack.** Open every script with the reset header (rm / cat clear / locale /
    dev.off) and the standard `library()` block. MLM via `nlme::lme` (this style's default; see
    Multilevel Models below). APA tables via `sjPlot::tab_model`; plots via `theme_minimal()` +
    `ggsave(..., dpi = 300)`. Report effect sizes.
11. **Tidy, documented folder.** One canonical taxonomy -- `code/`, `data/raw_frozen_<date>/`,
    `step_outputs/`, `step_checks/`, `docs/` -- mapped by an `INDEX.md`; nothing load-bearing lives
    only in `_ARCHIVE/`; a `REVIEW_PACKET` states open items honestly.
12. **AUDIT-PASSED != USER-LOCKED.** The N-consecutive-clean automated audit is necessary but NOT
    sufficient. Code is LOCKED only after the reviewer personally reads it top to bottom (via the
    checks-checklist path) and explicitly approves. Until then the honest status is
    "AUDIT-PASSED, awaiting your review" -- never "locked."

**Canonical owner + gate (pointers, all in this repo):**
- **Owner:** the **r-coder** agent (`r-coder/AGENT.md`) owns this style; this skill is its reference.
  Spawn it with the analysis spec + project context for any paper/pipeline/analysis R.
- **Gold exemplars (imitate these):** a `run_clean.R` (the linear, step-numbered pipeline) + `config.R`
  (pure-data config with provenance comments) -- the shape every deliverable should match.
- **Lint gate:** `r-coder/scripts/r_lint.py` -- run it before delivering; it flags loops, custom
  functions, bare positional indexing, missing step headers / saves / guards, low comment density,
  non-ASCII comments, unshielded base-R reads under a Hebrew locale, and pattern-chosen column sets
  whose members are never named.

The sections below are the operational detail that implements the constitution -- every dated lesson
preserved.

## File Header
Always start scripts with:
```r
rm(list=ls())
cat("\014")
Sys.setlocale("LC_ALL", "Hebrew")
if (is.null(dev.list()) == FALSE){dev.off()}
```

**Because this header sets the Hebrew locale, every base-R text read later in the script
(`read.csv`/`read.table`/`read.delim`/`scan`) must carry `encoding = "UTF-8"`** - e.g.
`read.csv(path, encoding = "UTF-8")` - or use an immune reader (`readr::read_csv`,
`data.table::fread`, `readxl`, `jsonlite`, `readRDS`; prefer these for text data). Under the Hebrew
locale an unshielded base-R read **silently drops every row containing a character outside CP1255**
(emoji, arrows, Cyrillic; Hebrew itself is safe) - measured 6 rows in, 4 out, no error - and
`fileEncoding = "UTF-8-BOM"` does NOT prevent it. The r-coder lint gate FAILs this pattern
(check (i)).

## Code Style
1. **NO LOOPS** - Write each step explicitly
2. **NO CUSTOM FUNCTIONS** - Keep code readable and explicit
3. Use tidyverse piping
4. Variable naming: `lowercase_with_underscores`
5. Section headers: `## Section Name----`
6. **ASCII-only in comments and `cat()` strings** (CRITICAL on Hebrew Windows). On a Hebrew-locale Windows machine R/RStudio uses the CP1255 codepage; fancy Unicode chars (em-dash, arrows, checkmarks, smart quotes) display as garbage like `ג€` or `?`. Use these replacements:

| Don't use | Use instead | Don't use | Use instead |
|---|---|---|---|
| `—` em-dash | `-` or `--` | `≥` `≤` | `>=` `<=` |
| `–` en-dash | `-` | `≈` | `~=` |
| `←` `→` | `<-` `->` | `≠` | `!=` |
| `✓` `✗` | `OK` `X` | `×` mult sign | `x` |
| `"` `"` `'` `'` smart quotes | `"` `'` ASCII | `…` ellipsis | `...` |
| `•` `·` bullets | `*` or `-` | non-breaking space | regular space |

Hebrew text in comments/paths IS fine (encoding-consistent with `Sys.setlocale("LC_ALL","Hebrew")`); the rule is only for NON-Hebrew Unicode chars.

For string matching of Hebrew literals in data (e.g., detect `"בדיקה"` in participant names), prefer **byte signatures via `charToRaw`** over literal Hebrew strings — encoding-agnostic and avoids file-display issues. Do it in constitution style (no custom function, no loop): build the byte pattern once, then match it vectorized over the whole column with `grepl(useBytes = TRUE)`:
```r
## Build the byte pattern once, then match it vectorized (no loop, no custom function).
sig_bedika_utf8 <- rawToChar(as.raw(c(215, 145, 215, 147, 215, 153, 215, 167, 215, 148)))  # "בדיקה" UTF-8
sig_bedika_cp   <- rawToChar(as.raw(c(0xE1, 0xE3, 0xE9, 0xF7, 0xE4)))                       # "בדיקה" CP1255

data <- data %>%
  mutate(is_test = grepl(sig_bedika_utf8, name, fixed = TRUE, useBytes = TRUE) |
                   grepl(sig_bedika_cp,   name, fixed = TRUE, useBytes = TRUE))
```

## Required Packages
```r
library(tidyverse)
library(dplyr)
library(haven)
library(psych)
library(nlme)
library(sjPlot)
library(ggplot2)
library(jtools)
library(interactions)
```

## Multilevel Models
For ESM/EMA data, use this pattern:
```r
model <- lme(outcome ~ predictor1 + predictor2,
             random = ~ 1 + predictor | id,
             data = data,
             na.action = na.omit,
             control = lmeControl(opt = "optim"))
```

## Output Tables
Use sjPlot for APA-formatted output:
```r
sjPlot::tab_model(model,
                  show.std = TRUE,
                  show.ci = FALSE,
                  p.style = "stars")
```

## Visualization
- Use `theme_minimal()`
- Save with `ggsave("plot.png", width = 8, height = 6, dpi = 300)`
- Colors: Blue vs Red for group comparisons

## Scale Construction
```r
data <- data %>%
  rowwise() %>%
  mutate(scale_mean = mean(c(item1, item2, item3), na.rm = TRUE)) %>%
  ungroup()
```

## Key Rules
- Always provide APA-formatted output
- Include effect sizes when relevant
- Generate publication-ready plots
- Hebrew labels are acceptable in visualizations

## Provenance comments next to every locked threshold (2026-05-29)

For every numerical threshold or named constant that traces to a spec, paper, or decision record, inline-comment the authoritative source.

```r
STRONG_FIT_THRESHOLD          <- 0.70   # analysis plan sec X.Y + decision record NNN (banding scheme)
MODERATE_FIT_THRESHOLD        <- 0.50   # published field-standard floor (cite the paper)
HIT_RATE_FLAG_THRESHOLD       <- 0.85   # analysis plan sec X.Y + pre-reg auxiliary #N
DECLINE_FLAG_THRESHOLD        <- 0.25   # analysis plan Part N + pre-reg auxiliary #N
GOLD_STANDARD_RELIABILITY     <- 0.80   # reliability assumption taken from the cited source
HOLM_ALPHA                    <- 0.05   # analysis plan sec X.Y step N
BOOTSTRAP_ITERATIONS          <- 10000  # analysis plan sec X.Y step N
```

Why: when the spec drifts (e.g., a two-band cutoff scheme from one paper is later revised to a four-band scheme in the plan), the code becomes the canonical implementation but loses the audit trail. Provenance comments make future alignment audits trivial — grep for the value or the cite gets you both.

## Refactor = grep ALL references before declaring done (2026-05-29)

After renaming a constant, column, or variable, grep the ENTIRE codebase for the old name before considering the work done. Stale downstream references are the most common refactor bug class.

```r
# After renaming PRIMARY_FIT_FLOOR to four-band thresholds:
# Grep the project for PRIMARY_FIT_FLOOR -- must return zero matches.
```

For column renames in tibbles/data.frames: grep for `$old_name`, `["old_name"]`, AND `[, "old_name"]` patterns. Downstream consumers index columns multiple ways.

## Tibble schema consistency across branches (2026-05-29)

When a result table is built across multiple branches (success path + early-return paths + error fallback), every branch must emit the same column set. Otherwise `dplyr::bind_rows()` pads with NAs but the schema is drifted — downstream code that asserts column count or relies on column order breaks.

Constitution-style defensive pattern (no custom function, no loop): define ONE template tibble with the full column set, build every row -- kept OR dropped -- from that same schema in a single vectorized pass, then enforce the schema with `select(all_of(names(template)))`.

```r
## ONE template defines the schema; every row -- kept or dropped -- is built from it in a
## single vectorized pass, then the schema is enforced by select().
result_template <- tibble::tibble(
  source_variable       = character(),
  r_observed            = numeric(),
  abs_r_observed        = numeric(),
  signed_predicted_low  = numeric(),
  signed_predicted_high = numeric(),
  p_value               = numeric(),
  missing_reason        = character()
)

results <- cell_grid %>%                                    # one row per source x target cell
  mutate(
    missing_reason = dplyr::case_when(
      is.na(source_col) ~ "source missing",
      is.na(target_col) ~ "target missing",
      TRUE              ~ NA_character_
    ),
    r_observed            = dplyr::if_else(is.na(missing_reason), r_cell,    NA_real_),
    abs_r_observed        = abs(r_observed),
    signed_predicted_low  = dplyr::if_else(is.na(missing_reason), pred_low,  NA_real_),
    signed_predicted_high = dplyr::if_else(is.na(missing_reason), pred_high, NA_real_),
    p_value               = dplyr::if_else(is.na(missing_reason), p_cell,    NA_real_)
  ) %>%
  dplyr::select(dplyr::all_of(names(result_template)))      # enforce the one schema
```

Origin: in a real pipeline, the early-return tibbles of one step lost three columns after a refactor; bind_rows worked but the schema drifted until QC caught it.

## Code key == data label, character by character (2026-05-29)

When a list/dict key in code is supposed to match a value in a data column, verify the match programmatically. A single-character mismatch silently drops data.

```r
# Bad: subscale_definitions[["anxiety"]] vs items_long$item == "anx_pre"
# silently drops the anxiety subscale from output

# Defensive check:
expected_keys <- c("anx", "dep", "str", "sle", "soc")
actual_data_codes <- unique(sub("_(pre|post)$", "", items_long$item[grepl("_(pre|post)$", items_long$item)]))
stopifnot(
  "subscale_definitions keys must match data codes" =
    all(expected_keys %in% actual_data_codes)
)
```
