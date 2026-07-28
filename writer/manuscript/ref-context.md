# Citation Context Verifier

Verifies that each citation is contextually appropriate for the sentence where it appears.

**Trigger keywords**: "check citation context", "verify citation accuracy", "do references match", "בדוק התאמת ציטוטים"

---

## Architecture

```
Python extraction → Dedicated web search per reference → Sonnet evaluation → Opus confirmation
```

## Pipeline (8 Steps)

### Step 1: Get file path

### Step 2: Run extraction script
```bash
py "<SET_YOUR_PATH>/skills/ref-context/ref_context.py" "<INPUT_FILE_PATH>"
```
Outputs: `_PAIRS.json` with citation-sentence pairs and search queries.

### Step 3: Read JSON output
Note stats and `unique_references` section.

### Step 4: Search each reference with Tavily
For EACH entry in `unique_references`, use `mcp__tavily__tavily_search`. Search ALL references (parallel, batch 3-5).

### Step 5: Spawn Sonnet evaluation sub-agent
Evaluates all pairs using ONLY web data (not its own knowledge).
Task tool: `subagent_type: "general-purpose"`, `model: "sonnet"`

### Step 6: Opus confirmation of flagged items
Independently verifies each Sonnet flag via its own web search.
Task tool: `subagent_type: "general-purpose"`, `model: "opus"`

### Step 7: Build final report
Save to `_CONTEXT_CHECK.txt`: Confirmed Flags, Dismissed Flags, Verified Citations, Insufficient Data.

### Step 8: Report to user
Show confirmed flags with evidence, dismissed flags, insufficient data references.

## What It Catches
- Wrong year (Beck 1967 vs 1979)
- Wrong author (similar names confused)
- Irrelevant reference (topic mismatch)
- Non-existent reference
- Scope mismatch

## Optional Step 9: Embed flags as Word comments
Add confirmed flags as bubble comments directly on the manuscript.

## Notes
- Python extraction: no API keys needed
- Every reference gets a dedicated Tavily web search
- Only consensus flags reported (Sonnet + Opus agree)
- Cost: ~$0.50-1.00 per paper
- Best run AFTER ref-check
