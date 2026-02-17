---
name: ref-context
description: |
  Verify that citations in an academic paper (.docx) contextually match the sentences where they appear.
  Three-stage pipeline: Python extraction → dedicated web search per reference → Sonnet evaluation → Opus confirmation.
  Every reference gets its own web search. Only consensus flags are reported.

  TRIGGERS: "check citation context", "verify citation accuracy", "do references match",
  "citation relevance", "are citations correct", "reference context check",
  "בדוק התאמת ציטוטים", "האם ההפניות מתאימות", "בדיקת הקשר הפניות"
---

# Citation Context Verifier

Verifies that each citation in an academic paper is contextually appropriate for the sentence where it appears. Three-stage pipeline ensures every reference is independently searched and evaluated.

## Architecture

```
Python extraction → Dedicated web search per reference → Sonnet evaluation → Opus confirmation
```

1. **Python**: Extract citation-sentence pairs (no API)
2. **Web search**: Claude Code searches EACH unique reference with Tavily (dedicated, auditable)
3. **Sonnet**: Evaluates all pairs using real web data (not its own knowledge)
4. **Opus**: Reviews only the flagged items for final confirmation

## How to Run

### Step 1: Get the file path
Ask the user for the .docx file path if not provided.

### Step 2: Run the extraction script

```bash
py "C:/Users/user/.claude/skills/ref-context/ref_context.py" "<INPUT_FILE_PATH>"
```

This outputs `<filename>_PAIRS.json` with all citation-sentence pairs and search queries.
Only requires `python-docx`. No API keys needed.

### Step 3: Read the JSON output

Use the Read tool to read the generated `_PAIRS.json` file. Note the stats and the `unique_references` section.

### Step 4: Search each reference with Tavily

For EACH entry in `unique_references`, use `mcp__tavily__tavily_search` to search:

```
mcp__tavily__tavily_search({
  query: "<search_query from JSON>",
  max_results: 3
})
```

**IMPORTANT**: Search ALL unique references, not just some. Use parallel tool calls where possible (batch 3-5 searches per message to stay efficient).

For each reference, record:
- The reference text (from JSON)
- The search query used
- Top 2-3 search result snippets (title + content, max 200 chars each)

Save all search results into a structured block like:

```
=== REFERENCE: Author (Year) ===
Search: "<query>"
Result 1: <title> — <snippet>
Result 2: <title> — <snippet>
```

### Step 5: Spawn Sonnet evaluation sub-agent

Use the **Task tool** with these settings:
- `subagent_type`: `"general-purpose"`
- `model`: `"sonnet"`
- `description`: `"Evaluate citation context"`

**Sub-agent prompt template** (fill in the data):

```
You are an expert academic citation verifier. You have citation-sentence pairs from an academic paper, AND pre-searched web data about each reference. Your job is to evaluate whether each citation is contextually appropriate.

IMPORTANT: Use ONLY the provided web search data to evaluate references. Do NOT rely on your own knowledge about what papers contain. If the web data is insufficient for a reference, mark it as "insufficient data" rather than guessing.

PAPER: {paper name}

==============================
WEB SEARCH RESULTS PER REFERENCE
==============================
{For each unique reference, paste the search results block from Step 4}

==============================
CITATION-SENTENCE PAIRS TO VERIFY
==============================
{For each pair, list:}
--- Pair N ---
SENTENCE: {sentence}
CITATION: {citation}
REFERENCE: {reference_text}

EVALUATION RULES:
1. Compare each sentence's claim against the web data for its cited reference
2. Only flag when web data provides POSITIVE EVIDENCE of a mismatch
3. "Insufficient data" is NOT a flag — skip those
4. Most citations in a good paper are correct. Be conservative.
5. Consider that a work can be legitimately cited for concepts it discusses, even if it's not the primary source

OUTPUT FORMAT:
======================================================================
CITATION CONTEXT EVALUATION
Paper: {paper name}
References with web data: N
Pairs evaluated: N
======================================================================

FLAGGED CITATIONS:
----------------------------------------------------------------------
  [HIGH/MEDIUM/LOW] Author (Year)
    Issue: description of the mismatch
    Web evidence: what the search results show about this work
    Sentence: "the sentence where it appears..."
    Suggestion: what might be more appropriate
----------------------------------------------------------------------

CLEAN CITATIONS:
  (list each verified citation briefly, e.g., "Bordin (1979) - working alliance - APPROPRIATE")

INSUFFICIENT DATA:
  (list references where web results were not informative enough to evaluate)
======================================================================
```

