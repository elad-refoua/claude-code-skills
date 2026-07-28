---
name: artifact-lock-7clean
description: |
  Lock a derived artifact against approved source(s)-of-truth via 7 consecutive
  clean audits by independent hostile agents. Phase 0: user explicitly approves
  each source (with SHA256). When sources >= 2, user ranks them and the skill
  runs a 7-clean alignment of each secondary against the master BEFORE the
  product audit begins. Every CLEAN round also runs a behavioral smoke-test of
  the product (run / parse / open). The audit explicitly enumerates source
  requirements and flags silent omissions as CRITICAL. Optional build-and-audit
  mode. Hash-drift detection on every round. On completion: immutable lock
  bundle (zip + git tag). State persists across sessions at
  `.artifact-lock/state.json`.

  USE WHEN finalizing any artifact derived from a locked spec:
  - analysis code derived from a locked analysis plan (+ pre-reg)
  - questionnaire + codebook derived from a questionnaire-decision document
  - manuscript edits + reviewer response derived from a "how to answer" decision
  - pre-registration derived from a locked analysis plan
  - IRB protocol derived from a study design document

  TRIGGERS:
  English: "lock this", "7-clean audit", "freeze for submission", "audit until clean", "build and lock"
  Hebrew:  "נעל את זה", "בדיקת 7 נקיים", "בדיקה לפני הגשה", "פרוטוקול 7 נקיים", "בנה ונעל"
---

# artifact-lock-7clean — Lock a derived artifact with 7-consecutive-clean discipline

This skill enforces that any high-stakes derived artifact is genuinely aligned with
its locked source(s)-of-truth before it ships. It generalizes the precursor
`manuscript-finalize-3clean` from manuscripts-only / 3-clean to ANY derived artifact
/ N-clean (default 7) and adds hash drift, multi-source alignment, behavioral
verification, negative coverage, build mode, and immutable lock bundles.

The artifact is "locked" only after 7 consecutive CLEAN audit rounds by
independent hostile agents, with each round including both structural alignment
and behavioral smoke-testing.

---

## 1. The protocol in 10 lines

1. User invokes (`lock with <N> clean` and `mode=build-and-audit` are optional).
2. **Phase 0 — Approve each source** end-to-end. Store SHA256 + verbatim approval message.
3. **Rank sources by authority** (if N >= 2).
4. **Phase 0.5 — Source-vs-source 7-clean** alignment of each secondary against the master.
5. Branch: `audit-only` (user supplies product) OR `build-and-audit` (skill builds draft → user reviews).
6. **Behavioral-check setup** — infer smoke-test from product type, or ask user once.
7. **Product audit loop** — per round: hash check → fresh agent runs Stage-A negative coverage + Stage-B structural audit → on CLEAN structural, run smoke-test → CLEAN +1 / NOT CLEAN reset 0 + apply fixes.
8. At `counter == N`, build the **lock bundle** (zip + git tag).
9. Print full audit trail. Exit.
10. The artifact is locked. Hash any source again later → re-lock required.

---

## 2. State file

**Location:** `<project-root>/.artifact-lock/state.json` (single active lock per project; archived: `state_archived_<date>.json`).

```json
{
  "mode": "audit-only",
  "required_clean_rounds": 7,
  "multi_source_strategy": "pairwise_vs_master",
  "sources": [
    {
      "id": "S0",
      "rank": 0,
      "role": "master",
      "path": "<project-root>/...path/to/source_master",
      "sha256": "<hex>",
      "approved_by_user": true,
      "approved_on": "2026-05-31T14:00:00Z",
      "approval_message": "<verbatim user text>"
    },
    {
      "id": "S1",
      "rank": 1,
      "role": "secondary",
      "path": "<project-root>/...path/to/source_secondary",
      "sha256": "<hex>",
      "approved_by_user": true,
      "approved_on": "2026-05-31T14:05:00Z",
      "approval_message": "<verbatim user text>"
    }
  ],
  "source_alignment": {
    "S1_vs_S0": {
      "counter": 0,
      "completed": false,
      "rounds": [
        {"n": 1, "verdict": "NOT CLEAN",
         "hash_drift_detected": false,
         "findings_presented": [
           {"topic": "HTC threshold", "S0_says": "0.75", "S1_says": "0.84",
            "user_decision": "edit_S1_to_match_S0", "applied": true}
         ]
        },
        {"n": 2, "verdict": "CLEAN"}
      ]
    }
  },
  "source_reconciliations": [
    {
      "topic": "decline-flag threshold wording",
      "S0_says": "20 percent",
      "S1_says": "one-fifth",
      "resolution": "agree to disagree (both phrasings accepted)",
      "decided_by_user_on": "2026-05-31T14:30:00Z"
    }
  ],
  "build": {
    "performed": false,
    "draft_path": null,
    "user_approved_draft_on": null
  },
  "derived_product": {
    "path": "<project-root>/...path/to/product"
  },
  "behavioral_check": {
    "inferred_type": "r_script",
    "command": "Rscript -e \"source('<product_path>')\"",
    "expected_outputs": ["<project>/output/results.RDS"]
  },
  "product_audit": {
    "counter": 0,
    "completed": false,
    "rounds": []
  },
  "lock_bundle": {
    "created": false,
    "path": null,
    "git_tag": null
  },
  "completed": false
}
```

