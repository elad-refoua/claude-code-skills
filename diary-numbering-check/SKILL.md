---
name: diary-numbering-check
description: Validates NumberOfDay / NumberInDay correctness in ESM/diary data. Detects wraparounds, duplicates, off-by-one errors, calendar-day inconsistencies, and out-of-range values. Produces a clear problem report with row-level diagnosis. Use when cleaning any diary/ESM data from Qualtrics or similar platforms where each participant fills out multiple short surveys per day over multiple days. Triggers - "check diary numbering", "validate numbering", "diary problems", "numbering audit", "בדיקת מספור יומנים", "בדוק יומנים".
---

# Diary numbering validation skill

A standalone checker for ESM/diary data. Surfaces **all numbering problems in one clear report** so the researcher can fix them quickly.

## The numbering convention (CRITICAL - learned from Elad's AIC studies)

In any well-formed diary dataset:

1. **`NumberOfDay`** = calendar days since the participant's first diary entry. The first day is **day 1**, the next calendar day is day 2, and so on. **Gap days (weekends, holidays, war breaks, missed days) are still counted** - they advance the counter. Example: if day 1 is 01/01, then day 5 is on 01/05 (even if the participant didn't submit anything between 01/02 and 01/04).

2. **`NumberInDay`** = the diary slot within a single calendar day. Typically 1, 2, 3, 4 (corresponding to ~4 prompts per day).

3. **Each diary entry has a unique `(id, NumberOfDay, NumberInDay)` triple.** No two entries should share the same triple - that's the definition of a numbering bug.

4. **NumberOfDay can exceed the planned study window** (e.g., 14) if a participant continued submitting beyond the scheduled period. Examples include participants who restarted after a long break, or participants who had to make up missed days late.

5. **Wraparound bug**: Qualtrics or similar platforms sometimes reset NumberOfDay to 1 after day 14 (or after a restart prompt). The researcher must detect this and renumber the second cycle to continue (15, 16, 17, ...).

6. **Drop signal**: A value of **0** in a `_R` correction column means "drop this row entirely." Researchers use this for test entries, false starts, or any other rows that should be excluded.

## What the checker validates

For a dataset with columns `id`, `NumberOfDay`, `NumberInDay`, `StartDate` (datetime), `ResponseId`:

| Check | Severity | Description |
|---|---|---|
| `duplicate_triples` | **FAIL** | Any `(id, NumberOfDay, NumberInDay)` triple appears more than once |
| `responseid_uniqueness` | **FAIL** | Any ResponseId appears more than once |
| `calendar_consistency` | **WARN** | NumberOfDay disagrees with calendar days from each participant's first StartDate (Δ >= 2 days) |
| `wraparound_suspected` | **WARN** | NumberOfDay drops by >= 3 between consecutive chronological entries for the same participant (e.g., 9 -> 1) |
| `numberinday_out_of_range` | **WARN** | NumberInDay < 1 or > some expected max (default 4) |
| `numberofday_negative_or_zero` | **FAIL** | NumberOfDay = 0 or negative (likely an invalid value) |
| `gap_too_large` | **INFO** | A participant has a gap of > 7 calendar days between consecutive entries - possible restart |

## How to invoke

```r
source("~/.claude/skills/diary-numbering-check/check_diary_numbering.R")
report <- check_diary_numbering(
  data         = my_dataset,           # data.frame with id, NumberOfDay, NumberInDay, StartDate, ResponseId
  expected_max_NumberInDay = 4,        # set to your study's prompts-per-day
  expected_max_NumberOfDay = 14,       # set to your planned diary length
  output_file  = "diary_numbering_report.md"  # human-readable markdown
)
```

The function returns a list with:
- `passed`: TRUE if no FAIL-level checks failed
- `summary`: counts per check
- `details`: per-row diagnostic table
- `report_md`: a markdown report saved to disk

## Report format

The output markdown follows this structure (one section per problem type):

