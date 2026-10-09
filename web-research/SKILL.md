---
name: web-research
description: Token-efficient web research across multiple sources. Use when user wants to research a topic online, search academic databases, or gather information from multiple websites.
---

# Web Research - Multi-Source Information Gathering

Efficiently research topics across multiple web sources while minimizing token usage.

## Workflow

### Step 1: Understand the Query

Ask the user:
- What topic to research?
- Which sources? (default: Google Scholar + general web)
- How many results? (default: 5)
- Save to file? (default: yes, to `~/Desktop/research-TOPIC.md`)

### Step 2: Search

Use `WebSearch` or `mcp__brave-search__brave_web_search` first (no browser needed, very token-efficient).

Only use Chrome browser when:
- Need to access a specific database (PubMed, Scopus, etc.)
- Need institutional access
- WebSearch doesn't have what you need

### Step 3: Extract Content (Token-Efficient)

For each relevant result:

```
1. navigate → URL
2. get_page_text → extract article text
3. Save key findings immediately to output file
4. DO NOT keep full article text in context
```

**NEVER** screenshot articles. Text extraction is sufficient.

### Step 4: Compile Results

Write results to markdown file with:
- Title and source URL
- Key findings (2-3 sentences each)
- Date accessed

## Source-Specific Instructions

### Google Scholar
```
1. WebSearch "site:scholar.google.com TOPIC"
   OR navigate to scholar.google.com
2. find "search input" → type query
3. get_page_text → extract results list
4. For each paper: extract title, authors, year, abstract snippet
```

### PubMed
```
1. navigate to pubmed.ncbi.nlm.nih.gov
2. find "search input" → type query
3. computer left_click on search button
4. get_page_text → extract results
```

### General Web
```
1. Use WebSearch (preferred - no browser tokens)
2. For specific pages: navigate + get_page_text
```

## Token-Saving Rules

1. **ALWAYS** try `WebSearch` before opening Chrome
2. **NEVER** screenshot search results - use `get_page_text`
3. **NEVER** read full articles into context - save to file
4. **Use** `javascript_tool` for structured extraction:
   ```javascript
   // Extract all result titles and links
   Array.from(document.querySelectorAll('.result')).map(r => ({
     title: r.querySelector('h3')?.innerText,
     link: r.querySelector('a')?.href
   }))
   ```
5. **Batch operations**: Open tabs first, then extract sequentially
6. **Save immediately**: Write findings to file after each source

## Output Format

```markdown
# Research: [TOPIC]
Date: [DATE]

## Source 1: [Title]
- **URL:** [link]
- **Key findings:** [2-3 sentences]

## Source 2: [Title]
...

## Summary
[3-5 sentence synthesis of all findings]
```