Computing SHA256 (Python or PowerShell):

```python
import hashlib, pathlib
sha = hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
```

```powershell
(Get-FileHash -Path $path -Algorithm SHA256).Hash.ToLower()
```

---

## 3. Phase 0 — Source approval gate

Per source, the skill MUST:

1. Read the file end to end.
2. Surface a structured summary back to the user: list of every analysis named, every threshold cited, every section / decision / variable / scope rule, every figure mandated. (This is the same checklist Stage A of the audit agent will build, so doing it here once primes the user to spot weaknesses early.)
3. Iterate with the user until they type an EXPLICIT approval phrase. Anything ambiguous ("looks good", "fine", "OK?") is NOT enough. Required phrases:
   - English: "approved as source", "I approve this source", "lock this as source"
   - Hebrew: "אני מאשר", "מאשר כמקור אמת", "נעל כמקור"
   - Equivalent unambiguous user-typed statement.
4. Write to state: path + SHA256 + ISO-8601 UTC timestamp + verbatim user approval message.
5. Refuse to start any audit loop without explicit approval on every source.

**Why detailed approval matters:** Phase 0 is the only chance the user has to catch a flawed source BEFORE 7-clean spends rounds enforcing the flaw. The summary step is where the v7 ↔ Eshkol-approval workflow extracts its value — the user reviews and corrects the source FIRST.

---

## 4. Phase 0.5 — Source-vs-source 7-clean alignment (sources >= 2)

When the user supplies 2+ sources, the skill:

1. Asks: "Of these sources, which is the MOST authoritative (the master)? Rank the rest in descending authority order."
2. Stores ranking under `multi_source_strategy: "pairwise_vs_master"` (default) or `"cumulative"` (opt-in).
3. For each secondary source `S_i` (in rank order), runs a **7-clean loop** treating the master `S_0` as source-of-truth and `S_i` as the target.

Per round:
- Recompute hash of `S_0` and `S_i`. If either drifted → pause, return to Phase 0 for re-approval.
- Spawn fresh agent (see §9 prompt template).
- CLEAN → `source_alignment.<S_i>_vs_S_0.counter += 1`. Save.
- NOT CLEAN → present each finding to the user one-by-one:
  - Option A: "edit `S_i` to match `S_0`" (most common — secondary should align to authority)
  - Option B: "edit `S_0`" (rare; forces Phase 0 re-approval of master, resets every downstream loop)
  - Option C: "agree to disagree — record reconciliation" (writes to `source_reconciliations[]`; future audits skip this topic for THIS pair)
  - Counter resets to 0 after fixes are applied.
- When counter reaches `required_clean_rounds` for `S_i`, move on to `S_{i+1}`.

Only after EVERY secondary source has completed 7 CLEAN does the skill proceed to product audit.

**Cumulative variant** (`multi_source_strategy: "cumulative"`): `S_2` is audited against the validated `{S_0, S_1}` pair instead of just `S_0`. Opt-in — pairwise is default for simplicity.

---

## 5. Build-and-audit mode

Invoked with `mode=build-and-audit`. Used when the user wants the skill to ALSO produce the derived product from the approved (and aligned) source-set.

1. After Phase 0 (and Phase 0.5 if applicable), skill spawns a build agent (see §10).
2. Build agent writes the draft to `<project>/.artifact-lock/draft_<YYYY-MM-DD>/<filename>`.
3. Skill presents the draft to the user. User can:
   - Approve the draft path → state records `build.user_approved_draft_on` + sets `derived_product.path` to the draft path (or a user-supplied canonical path).
   - Reject + give feedback → re-spawn build agent with corrections; loop until approval.