```
# Diary numbering check - <dataset name>

**Generated:** <timestamp>
**Total rows:** <n>  *  **Total participants:** <m>  *  **Overall:** PASS/FAIL

## Summary

| Check                    | Status | Count |
|---|---|---|
| duplicate_triples        | FAIL   | 2     |
| responseid_uniqueness    | PASS   | 0     |
| calendar_consistency     | WARN   | 5     |
| ...                      | ...    | ...   |

## Detailed problems

### duplicate_triples (FAIL: 2)

For each duplicate, show:
- All rows sharing the triple
- StartDate of each, time gap between them
- Suggested action (fix_wraparound / drop_double_submission / keep_restart)

### calendar_consistency (WARN: 5)

Per participant:
- First StartDate (day 1)
- Expected vs actual NumberOfDay for each entry
- Rows where they disagree

...etc...
```

## When to use

- **Before any analysis** that depends on accurate day numbering (lag analyses, day-level aggregation)
- **After applying numbering corrections** from a manual review CSV to confirm no problems remain
- **As a one-shot QC** on raw Qualtrics output before any cleaning

## Recommended manual-review workflow (learned from AIC Study 2, 2026-05-18)

Iterative review pattern that worked well:

1. **Build review CSV in the SAME format** as the team's original review file. Researchers know that format and can edit it without learning new conventions. Add helper columns (is_in_duplicate, has_calendar_skip, suggested_NumberOfDay, calendar_day_from_start) at the END so they don't disrupt the familiar layout.

2. **Include FULL participant chronology**, not just the problem rows. Researchers need to see the diary entries before and after a problem to understand whether it's a wraparound, a restart, or a double-submission.

3. **Iterate in rounds.** Round 1: fix the obvious duplicates. Round 2: re-build the review file from the round-1 corrected data, surfacing what's still broken (often: calendar-skip-but-sequential issues that emerge once the wraparound is resolved). Round 3 etc. as needed.

4. **Use `build_review_csv()`** helper in this skill. It produces the AyE-format CSV with helper columns automatically.

5. **Use `flag_long_gaps()`** to add a participant-level `has_long_gap` flag at the end. This is for downstream analyses - researchers may want to filter or interact with this.

## Common subtle bug: calendar-skip-but-sequential

The hardest-to-spot bug is when:
- A participant skipped one or more diary days (war break, weekend, missed days)
- Qualtrics's NumberOfDay just incremented by 1 anyway, ignoring the skip
- Result: NumberOfDay says "day 4" but the calendar says "day 5"

Example:
| Calendar date | Qualtrics NumberOfDay | Correct NumberOfDay |
|---|---|---|
| 01/01 (Sun) | 1 | 1 |
| 01/02 (Mon) | 2 | 2 |
| _no entry_ | _no entry_ | _no entry_ |
| 01/04 (Wed) | 3 | **4** <- bug |
| 01/05 (Thu) | 4 | **5** <- bug |

Detect by: `NumberOfDay < calendar_day_index` where `calendar_day_index = as.integer(as.Date(StartDate) - as.Date(min(StartDate))) + 1`.

## When NumberOfDay > expected_max is OK

Don't treat NumberOfDay > 14 as a failure. Common legitimate reasons:
- The team renumbered second-cycle entries (15, 16, ..., 26) instead of restarting
- Participants who missed days but continued past day 14 to complete the planned number of submissions
- Re-enrolled participants who started a new cycle continuing from where they left off

This skill emits INFO (not WARN/FAIL) for NumberOfDay > expected_max.

## When long gaps (> 7 days) are OK

In Study 2 (war breaks), participants often took 1-3 week breaks and continued. The researcher (Elad) intentionally kept these as continuous numbering with calendar-day counting (so day 1 on 1/1, gap, day 25 on 1/25 is valid). Mark these participants with `has_long_gap = TRUE` for downstream awareness but DO NOT treat as a failure.

## Where the checker code lives

The full R implementation is at `~/.claude/skills/diary-numbering-check/check_diary_numbering.R`.
A worked example using AIC Study 2 data is at `~/.claude/skills/diary-numbering-check/example_aic_s2.R`.
The review-CSV builder is at `~/.claude/skills/diary-numbering-check/build_review_csv.R`.
The long-gap flagger is at `~/.claude/skills/diary-numbering-check/flag_long_gaps.R`.
