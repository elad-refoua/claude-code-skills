# CHECKS CHECKLIST -- <PIPELINE NAME> (<YYYY-MM-DD>)

<!--
WHEN TO USE: Ship this file with EVERY R pipeline (R Style Constitution rule 6). It is the
staged, human-readable review path that turns "trust me, it works" into "here is exactly what to
check, where, and how long it takes." Two audiences in one document: Part A is the mechanical
record of what the code already verified (PASS/FAIL, straight from step_checks/); Part B is the
ordered path a human reviewer (usually <USER>) walks to reach USER-LOCK. Organizing logic modeled on
a "complete review path" appendix -- capture the STRUCTURE, write your own content.

HOUSE RULES for this file: ASCII only (no unicode dashes/arrows/checkmarks -- use - / -> / [x]).
Bold the highest-priority rows. Every file path is real and relative to the folder root (or
absolute where it leaves the folder). Fill in the counts -- do not leave <...> placeholders in a
delivered checklist.
-->

**What this is:** the complete verification path for the `<pipeline>` deliverable -- every automated
check the code runs, plus the exact order a human should review it in, ending in a sign-off rule.
**Source of truth:** `<docs/PLAN_vN_YYYY-MM-DD.md>` (the approved plan this pipeline was built from).
**Status:** `AUDIT-PASSED (<n>/<n> consecutive clean)` -- awaiting personal review. NOT yet USER-LOCKED.

**THE RULE (read first):** see ALL the code, from the raw data through every intermediate to the
numbers that land in the output, and only THEN the write-up. This is the full path, in review order.
Do not skip a stage because the next one "looks fine."

**Time budget:** Stage 0 ~<15> min | Stage 1 ~<90> min | Stage 2 ~<30> min | Stage 3 ~<10> min. Total ~<2.5> h.

---

## Part A -- what the code already verified (mechanical, from `step_checks/`)

One row per automated gate. Status is copied verbatim from the PASS/FAIL file each step writes; a
FAIL here means the pipeline `stop()`ed and never produced final output. Regenerate this table from
`step_checks/` after every run -- it is evidence, not decoration.

| # | Gate | File that proves it | What it asserts | Status |
|---|---|---|---|---|
| A1 | <freeze> | `step_checks/step_0_freeze.txt` | <all N raw files pulled, checksummed, read-only> | <PASS> |
| A2 | <keep gate> | `step_checks/step_1_keep.txt` | <rows kept <= rows in; no rows invented> | <PASS> |
| A3 | <row reconciliation> | `step_checks/step_2_drops.txt` | <raw = kept + sum(drop reasons); no unexplained loss> | <PASS> |
| An | <final invariant> | `step_checks/step_N_sanity.txt` | <wide <-> long agree cell-for-cell, 0 mismatches> | <PASS> |

Bottom line (fill in): `<all A-rows PASS; 0 stop()s fired; every dropped row has a logged reason.>`

---

## Part B -- your review path (staged; read in this order)

Each row = a numbered item | the file | what it does | the exact spots to scrutinize. The last
column is yours to tick. Bold rows are the ones that matter most -- if time is short, do those.

### Stage 0 -- the inputs (verify the starting point, ~<15> min)

| # | What | Where | Spots to scrutinize | Checked |
|---|---|---|---|---|
| 0.1 | <the frozen raw> | `<data/raw_frozen_YYYY-MM-DD/>` + `MANIFEST.json` | <path points to the frozen export; row counts + sha256 match; files are read-only> | [ ] |
| 0.2 | <the config / codebook> | `<code/config.R>` | <every threshold carries a provenance comment; item lists match the plan appendix> | [ ] |

### Stage 1 -- the pipeline, raw -> results (the deep read, ~<90> min)

| # | File | What it does | Spots to scrutinize | Checked |
|---|---|---|---|---|
| **1.1** | **`<code/run_clean.R>`** | <the linear pipeline, Steps 0-N top to bottom> | <read top to bottom; each `## Step N ----` matches the plan step; no bare row/col indices without an adjacent assert> | [ ] |
| 1.2 | `<code/config.R>` | <pure data: paths, IDs, item lists, thresholds> | <no logic here; every constant has provenance> | [ ] |
| 1.3 | <a step worth its own row> | `<run_clean.R Step 6>` | <the one clever/forced spot -- e.g. a positional pin that is re-derived + asserted live; confirm the assert can actually fail> | [ ] |

### Stage 2 -- the numbers that reach the write-up (~<30> min)

| # | File | Spots to scrutinize | Checked |
|---|---|---|---|
| 2.1 | `<docs/Results.md>` | <every number is glue-injected from the pipeline, none hand-typed; narrative stats match the tables> | [ ] |
| 2.2 | `<step_outputs/*_after_step_N.rds/csv>` | <spot-check that an intermediate reconciles with the counts printed on screen> | [ ] |

### Stage 3 -- the records (~<10> min)

| # | What | Where | Spots to scrutinize | Checked |
|---|---|---|---|---|
| 3.1 | <the review packet> | `<docs/REVIEW_PACKET_YYYY-MM-DD.md>` | <the plain-language step list matches the code; the open items are honestly stated> | [ ] |
| 3.2 | <the folder index> | `<INDEX.md>` | <the taxonomy is clean; nothing important is only in `_ARCHIVE/`> | [ ] |

---

## Sign-off rule (what ends the review)

- When **Stages 0-2 read clean**, the code flips from `AUDIT-PASSED` to `USER-LOCKED` on your explicit
  approval (say so, and the immutable lock bundle -- zip + git tag + sha256 -- is created and recorded
  in `PROJECT_TIMELINE.md`).
- **Findings triage:** a finding in a Stage-2/3 file (a write-up wording, an open item) can be fixed
  directly -- your review IS its lock gate. A finding in a Stage-0/1 file (data, config, pipeline
  logic) BREAKS the audit lock and triggers a fresh re-audit before it can be locked.
- Until you have personally read it, the honest status is "AUDIT-PASSED, awaiting your review" --
  never "locked."

---

### Filled mini-example (a 3-survey merge, so the shape is concrete)

**What this is:** verification path for `merge_waves` (three Qualtrics waves -> one clean panel).
**Source of truth:** `docs/MERGE_PLAN_v2_2026-07-07.md`. **Status:** AUDIT-PASSED (7/7 clean).
**Time budget:** Stage 0 ~10 min | Stage 1 ~40 min | Stage 2 ~15 min. Total ~65 min.

Part A (mechanical):

| # | Gate | File | What it asserts | Status |
|---|---|---|---|---|
| A1 | freeze | `step_checks/step_0_freeze.txt` | 3/3 waves pulled, checksummed, read-only | PASS |
| A2 | id join | `step_checks/step_2_join.txt` | every merged id exists in all 3 waves; 0 orphans | PASS |
| A3 | row math | `step_checks/step_3_recon.txt` | 412 raw = 380 kept + 32 logged drops | PASS |

Part B (review path), Stage 1:

| # | File | What it does | Spots to scrutinize | Checked |
|---|---|---|---|---|
| **1.1** | **`code/run_merge.R`** | the 4-step linear merge | Step 2 join key is `id_canonical` (semantic, not row position); Step 3 drop reasons sum to the raw total | [ ] |
| 1.2 | `code/config.R` | the 3 wave ids + the id-fix map | each id-fix has a "why" comment; no logic | [ ] |

Sign-off: Stages 0-1 clean -> `run_merge.R` + `config.R` flip to USER-LOCKED on the reviewer's OK; a wording
fix in `Results.md` is done directly; any change to the join logic in Step 2 re-opens the 7-clean audit.