4. Once the draft is approved, the product audit loop begins (§7).

**The build agent is NOT bound by 7-clean discipline** — its draft is just the starting point. The 7-clean discipline is enforced by the audit loop that runs AFTER the build.

---

## 6. Behavioral-check setup

Once the product path is known, infer a smoke-test from the file type:

| Product type | Default smoke-test |
|---|---|
| `.R` file or directory of `.R` files | `Rscript -e "source('<path>')"` per script in pipeline order; assert exit 0; verify `expected_outputs` paths exist |
| `.py` file | `python -c "import importlib.util; spec=importlib.util.spec_from_file_location('m','<path>'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)"`; assert exit 0 |
| `.docx` manuscript | `python -c "from docx import Document; d=Document('<path>'); print(len(d.paragraphs))"`; assert exit 0; check XML validity |
| OSF AsPredicted JSON / Markdown | parse JSON; assert all required AsPredicted fields present (`questions[1..11]`) |
| Qualtrics QSF | load + parse; assert no schema errors; assert all questions referenced in source codebook exist |
| Unknown | ask user once at Phase 1 for a one-liner Bash command (stored under `behavioral_check.command`) |

If the source spec names specific output files (e.g., "after step5 the script writes `output/htc_table.csv`"), record those paths under `behavioral_check.expected_outputs` and assert each exists after the smoke-test succeeds.

---

## 7. Hash-drift detection

At the start of every audit round (in any loop), the skill recomputes SHA256 for every source file and compares against `sources[*].sha256`. If any source's hash differs:

1. Pause the loop.
2. Surface to user: "Source `<path>` has changed since you approved it. Hash was `<old>`, is now `<new>`."
3. Show a diff (optional — if the source is text-based, `git diff` style).
4. Require fresh explicit approval (see §3). Re-write hash + timestamp + new approval message.
5. If sources >= 2 AND the changed source is the master OR involved in alignment: reset all affected `source_alignment` loops to counter 0 and re-run Phase 0.5.
6. Counter of the current loop does NOT auto-reset on hash change — it resets only if the re-approval brings real changes (the user effectively confirms a re-lock). The skill asks: "Should the product-audit counter reset to 0 given this change?" Default = yes.

---

## 8. Negative-coverage check (silent-omission detector)

This is the most important addition over the precursor skill. The audit agent must NEVER skip Stage A.

The agent's brief (see §9) requires it to FIRST enumerate every requirement stated in the source-of-truth (every analysis, threshold, section, variable, decision rule) and verify each is addressed in the target. Missing items become CRITICAL findings labeled "silent omission".

This catches the failure mode where the product looks aligned because everything IT contains matches the source, but it silently omits something the source mandated. Stage-A explicitly enumerates → silent omissions cannot hide.

---

## 9. Audit-agent prompt template (reused in BOTH source-vs-source and product-audit loops)

Each round spawns ONE fresh `general-purpose` agent (model: opus) with this brief. Inputs are the only thing that changes between rounds; the agent receives NO prior verdicts, NO counter, NO fix history.

