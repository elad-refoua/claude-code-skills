---
name: r-analysis
description: "R statistical analysis with Elad's coding style. Use when performing R analysis - includes file headers, code style (no loops, no custom functions), multilevel models, sjPlot output, and visualization guidelines."
---

# R Statistical Analysis Skill

When performing R statistical analysis, follow these guidelines:

## File Header
Always start scripts with:
```r
rm(list=ls())
cat("\014")
Sys.setlocale("LC_ALL", "Hebrew")
if (is.null(dev.list()) == FALSE){dev.off()}
```

## Code Style
1. **NO LOOPS** - Write each step explicitly
2. **NO CUSTOM FUNCTIONS** - Keep code readable and explicit
3. Use tidyverse piping
4. Variable naming: `lowercase_with_underscores`
5. Section headers: `## Section Name----`
6. **ASCII-only in comments and `cat()` strings** (CRITICAL on Hebrew Windows; established 2026-05-18). On Elad's machine R/RStudio uses CP1255 codepage; fancy Unicode chars (em-dash, arrows, checkmarks, smart quotes) display as garbage like `ג€` or `?`. Use these replacements:

| Don't use | Use instead | Don't use | Use instead |
|---|---|---|---|
| `—` em-dash | `-` or `--` | `≥` `≤` | `>=` `<=` |
| `–` en-dash | `-` | `≈` | `~=` |
| `←` `→` | `<-` `->` | `≠` | `!=` |
| `✓` `✗` | `OK` `X` | `×` mult sign | `x` |
| `"` `"` `'` `'` smart quotes | `"` `'` ASCII | `…` ellipsis | `...` |
| `•` `·` bullets | `*` or `-` | non-breaking space | regular space |

Hebrew text in comments/paths IS fine (encoding-consistent with `Sys.setlocale("LC_ALL","Hebrew")`); the rule is only for NON-Hebrew Unicode chars.

For string matching of Hebrew literals in data (e.g., detect `"בדיקה"` in participant names), prefer **byte signatures via `charToRaw`** over literal Hebrew strings — encoding-agnostic and avoids file-display issues. Example:
```r
sig_bedika_utf8 <- c(215, 145, 215, 147, 215, 153, 215, 167, 215, 148)  # בדיקה in UTF-8
sig_bedika_cp   <- c(0xE1, 0xE3, 0xE9, 0xF7, 0xE4)                       # בדיקה in CP1255
contains_bedika <- function(s) {
  rb <- as.integer(charToRaw(s))
  in_seq <- function(needle, hay) {
    n <- length(needle); h <- length(hay)
    if (n > h) return(FALSE)
    for (i in seq_len(h - n + 1)) if (all(hay[i:(i + n - 1)] == needle)) return(TRUE)
    FALSE
  }
  in_seq(sig_bedika_utf8, rb) || in_seq(sig_bedika_cp, rb)
}
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

For every numerical threshold or named constant that traces to a spec, paper, or ADR, inline-comment the authoritative source.

```r
HTC_STRONG_THRESHOLD          <- 0.75   # v7 sec 4.II.4 + ADR 0011 four-band scheme
HTC_MODERATE_THRESHOLD        <- 0.60   # Matthews 2022 field-standard floor
MCQ_HIT_FLAG_THRESHOLD        <- 0.80   # v7 sec 4.II.7 + pre-reg auxiliary #2 locked
DECLINE_FLAG_THRESHOLD        <- 0.20   # v7 Part VI + pre-reg auxiliary #4 locked
GOLD_STANDARD_RELIABILITY     <- 0.80   # Song et al. 2023 r_xx input assumption
HOLM_ALPHA                    <- 0.05   # v7 sec 4.III.2 step 4
BOOTSTRAP_ITERATIONS          <- 10000  # v7 sec 4.II.2 + sec 4.III.2 step 2
```

Why: when the spec drifts (e.g., HTC band scheme revised from Colquitt's 0.91/0.84 to S5's 0.75/0.60/0.50 four-band), the code becomes the canonical implementation but loses the audit trail. Provenance comments make future alignment audits trivial — grep for the value or the cite gets you both.

## Refactor = grep ALL references before declaring done (2026-05-29)

After renaming a constant, column, or variable, grep the ENTIRE codebase for the old name before considering the work done. Stale downstream references are the most common refactor bug class.

```r
# After renaming HTC_PRIMARY_FLOOR to four-band thresholds:
# Grep the project for HTC_PRIMARY_FLOOR -- must return zero matches.
```

For column renames in tibbles/data.frames: grep for `$old_name`, `["old_name"]`, AND `[, "old_name"]` patterns. Downstream consumers index columns multiple ways.

## Tibble schema consistency across branches (2026-05-29)

When a function returns a tibble built across multiple branches (success path + early-return paths + error fallback), every branch must emit the same column set. Otherwise `dplyr::bind_rows()` pads with NAs but the schema is drifted — downstream code that asserts column count or relies on column order breaks.

Defensive pattern: define ONE template tibble at the top of the function with NA defaults for all columns, and modify a copy in each branch.

```r
empty_result <- tibble::tibble(
  source_variable = NA_character_,
  r_observed      = NA_real_,
  p_value         = NA_real_,
  ci_lower        = NA_real_,
  ci_upper        = NA_real_,
  # ... all columns, NA defaults
)

compute_one_cell <- function(...) {
  if (missing_source) return(empty_result %>% mutate(missing_reason = "..."))
  if (missing_target) return(empty_result %>% mutate(missing_reason = "..."))
  # success path: rebuild same schema
  ...
}
```

Origin: Study 5 step5 early-return tibbles missed `abs_r_observed` + `signed_predicted_low/high` columns after a refactor; bind_rows worked but the schema drifted until QC caught it.

## Code key == data label, character by character (2026-05-29)

When a list/dict key in code is supposed to match a value in a data column, verify the match programmatically. A single-character mismatch silently drops data.

```r
# Bad: compound_definitions[["trust"]] vs pgr_long$item == "tru_sat"
# silently drops the trust compound from output

# Defensive check:
expected_keys <- c("tru", "cont", "worth", "mean", "ide")
actual_data_codes <- unique(sub("_(sat|fru)$", "", pgr_long$item[grepl("_(sat|fru)$", pgr_long$item)]))
stopifnot(
  "compound_definitions keys must match data codes" =
    all(expected_keys %in% actual_data_codes)
)
```
