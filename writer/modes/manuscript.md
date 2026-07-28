# Mode: Manuscript

Primary writing mode. APA-style academic manuscripts for psychology journals.

**Trigger keywords**: "write Introduction/Method/Results/Discussion/Abstract", "paper", "manuscript", "journal article"

---

## What This Mode Does

When writing a manuscript section, the agent:

1. **Reads analysis output** (tables, Results.md, R script output)
2. **Reads references.csv** (check the `relevance` column for narrative arc)
3. **Loads journal profile** if a target journal is specified
4. **Builds the Argument Map** (mandatory before writing -- see argument-map-template.md)
5. **Executes the five-move Working Method defined in AGENT.md** (Story Architecture -> Write -> Independent Review with 5 verification passes -> Deterministic Gate -> Learn). AGENT.md is the canonical source for the workflow, pass counts, and iteration budgets — do not duplicate its numbers here.
6. **Applies all writing quality rules** from writing-rules.md to prose
7. **Spawns reviewer sub-agent** for manuscript sections (revision budget per AGENT.md Move 3)
8. **Updates session context** (.writer-context.yaml + Paper_Outline.md)
9. **Outputs** a complete, runnable R script producing .md + .docx

---

## CRITICAL: Results ALWAYS Come From Code

**NEVER write manuscript text as plain Markdown.** ALWAYS generate from an R script that:
- Loads analysis CSV tables
- Extracts statistics into R variables
- Builds prose using `glue()` with embedded `{variable}` references
- Outputs both Markdown (via `writeLines()`) and Word (via `officer::body_add_par()`)

Every statistic traces directly to analysis output. No hardcoded numbers.

For R code architecture, load the r-coder agent stack (`agents/r-coder/AGENT.md`) plus the `r-analysis` and `r-results-narrative` skills — recommended for all substantive R code.

---

## Living Outline: Paper_Outline.md (Mandatory)

Every paper has a `Paper_Outline.md` in its manuscript folder. This is a LIVING document
that combines the Argument Map and Narrative Outline into a single, continuously updated
source of truth for the paper's structure.