```
ROLE: Independent, MAXIMALLY HOSTILE quality-control auditor.

INPUTS:
- SOURCE-OF-TRUTH for this round (user-approved):
    {primary_source_path}
    [+ supporting sources if multi_source_strategy is "cumulative"]
- RECONCILIATIONS already accepted (skip these from findings):
    - {topic}: {resolution}
- TARGET under audit: {target_path}
  (May be a secondary source being aligned to the master, OR the final derived product.)

YOUR JOB IS IN TWO STAGES.

STAGE A - NEGATIVE-COVERAGE CHECKLIST (build first, before listing misalignments):
Enumerate EVERY distinct requirement stated in the SOURCE-OF-TRUTH. Categories:
- Every analysis named (variable, model, statistic)
- Every threshold cited (numeric value + provenance)
- Every section / figure / table / appendix mandated
- Every variable required (name, type, scoring direction)
- Every decision rule the source commits to (e.g., "if X, then Y")
- Every constraint (e.g., "must hold for all participants where Z")

For each requirement, verify the TARGET addresses it. Missing items are CRITICAL ("silent omission").

STAGE B - STRUCTURAL ALIGNMENT (after the checklist):
Re-derive expectations from the SOURCE independently. Check whether the TARGET matches what's there.
List misalignments by SEVERITY x FIX-SIZE.

SEVERITY:
- CRITICAL: source says X, target says NOT X on a semantic / logic / threshold / scope point; OR silent omission of a source requirement.
- MAJOR: real drift but smaller (e.g., missing minor section, wrong wording on a side claim).
- MINOR: cosmetic only, does NOT affect verdict.

FIX-SIZE (per finding, only for CRITICAL + MAJOR):
- LIGHT: one-line / rename / typo / column reorder / single-value substitute. Safe to auto-apply.
- BIG: semantic / logic / threshold / scope change. Requires user approval.

CLEAN = no CRITICAL + no MAJOR.

OUTPUT FORMAT (markdown):

# VERDICT: CLEAN | NOT CLEAN

## Source-requirement checklist (from Stage A)
Table or list, for each requirement: addressed_in_target (Y/N), evidence_or_note.

## CRITICAL findings (silent omissions + alignment violations)
For each: {file:line, source citation, what's wrong, expected from source, proposed fix, fix_size: LIGHT|BIG}

## MAJOR findings
Same format.

## MINOR (cosmetic; for transparency only)

## Summary
2-3 sentences.

BE HOSTILE. Don't trust anything you weren't shown. Re-derive everything from raw source.
Pretend you are a peer reviewer / journal editor / OSF reviewer / advisor looking for any
reason to reject the lock. The Stage-A checklist is NOT OPTIONAL — it is the most important
deliverable. If a requirement is missing from the target, it is ALWAYS CRITICAL even if
small.
```

After the agent returns, the skill:

1. Parses the verdict.
2. If structural CLEAN: runs the behavioral smoke-test. If smoke-test exits 0 AND all `expected_outputs` exist → round is CLEAN. Counter += 1. If smoke-test fails → round is NOT CLEAN with one CRITICAL finding: "behavioral check failed: <error>".
3. If structural NOT CLEAN: auto-applies LIGHT findings (records each in `light_findings_auto_applied`), presents BIG findings one-by-one to the user, applies approved fixes. Counter resets to 0.

---

## 10. Build-agent prompt template (build-and-audit mode only)

```
ROLE: Faithful implementer.

INPUTS:
- APPROVED AND ALIGNED SOURCE-SET:
    1. {master_source_path} (rank 0)
    2. {secondary_source_path} (rank 1, aligned to master via 7-clean)
    ...
- RECONCILIATIONS:
    - {topic}: {resolution}
- TARGET PRODUCT TYPE: {inferred from user request — e.g., "R analysis script", "Qualtrics survey JSON", "manuscript revision"}
- TARGET PRODUCT PATH: {project}/.artifact-lock/draft_<date>/{filename}

YOUR JOB:
Produce the derived product faithfully from the approved + aligned source(s), honoring reconciliations.
Do NOT introduce design decisions that are absent from the sources — if you encounter a gap, STOP and ask the user.
Write the result to the TARGET PRODUCT PATH.

When done, output a brief summary of what was generated and a list of any choices that should be flagged for user review.
```

---

## 11. Counter / reset rule

For every loop (source-alignment and product-audit):

- **CLEAN** verdict (no CRITICAL, no MAJOR, smoke-test passed) → `counter += 1`.
- **NOT CLEAN** verdict (any CRITICAL or MAJOR, OR smoke-test failed) → `counter = 0`. Apply LIGHT auto-fixes. Present BIG findings to user.

When `counter == required_clean_rounds`, the loop completes. For source-alignment loops, move on to the next secondary or to product audit. For the product-audit loop, build the lock bundle (§12).

**Anti-pattern:** the counter must NEVER be manually advanced by the assistant. If the user says "this is fine, skip ahead", the skill MUST refuse and explain the discipline. The whole point is independent rounds. Manual advancement defeats it.

---

## 12. Lock bundle on completion

When `product_audit.counter == required_clean_rounds`:

1. Set `product_audit.completed: true`.
2. Build the bundle: zip everything in `<project>/.artifact-lock/locked_<YYYY-MM-DD>.zip` containing:
   - Every source file (paths from `sources[*].path`)
   - The product file/dir (from `derived_product.path`)
   - The full `state.json`
   - Behavioral check logs (stdout/stderr captures from the last 7 rounds)
3. Commit the current state.json + any final fixes to git with message:
   `lock(artifact-lock-<date>): 7-clean passed for <product_path>`
4. Tag HEAD: `git tag artifact-lock-<YYYY-MM-DD>` (or with a counter suffix if a tag for that date already exists).
5. Write `lock_bundle.path` and `lock_bundle.git_tag` to state.
6. Set top-level `completed: true`.
7. Print the FULL audit trail: every source-alignment round + every product round + every finding + every fix + bundle path + git tag.

