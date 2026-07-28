# <DELIVERABLE NAME> -- Review Packet (for the reviewer's USER-LOCK review)

<!--
WHEN TO USE: Produce this for ANYTHING the reviewer will personally review (R Style Constitution rule 10) --
a cleaning pipeline, an analysis, a scoring script. It is the plain-language companion to the code:
it tells the reviewer what the thing does, what it found, how it was verified, what is still open, and
exactly what you are asking them to do -- WITHOUT making them read the code first. Structure modeled on
a good cleaning-pipeline REVIEW_PACKET (7 sections). Ship it as BOTH .md and .docx (docx so they can
comment/track-changes -- editable-docs-for-collaborators house rule).

HOUSE RULES: ASCII only. Numbers reconcile on screen (every count adds up; every dropped row has a
reason). Never claim "locked" -- the packet exists precisely because AUDIT-PASSED is not USER-LOCKED.
-->

**Date:** <YYYY-MM-DD>   **Status:** AUDIT-PASSED (<n>/<n> consecutive clean) -- **awaiting your personal review.**
**Built from:** the approved plan `<docs/PLAN_vN_YYYY-MM-DD.md>`.

<One or two sentences: what this deliverable is, and -- just as important -- what it is NOT (scope
boundary). E.g. "This is the data-organization pipeline only; no analysis, no models, no hypotheses.">

---

## 1. What you are approving

| File | What it is |
|---|---|
| `<code/config.R>` | <Pure settings/data: paths, ids, item lists, scoring rules, thresholds -- each with a provenance comment. No logic.> |
| `<code/run_clean.R>` | <The pipeline: N explicit Steps, top to bottom, in your style -- no loops, no custom functions, `## Step N ----` headers, ASCII comments, saves every step.> |

Both written fresh from the approved plan. Independently verified: **<0 custom functions, 0 loops>** (deterministic grep).

## 2. What it does, step by step (plain language)

<One bullet per step. No jargon -- describe the intent, not the code. Name the numbers that matter.>

- **Step 0 -- <freeze the raw>.** <Pulls all N surveys with readable names; saves a read-only copy + checksums.>
- **Step 1 -- <keep real responses>.** <Keeps a row if finished OR >= X% complete; records consent.>
- **Step 2 -- <remove non-participants>.** <Drops preview/test rows, junk ids, pre-start rows; flags (does not delete) <60s sessions.>
- **Step N -- <final tables + verification>.** <Builds the primary output and the full sanity battery.>

## 3. The results

<The reconciling counts, stated so they visibly add up. This is the section the reviewer scans first.>

- **<76> participants** (<Site A 34 + Site B 42>).
- <664 raw rows -> 524 pass the keep gate -> 449 kept after filtering; 26 duplicates collapsed>.
- Drops (all logged): <junk-id 117, no-id 13, staff-email 2, unfinished 82>. <32 short (<60s) responses flagged-and-kept.>
- <Key downstream count, e.g. 702 skill observations in the long table; reliability alpha 0.80-0.96.>

<Optional one-line comparison to a prior version, with the reason for any difference.>

## 4. How it was verified (your "verify with code" rule)

- **<n> consecutive clean** rounds by independent hostile auditors, each re-running the whole pipeline.
- <The single riskiest decision (e.g. which of two look-alike column blocks is real) is re-proven in
  code every run by tying back to <the old value-level-verified pipeline>.>
- <Primary output cross-checked against a derived output cell-for-cell, both directions: 0 mismatches.>
- Sanity battery: **ALL GREEN** (`<docs/VERIFICATION_REPORT.md>`).

## 5. Files to look at (the outputs)

In `<data/clean/>`: `<PROJECT_WIDE.csv>` (primary), `<PROJECT_LONG.csv>`, `<participants_overview.xlsx>`,
`<per_survey/>`, `<VERIFICATION_REPORT.md>`, `<codebook_clean.xlsx>`. The full review path with
time estimates is in `<docs/CHECKS_CHECKLIST_YYYY-MM-DD.md>`.

## 6. Small open items (your call whether to tidy before lock)

<Honest, specific, non-defensive. If none affect the data, say so. Never hide a discrepancy -- flag
it even if it is cosmetic; surfacing it is the point.>

1. <A reporting-coverage gap that does not affect the data; I can add it.>
2. <A cosmetic count that appears as X at one stage and Y at another -- same underlying rows, counted twice.>
3. <Anything I cannot fully explain -- flagged for honesty rather than guessed at.>

## 7. What I need from you

This is **AUDIT-PASSED, not locked.** Per your rule it becomes **USER-LOCKED** only after you
personally review it and approve. Please look over `<run_clean.R>` + `<config.R>` (and spot-check
`<the primary output>`). When you are satisfied, say so and I will create the immutable lock bundle
(git tag + checksums) and record it as USER-LOCKED in `PROJECT_TIMELINE.md`. If you want the items
in Section 6 tidied first, tell me and I will do that, then you approve.

---

### Filled mini-example (compressed, so the tone is concrete)

**Date:** 2026-07-07  **Status:** AUDIT-PASSED (7/7 clean) -- awaiting your review.
**Built from:** `docs/MERGE_PLAN_v2_2026-07-07.md`.
This turns three raw Qualtrics waves into one clean panel. No analysis, no models.

**1. Approving:** `code/config.R` (3 wave ids + id-fix map, no logic) and `code/run_merge.R`
(4 Steps, top to bottom, 0 loops / 0 functions -- grep-verified).

**2. Steps:** Step 0 freezes the 3 waves (checksummed, read-only). Step 1 keeps finished-or->=90%
rows. Step 2 joins on canonical id. Step 3 drops non-participants (logged) and writes the panel.

**3. Results:** 150 participants; 412 raw rows -> 380 kept + 32 logged drops (junk-id 20, no-id 12);
0 orphan ids after the join.

**4. Verified:** 7/7 clean; the id-join re-proven against wave-1 each run (380/380 match); panel row
count reconciles with the sum of per-wave keeps. Sanity battery ALL GREEN.

**5. Outputs:** `data/clean/PANEL.csv` (primary), `codebook_clean.xlsx`; path in `CHECKS_CHECKLIST_2026-07-07.md`.

**6. Open items:** (1) the id-fix log lists 32 corrections but the codebook shows 30 -- same fixes,
2 counted at both waves; cosmetic. (2) none affect the data.

**7. The ask:** review `run_merge.R` + `config.R`, spot-check `PANEL.csv`; on your OK I cut the lock
bundle and record USER-LOCKED.
