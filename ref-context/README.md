# ref-context

Verify that each citation in an academic paper (.docx) contextually matches the sentence where it appears. Goes beyond ref-check (which only checks existence) to verify *relevance*.

## What It Does

1. Extracts every citation-sentence pair from your paper
2. Web-searches each unique reference to find what it's actually about
3. Verifies whether each citation is appropriate for its sentence context
4. Flags mismatches with evidence and confidence levels

## What It Catches

- **Wrong year**: Beck (1967) cited for concepts from Beck (1979)
- **Wrong author**: Similar names confused (e.g., Fonagy vs Bowlby)
- **Irrelevant reference**: Reference topic doesn't match sentence claim
- **Missing references**: Papers cited that don't actually exist
- **Scope mismatch**: Military psychiatry book cited for general psychotherapy

## Requirements

```bash
pip install python-docx
```

No API keys needed - the verification is done by Claude Code's own Sonnet sub-agent with web search.

## Usage

In Claude Code, say:
- "check citation context"
- "verify citation accuracy"
- "are citations correct"
- "do references match their sentences"

## How It Works

1. Python script extracts citation-sentence pairs (no API calls)
2. Claude Code spawns a Sonnet sub-agent
3. Sub-agent web-searches each reference to learn what it's about
4. Sub-agent evaluates whether each citation fits its context
5. Report saved as `_CONTEXT_CHECK.txt`

Best used AFTER running ref-check to verify citations exist first.