### Step 6: Opus confirmation of flagged items

If Sonnet flagged any items, spawn an **Opus sub-agent** to independently verify EACH flag:

Use the **Task tool** with:
- `subagent_type`: `"general-purpose"`
- `model`: `"opus"`
- `description`: `"Confirm citation flags"`

**Opus prompt template**:

```
You are a senior academic citation reviewer. A junior reviewer flagged some citations as potentially problematic. Your job: independently verify each flag using web search. You may CONFIRM or DISMISS each flag.

For each flagged citation below:
1. Use WebSearch to independently search for the reference
2. Read what the work is actually about
3. Read the sentence where it's cited
4. Decide: is the flag valid (CONFIRM) or a false alarm (DISMISS)?

FLAGGED ITEMS:
{For each Sonnet flag, list:}
--- Flag N ---
CITATION: Author (Year)
SENTENCE: "the sentence..."
REFERENCE: full reference text
JUNIOR REVIEWER'S CONCERN: {the issue Sonnet described}

OUTPUT:
For each flag, respond:
  [CONFIRM/DISMISS] Author (Year)
    Your finding: what you found about this work
    Verdict: why you confirm or dismiss the flag
    Confidence: HIGH/MEDIUM/LOW
```

### Step 7: Build final report

Combine results into the final report. Only include flags that Opus CONFIRMED (or all Sonnet flags if Opus was not run).

Save to `<filename>_CONTEXT_CHECK.txt` with this structure:

```
======================================================================
CITATION CONTEXT VERIFICATION REPORT
Paper: {paper name}
Method: Dedicated web search + Sonnet evaluation + Opus confirmation
======================================================================

Total pairs checked: N
Unique references searched: N
References with sufficient web data: N

----------------------------------------------------------------------
CONFIRMED FLAGS (Sonnet flagged + Opus confirmed)
----------------------------------------------------------------------
  [HIGH/MEDIUM/LOW] Author (Year)
    Issue: ...
    Evidence: ...
    Sentence: "..."
    Suggestion: ...

----------------------------------------------------------------------
DISMISSED FLAGS (Sonnet flagged but Opus dismissed)
----------------------------------------------------------------------
  Author (Year) - Opus: "reason for dismissal"

----------------------------------------------------------------------
VERIFIED CITATIONS
----------------------------------------------------------------------
  (Brief list of confirmed-appropriate citations)

----------------------------------------------------------------------
INSUFFICIENT DATA
----------------------------------------------------------------------
  (References that couldn't be verified due to limited web results)

======================================================================
```

### Step 8: Report to user

Show the user:
- Total pairs checked and references searched
- CONFIRMED flags with evidence (these are the real issues)
- DISMISSED flags (Sonnet was wrong, Opus caught it)
- Insufficient data references (manual check recommended)
- Path to the saved report

## What It Catches
- **Wrong year**: Beck (1967) cited for cognitive therapy concepts, but Beck (1979) is the correct work
- **Wrong author**: Similar names confused (e.g., citing Fonagy when meaning Bowlby)
- **Irrelevant reference**: Reference topic doesn't match the sentence's claim
- **Non-existent reference**: Paper that doesn't actually exist
- **Scope mismatch**: Military psychiatry book cited for general psychotherapy diversification

## Important Notes
- The Python script only does extraction - no API keys needed
- Every reference gets a dedicated Tavily web search (auditable)
- Sonnet evaluates using ONLY web data, not its own knowledge
- Opus independently confirms flags (reduces false positives)
- Does NOT modify the original document
- Works best AFTER running ref-check (assumes citations and references exist)
- Install: `py -m pip install python-docx`
- Cost estimate: ~$0.50-1.00 per paper (Tavily searches + Sonnet + Opus for flags only)