The bundle is the deliverable. If anything drifts afterward, the user can diff against the bundle to prove what passed.

---

## 13. Cross-session resume

On any invocation, read `<project>/.artifact-lock/state.json` first:

- If file missing: this is a fresh invocation. Proceed from §3.
- If file present and `completed: false`:
  - Identify the active loop (the latest one with `counter < required_clean_rounds`).
  - Recompute source hashes — if drifted, return to Phase 0.
  - Resume that loop at round `counter + 1`.
- If file present and `completed: true`:
  - Inform the user: "An active lock exists from <date>, bundled at <path>, tagged <tag>."
  - Ask: "Start a new lock (archive this one)? Re-verify the existing lock? Or abort?"

---

## 14. Product-type playbook (the agent picks this up from the source + product types)

The audit agent infers what to check from file types alone — no profile flags. The notes below are reference material the agent naturally reaches for when given the relevant inputs. They are NOT separate modes.

### .docx manuscript + .md decision/reviewer-response document

When the product is a `.docx` manuscript and the source is a "how to answer" decision document or reviewer-response plan, the hostile audit naturally covers:

- **Flow & sense:** prose coherence end-to-end; hypotheses (if a/b/c) intact across Method / Results / Discussion; tense + voice consistent; no orphan paragraphs or dangling references.
- **Numbers vs pipeline:** every numeric value in the manuscript MUST trace to a pipeline traceability source (Results CSV, analysis output, prior approved draft). Fabricated or untraced numbers = CRITICAL. Internal consistency: Abstract ↔ Method ↔ Results ↔ Discussion ↔ Tables ↔ Figures.
- **Coverage + attribution:** every reviewer comment / advisor request addressed in body text OR tracked-change comment. Claude-authored Word comments must cite ONLY approved sources (`per Reviewer #N`, `per pipeline`, `per <advisor>`, etc.) and must NEVER leak internal scaffolding (no "audit fix", "V3/V4/V5", "round N", "pass N").
- **References integrity:** every in-text citation has a matching reference list entry; no orphan refs; no year mismatches; no duplicates.
- **XML hygiene:** `document.xml` + `comments.xml` parse cleanly; every `<w:commentRangeStart>` has matching `<w:commentRangeEnd>` AND `<w:commentReference>`; every comment ID in document.xml exists in comments.xml (and vice versa); all `<w:ins>` / `<w:del>` carry valid author + date.

#### Accept-all extraction code (paste into the agent's audit prompt when product is .docx with tracked changes)

The default `python-docx` extraction merges deletion + insertion text, producing FALSE positives like `phasecheck`, `0.071after RC`. The agent MUST use accept-all extraction (skip `<w:del>` subtrees, keep `<w:ins>` subtrees):

```python
import zipfile
from xml.etree import ElementTree as ET
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
W = '{' + NS['w'] + '}'

with zipfile.ZipFile('<docx_path>') as z:
    doc = ET.fromstring(z.read('word/document.xml'))

def extract_accept_all(p):
    parts = []
    def walk(el):
        tag = el.tag.split('}')[-1]
        if tag == 'del':
            return
        if tag == 't':
            parts.append(el.text or '')
        for c in el:
            walk(c)
    walk(p)
    return ''.join(parts)

body = doc.find(W + 'body')
text = '\n'.join(extract_accept_all(p) for p in body.iter(W + 'p'))
```

#### Pre-existing accepted items

The user may pre-declare items that are known and acceptable (will be fixed at copy-editing): table row order, p-value style mixing, "et al." style choices, alphabetical placement of one reference. Auditors that don't know these will reset the counter forever. Record under `state.pre_accepted_items[]` and include the list in every audit prompt for .docx products.

#### Figure handling

When a manuscript change touches a figure: the agent MUST visually inspect each figure file with the Read tool (Opus is multimodal). PASS verdicts on figures based only on byte-comparison are insufficient — they may miss cropped labels, awkward aspect ratios, unreadable text.

When asked to remove ONE element from a figure: change ONLY that element. Do not redesign. Find the original ggplot in the canonical pipeline, copy verbatim, remove ONLY the specific element, keep all other layers / themes / dimensions / scales identical.

### .R or .py code + .md analysis plan

