---
name: ref-verify
description: |
  Verify all references in an academic paper (.docx) for accuracy via web search.
  Spawns Sonnet sub-agents to independently verify each reference against online sources.
  Also exports a Zotero-compatible RIS file.

  TRIGGERS: "verify references", "check references accuracy", "תוודא הפניות",
  "בדוק הפניות", "reference verification", "are the references correct",
  "verify all refs", "export to zotero", "ris file", "zotero export"
---

# Reference Verification Skill

Verify every reference in an academic paper for factual accuracy using web search sub-agents. Also produces a Zotero-importable RIS file.

**Architecture**: Python extraction → JSON batches → Sonnet sub-agents (WebSearch) → compiled summary table

## How to Run — Follow These Steps Exactly

### Step 1: Get the file path

Ask the user for the .docx file path if not provided. Look in the current working directory for .docx files if needed.

### Step 2: Run the extraction script

```bash
py "C:/Users/user/.claude/skills/ref-verify/ref_verify.py" "<DOCX_PATH>"
```

This produces TWO files:
- `<paper>_REFS_TO_VERIFY.json` — batched references for sub-agents
- `<paper>_REFS.ris` — Zotero/Mendeley/EndNote import file

Options: `--batch-size N` (default 10), `--ris-only` (skip JSON)

### Step 3: Read the JSON and prepare batches

Read `_REFS_TO_VERIFY.json` using the Read tool. Extract:
- `batches[]` — each has `batch_num`, `ref_start`, `ref_end`, `references[]`
- Each reference has `num`, `label`, `text`

### Step 4: Spawn Sonnet sub-agents — one per batch

**YOU MUST DO THIS.** For each batch in the JSON, spawn a Sonnet sub-agent using the Task tool. This is the core of the skill.

```
Task tool parameters:
  description: "Verify refs {ref_start}-{ref_end} accuracy"
  subagent_type: general-purpose
  model: sonnet
  run_in_background: true
```

**Sub-agent prompt** — build this for each batch by inserting the actual references:

```
You are a reference verification agent. For each of the academic references
below, search the web to verify that the reference is ACCURATE — correct
authors, year, title, journal/publisher, volume, issue, pages, and DOI.
Report any errors you find.

For each reference, output:
- REF #: [number]
- STATUS: CORRECT / ERROR / UNVERIFIABLE
- If ERROR: what specifically is wrong and what the correct value should be
- If UNVERIFIABLE: why you couldn't verify it

Here are the references to verify:

REF{num}: {full reference text}
REF{num}: {full reference text}
...

Search the web for EACH reference individually. Be thorough — check every field.
```

**Concurrency rules:**
- Launch up to 3 sub-agents in parallel (max concurrent agents limit)
- As each sub-agent completes, launch the next queued batch
- Track progress: show the user which batches are running, done, and queued

### Step 5: Collect results as agents complete

As each sub-agent returns, extract from its result:
- **CORRECT** references — no action needed
- **ERROR** references — note the specific field and correct value
- **UNVERIFIABLE** references — flagged for manual check

Keep a running tally and update the user on progress.

### Step 6: Present final summary table

When ALL agents are done, present a complete summary:

**First, show only the issues:**

```markdown
## Issues Found

| # | Reference | Status | Issue |
|---|-----------|--------|-------|
| 3 | Beck (1979) | ERROR | Year should be 1976, publisher should be IUP |
| 13 | Ferenczi (1932) | ERROR | Year should be 1988 (publication date) |
| 54 | Rachman (1972) | UNVERIFIABLE | No book found with this title/publisher |
```

**Then the clean count:**
```
Clean references: 66 of 74 verified correct.
```

**Classify issues by severity:**
1. **Errors** — clear factual mistakes that should be fixed
2. **Debatable** — edition/publisher/year ambiguities the author should decide on
3. **Unverifiable** — couldn't confirm online, needs manual check

### Step 7: Mention the RIS file

Tell the user:
> The file `<paper>_REFS.ris` is ready to import into Zotero: **File → Import → select the .ris file**.

## RIS File Details

- Contains ALL references (not just verified ones)
- Each entry includes original APA text in the N1 (notes) field
- Supported by: Zotero, Mendeley, EndNote, Papers, RefWorks
- Type mapping: JOUR (journal), BOOK (book), CHAP (chapter), EDBOOK (edited book), GEN (unknown)
- After Zotero import, use "Retrieve Metadata for PDFs" to auto-correct any parsing issues

## Example Session

User: "תוודא את ההפניות במאמר שלי"

1. Identify the .docx file
2. Run `py ref_verify.py "paper.docx"` → extracts 74 refs, creates JSON + RIS
3. Read JSON → 8 batches of 10
4. Spawn batch 1 (refs 1-10), batch 2 (refs 11-20), batch 3 (refs 21-30) in parallel
5. Batch 1 completes → spawn batch 4 (refs 31-40)
6. Continue until all 8 batches done
7. Compile results: "8 issues found in 74 references"
8. Show issues table + clean count
9. "The RIS file is ready for Zotero import"
