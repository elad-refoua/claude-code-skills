---
name: ref-context
description: |
  Verify that citations in an academic paper (.docx) contextually match the sentences where they appear.
  Extracts pairs via Python, then spawns a Sonnet sub-agent that web-searches each reference
  and verifies relevance. No API keys needed in the script.

  TRIGGERS: "check citation context", "verify citation accuracy", "do references match",
  "citation relevance", "are citations correct", "reference context check",
  "בדוק התאמת ציטוטים", "האם ההפניות מתאימות", "בדיקת הקשר הפניות"
---

# Citation Context Verifier

Verifies that each citation in an academic paper is contextually appropriate for the sentence where it appears. Uses web search + Sonnet for evidence-based verification.

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

Use the Read tool to read the generated `_PAIRS.json` file. Note the stats (pairs count, unique references).

### Step 4: Spawn a Sonnet verification sub-agent

Use the **Task tool** with these settings:
- `subagent_type`: `"general-purpose"`
- `model`: `"sonnet"`
- `description`: `"Verify citation context"`

**Sub-agent prompt template** (fill in the data from the JSON):

```
You are an expert academic citation verifier. You have a list of citation-sentence pairs from an academic paper. Your job:

1. For each UNIQUE REFERENCE, use WebSearch to find what the work is about
2. Then verify whether each citation is contextually appropriate for its sentence
3. Only flag CLEAR mismatches - most citations in a good paper are correct

PAPER: {paper name}

UNIQUE REFERENCES TO SEARCH (search each one):
{For each entry in unique_references, list: surname, year, search_query}

CITATION-SENTENCE PAIRS TO VERIFY:
{For each pair, list:}
--- Pair N ---
SENTENCE: {sentence}
CITATION: {citation}
REFERENCE: {reference_text}

WORKFLOW:
1. First, WebSearch each unique reference using its search_query. Record what you learn about each work.
2. Then go through each pair. Using the web info you found, assess:
   - Does the reference topic match what the sentence discusses?
   - Is it the correct work (right year, right author)?
   - Could a different work by the same author be more appropriate?
   - Is the claim consistent with what the cited work covers?
3. Only flag when you have POSITIVE EVIDENCE of a mismatch.

OUTPUT FORMAT - return this exact structure:
======================================================================
CITATION CONTEXT VERIFICATION REPORT
Paper: {paper name}
Method: Web search + Sonnet sub-agent
======================================================================

Total pairs checked: N
References searched online: N

----------------------------------------------------------------------
FLAGGED CITATIONS (if any)
----------------------------------------------------------------------

  [HIGH/MEDIUM/LOW] Author (Year)
    Issue: description of the mismatch
    Suggestion: what the correct citation might be
    Evidence: what web search revealed
    Context: "the sentence where it appears..."

----------------------------------------------------------------------
NOTES
----------------------------------------------------------------------
  Any general observations about citation patterns

======================================================================
```

### Step 5: Save the report

Save the sub-agent's output to `<filename>_CONTEXT_CHECK.txt` in the same folder as the paper.

### Step 6: Report to user

Show the user:
- Total citation-reference pairs checked
- How many references were searched online
- Any flagged mismatches with evidence and confidence
- Path to the saved report

## What It Catches
- **Wrong year**: Beck (1967) cited for cognitive therapy concepts, but Beck (1979) is the correct work
- **Wrong author**: Similar names confused (e.g., citing Fonagy when meaning Bowlby)
- **Irrelevant reference**: Reference topic doesn't match the sentence's claim
- **Anachronistic claims**: Citing a 2020 paper for a concept that existed since 1960

## Important Notes
- The Python script only does extraction - no API keys needed
- Verification is done by a Sonnet sub-agent with WebSearch (uses Claude Code's own API)
- Does NOT modify the original document
- Works best AFTER running ref-check (assumes citations and references exist)
- Web search makes verification evidence-based, not just LLM knowledge
- Install: `py -m pip install python-docx`