### What it contains
- Core Story (one sentence)
- Narrative Arc (5 bullets: tension, challenge, framework, answers, resolution)
- Section-by-Section Argument Map (table per section with: #, Claim, Evidence/References, WHY HERE, Altitude, Shape, Status)
- Verification Checklist (thread -> introduced -> delivered -> closed -> status)
- Echoing Rule (Introduction opens with... / Discussion closes with...)

### Update rules

| Event | What updates in the outline |
|-------|---------------------------|
| Section written for the first time | Status -> "written", actual claims/stats filled in |
| Section revised | Claims/evidence updated to match revision, verification checklist re-checked |
| The user gives feedback | Affected paragraphs flagged, notes added |
| New finding added or finding changes | Entire verification checklist re-run: do all threads still connect? |
| Reference added/removed | Evidence column updated |
| Reverse sync (user edited manuscript) | Agent reads edits, updates outline to match actual text |

### Where it lives
- Saved as `Paper_Outline.md` in the manuscript folder (alongside R scripts, references.csv)
- Referenced in `.writer-context.yaml` under `files.paper_outline`
- Read at startup (Loading Sequence Step 3), updated at end of session
- When writing ANY section, check the outline first and update it after

---

## Session Context: .writer-context.yaml

The writer agent reads `.writer-context.yaml` from the manuscript folder at startup.
This file tracks: paper metadata, journal target, file locations, progress, terminology, and study design.

### What it contains
- `paper`: title, short_name, type (empirical/conceptual/review/brief-report)
- `journal`: name, profile yaml reference
- `authors`: author list
- `files`: paths to references_csv, analysis_output, paper_outline, generated_scripts
- `progress`: status per section (not-started/in-progress/complete/revised), last session info
- `terminology`: consistent term usage (construct name, group labels, framework, measure)
- `design`: type (cross-sectional), confirmatory hypotheses, exploratory analyses
- `notes`: freeform notes for next session

### Terminology enforcement
When writing, check EVERY key term against the terminology section:
- If `construct: "workload strain"` -> NEVER use "job overload", "role pressure", "work stress"
- If `group1: "app adopters"` -> NEVER switch to "mentoring-app participants" or "tool users"
When the user introduces a new key term: add to terminology, ask if it replaces or adds to existing.

### Context staleness
If `.writer-context.yaml` is older than 30 days: ask "I have context from [date] for [paper]. Still current?"
When a paper is submitted: mark `status: submitted` in context file.

See AGENT.md Loading Sequence Step 3 for when/how context is loaded.

---

**Epistemic language and analysis tags: see manuscript/domain-rules.md.**

---

## Section-Specific Rules

### Introduction
- Open with the phenomenon, not literature (Bem, 2003)
- Start with the intellectual discourse/debate, NOT prevalence statistics (Lesson 4)
- Do NOT build theory around exploratory findings (Lesson 1)
- End with aims and hypotheses

### Method
- Replication-ready, not a tutorial
- "We examined whether..." not "We hypothesize that X will predict Y"
- "Association" not "relationship" in cross-sectional designs

### Results
- Finding first, statistics in parentheses
- Embed key tables in the manuscript body (Lesson 4)
- Prose, not bullet points
- Phase labels: "Phase 1", "Phase 2" (not "Act 1", "Act 2")

### Discussion
- Open with main finding in plain language (no statistics in first sentence)
- Each paragraph: finding → prior literature → theoretical implication
- Limitations: honest, brief, most serious first

### Abstract
- Flowing prose. Problem → Method → Key Findings → Conclusion.
- No bullet points, no sub-headings (unless journal requires structured abstract)
- Write it last.

---

## Word Document Formatting (Lesson 5)

All manuscript Word output uses:
- **Font**: Times New Roman, 12pt
- **Headings**: TNR 14pt bold (H1), TNR 12pt bold (H2)
- **Line spacing**: 1.5
- Use `ms_par()` helper function, not raw `body_add_par()`

---

## R Code Readability (Lesson 6)

Every R script must be written for a reader who has never seen it before:
1. Reading guide at the top (lines 1-15)
2. Numbered section headers: `### ---- N. Section Name ----`
3. Explanatory comments before every code block
4. Self-documenting variable names (full descriptive, not abbreviations)
5. Break complex operations into named steps
6. Table column names match manuscript text
7. No magic numbers (named constants at top)

---

## Journal Adaptation

When the user specifies a target journal, load its profile from `manuscript/profiles/`.

### Available Profiles

| File | Journal |
|------|---------|
| `apa7-default.yaml` | APA 7th (baseline) |
| `jama-network-open.yaml` | JAMA Network Open |
| `cyberpsychology.yaml` | Cyberpsychology, Behavior, and Social Networking |
| `computers-human-behavior.yaml` | Computers in Human Behavior |
| `journal-of-counseling-psychology.yaml` | Journal of Counseling Psychology |

If no profile exists, search web for author guidelines and create one.

---

## Citation System

Read `manuscript/citation-guide.md` for full details.

Core rule: NEVER hardcode citations. Use `cite()`, `cite_p()`, `cite_s()` from R functions.

---

## Reverse Sync Workflow

When the user has manually edited manuscript text:
1. Read edited file AND R generation script side by side
2. Compare glue() template strings with edited text
3. Update R code templates (preserve `{variable}` references)
4. Update references.csv for new/removed citations
5. Re-run R script to verify round-trip
6. Report summary

---

## Internal Sub-Agents

See AGENT.md "Internal Sub-Agents" (canonical): paper-reader = Sonnet, reviewer = Opus (the evaluator must be >= writer capability; self-bias research), writer = Opus. Do not duplicate model assignments here.

---

**Quality verification: follows the five-move Working Method defined in AGENT.md.**

---

## Mode-Specific Anti-AI
- Epistemic language must match analysis type (see domain-rules.md)
- Stats follow finding-first pattern (see writing-rules.md Level 2)
- No metacomments ("as mentioned", "as noted")
