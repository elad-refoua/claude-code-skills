# <DELIVERABLE NAME> -- <YYYY-MM-DD>

<!--
WHEN TO USE: Drop this at the ROOT of every dated R deliverable folder as the INDEX (R Style
Constitution rule 12: "the creation is accompanied by documentation and a tidy, not-overloaded
folder"). It is the single-glance map: what this folder is, the small fixed taxonomy, where each
kind of file lives, and the archive discipline. If someone can understand the folder from this one
file without scrolling through it, the folder is tidy enough. Taxonomy distilled from a good linear
cleaning-pipeline folder + a staged cleaning project (step-save + codebook-adjacency + _ARCHIVE).

HOUSE RULES: ASCII only. Dated folder name (e.g. `cleaning_2026-07-07`, never a bare descriptive
name). Intermediates NEVER at the folder root -- they go in step_outputs/. Superseded material is
MOVED to _ARCHIVE/, never deleted. Keep this file under ~1 screen; if the folder needs more
explaining than that, the folder is overloaded -- split it or archive.
-->

**What this folder is:** <one sentence -- e.g. "the v6 cleaning pipeline that turns the 14 raw
Qualtrics surveys into one clean, scored, organized dataset.">
**Source of truth:** `<docs/PLAN_vN_YYYY-MM-DD.md>` (the approved plan everything here is built from).
**Status:** <AUDIT-PASSED (n/n clean), awaiting the reviewer's review | USER-LOCKED YYYY-MM-DD (git tag <tag>)>.
**Start here:** read `<docs/REVIEW_PACKET_YYYY-MM-DD.md>` (plain language), then the review path in
`<docs/CHECKS_CHECKLIST_YYYY-MM-DD.md>`, then the code.

---

## The taxonomy (small and fixed -- 4 places for things)

| Folder | Holds | Rule |
|---|---|---|
| `code/` | the pipeline: `run_<name>.R` (linear script) + `config.R` (pure data) | the ONLY place logic lives; read top to bottom = execution order |
| `step_outputs/` | every intermediate, saved as RDS + CSV, named `*_after_step_N.*` | one save per Step; NEVER dumped at the folder root |
| `step_checks/` | one PASS/FAIL text file per Step (`step_N_<what>.txt`) | the mechanical evidence Part A of the checks checklist reads |
| `docs/` | the plan pointer, REVIEW_PACKET, CHECKS_CHECKLIST, Results.md, codebook, VERIFICATION_REPORT | everything a human reads about the pipeline |
| `data/raw_frozen_<date>/` | the immutable raw pull + `MANIFEST.json` + `MD5SUMS.txt` | set read-only; never edited in place; the one thing kept apart from `code/` |
| `_ARCHIVE/` | superseded versions + an `ARCHIVE_MANIFEST.md` saying what moved and when | supersede, NEVER delete; nothing important lives ONLY here |

Anything that does not fit one of these rows probably does not belong in this folder.

## What is in here right now (the index)

<Keep this list current. One line each. This is the "single glance" -- if it grows past a screen,
the folder is overloaded.>

- `code/run_<name>.R` -- <the linear pipeline, Steps 0-N>
- `code/config.R` -- <pure data: paths, ids, item lists, thresholds>
- `docs/REVIEW_PACKET_<date>.md` (+ `.docx`) -- <plain-language review packet for the reviewer>
- `docs/CHECKS_CHECKLIST_<date>.md` -- <the staged review path + sign-off rule>
- `docs/Results.md` -- <glue-generated results narrative + tables + file index>
- `data/raw_frozen_<date>/` -- <the N frozen raw files + checksums (read-only)>
- `step_outputs/` -- <N intermediate RDS+CSV>
- `step_checks/` -- <N PASS/FAIL files>
- `_ARCHIVE/` -- <superseded material; see ARCHIVE_MANIFEST.md>

## Refactor / re-run discipline

- A refactor NEVER overwrites an original output: new script (`run_<name>_v2.R`) -> new output path
  (`*_after_step_N_v2.*`) -> a `compare_v1_v2.R` that diffs cell-by-cell -> report PASS/FAIL. Only
  after the diff is clean do we propose replacing the original, and the `_v2` stays as evidence.
- Re-running the pipeline regenerates `step_outputs/` and `step_checks/`; it does NOT touch
  `data/raw_frozen_<date>/` (immutable) or `_ARCHIVE/`.

---

### Filled mini-example (the shape, concrete)

```
merge_waves_2026-07-07/
  README.md                      <- this file (the index)
  code/
    run_merge.R                  <- 4-step linear pipeline (0 loops, 0 functions)
    config.R                     <- 3 wave ids + id-fix map, no logic
  data/
    raw_frozen_2026-07-07/       <- 3 frozen wave CSVs + MANIFEST.json + MD5SUMS.txt (read-only)
  step_outputs/
    panel_after_step_1.rds/.csv
    panel_after_step_2.rds/.csv
    panel_after_step_3.rds/.csv
  step_checks/
    step_0_freeze.txt            <- PASS
    step_2_join.txt              <- PASS (380/380 ids matched)
    step_3_recon.txt             <- PASS (412 = 380 + 32)
  docs/
    MERGE_PLAN_v2_2026-07-07.md  <- source of truth (the approved plan)
    REVIEW_PACKET_2026-07-07.md  (+ .docx)
    CHECKS_CHECKLIST_2026-07-07.md
    Results.md                   <- glue-generated
    codebook_clean.xlsx
  _ARCHIVE/
    ARCHIVE_MANIFEST.md          <- "run_merge_v1.R moved here 2026-07-07, superseded by v2"
    run_merge_v1.R
```

Status: AUDIT-PASSED (7/7 clean), awaiting review. Start at `docs/REVIEW_PACKET_2026-07-07.md`.
