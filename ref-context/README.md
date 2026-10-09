# ref-context

Verify that each citation in an academic paper (.docx) contextually matches the sentence where it appears. Goes beyond ref-check (which only checks existence) to verify *relevance*.

## What It Does

Three-stage verification pipeline:

1. **Dedicated web search** for every unique reference (via a Tavily MCP server if installed, otherwise the built-in WebSearch)
2. **Sonnet evaluation** using real web data (not model knowledge)
3. **Opus confirmation** independently verifies flagged items

Only reports flags that both Sonnet and Opus agree on.

## What It Catches

- **Wrong year**: Smith (2005) cited for concepts first introduced in Smith (2012)
- **Wrong author**: Similar names confused (e.g., Fonagy vs Bowlby)
- **Irrelevant reference**: Reference topic doesn't match sentence claim
- **Non-existent references**: Papers that don't actually exist
- **Scope mismatch**: a book about one specialised population cited for a general claim

## Requirements

```bash
pip install python-docx
```

No API keys needed in the script. Claude Code handles web search and model calls. Step 4 optionally uses a Tavily MCP server (own API key); without it, WebSearch is used.

## Usage

In Claude Code, say:
- "check citation context"
- "verify citation accuracy"
- "are citations correct"

## How It Works

1. Python script extracts citation-sentence pairs → `_PAIRS.json`
2. Claude Code web-searches each unique reference individually (auditable)
3. Sonnet sub-agent evaluates all pairs using the web data
4. Opus sub-agent independently confirms each flagged issue
5. Final report includes only confirmed flags + dismissed false alarms

Best used AFTER running ref-check to verify citations exist first.