- Negative-coverage: every analysis, threshold, sample-handling rule, expected output the plan mentions → present in code.
- Provenance comments: every locked threshold should carry a comment citing the source section (e.g., `# v7 sec 4.II.4`).
- Refactor invariants: if the plan renames `htc_primary_floor` → `htc_strong_threshold`, the audit grep'd EVERY occurrence in the codebase.
- Tibble schema consistency: all branches of a function returning a tibble must produce the same column set.

### Pre-registration (OSF AsPredicted JSON / Markdown) + analysis plan

- Negative-coverage: every analysis named in the plan → represented in the pre-reg (questions #6, #7, #8, #11).
- AsPredicted's 11-question schema requirements must all be filled.
- "It's complicated" answers must point at the supplement.

### Qualtrics QSF + questionnaire-decision document

- Every item in the codebook exists in the QSF with matching wording.
- Scale anchors match the decision document.
- Skip logic matches the documented flow.

---

## 15. Anti-patterns

The skill MUST refuse to do any of the following, even if the user asks:

- **Counter manipulation.** "This counts as CLEAN, skip ahead." NO. The discipline is independent rounds. If you skip, the lock is meaningless.
- **Weak Phase-0 approval.** "Looks good." NO. The user must explicitly type one of the approved phrases or an unambiguous equivalent.
- **Parallel rounds.** Running 7 agents in parallel does NOT count as 7 consecutive cleans. It counts as ONE round with 7 reviewers. Rounds must be sequential to preserve independence and to let fixes from one round be re-audited by the next.
- **Skipping source-vs-source alignment** when sources >= 2. The whole point of multi-source workflows is that the secondaries align with the master; skipping that means later product-audit findings will conflict with reality.
- **Auto-applying BIG fixes** without user check-in. LIGHT fixes are by definition single-line / rename / typo. BIG fixes by definition need judgment.
- **Skipping hash check.** If the user edited the source mid-loop, the audit is auditing the wrong thing. Always re-hash at round start.
- **Skipping the behavioral check.** Structural CLEAN without behavioral CLEAN ships code that crashes / a docx that won't open / a JSON that won't parse.
- **Skipping Stage A** (negative coverage). Stage A catches silent omissions; without it, the agent finds what's wrong but misses what's missing.

---

## 16. Model requirement: Opus for audit agents, never Sonnet

Use `model: "opus"` for every audit and build agent spawned by this skill. Sonnet's false-positive rate on hostile audits is too high — Elad explicitly demanded a mid-session restart with Opus on Paper-1 Treatment Saturation finalization, May 2026, after Sonnet flagged dozens of fake "merge artifacts" that turned out to be extraction bugs. Sonnet also missed real structural XML defects that Opus caught.

---

## 17. When NOT to use this skill

- Quick drafts (no review pressure, no advisor or journal eyes on it yet).
- Internal working documents.
- Documents where one auditor pass is sufficient confidence.
- Tasks where there is no clear single source-of-truth (use brainstorming first; come back when there is one).

Use lighter-friction skills for routine work — e.g., `apa-manuscript` for APA formatting, `r-analysis` for ad-hoc R scripts, `manuscript-qc` for pre-submission QC without the multi-round audit overhead.

---

## 18. Provenance

This skill replaces `manuscript-finalize-3clean` (2026-04 → 2026-05). Major changes:

- N raised from 3 to 7 by default (configurable).
- Generalized from manuscripts-only to ANY derived artifact (code, pre-reg, questionnaire, manuscript, etc.).
- Added: hash-drift detection, hierarchical multi-source 7-clean alignment, build-and-audit mode, behavioral smoke-test, negative-coverage check, immutable lock bundle.
- Manuscript-specific lessons (5 audit dimensions, accept-all extraction, 4-source attribution, figure visual inspection) are now reference material under §14 the audit agent picks up from the source/product file types — no separate profile system.

Lessons baked into this skill:

- Round 8 of Paper-1 Treatment Saturation (May 2026): 4 clean + 1 numbers-drift would have shipped a wrong 3-level piecewise value (0.1211 vs 0.1141). Without the 3-consecutive rule, the defect reaches the journal. The discipline saved it.
- Study 5 R-pipeline alignment (May 2026): 6 rounds were needed before 3 consecutive CLEAN. Round 3 caught a PGR halt missing — without counter pressure, Rounds 4-5-6 wouldn't have happened, the defect would have shipped.
- Multi-source alignment lesson (May 2026): when sources >= 2, the alignment between sources is itself a 7-clean discipline, not a one-shot check.
