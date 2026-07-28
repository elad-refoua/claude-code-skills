---
name: lit-synthesis
description: |
  Convert multiple AI literature review PDFs into cohesive manuscript sections with APA citations and a papers database.

  TRIGGERS: "synthesize literature", "combine literature reviews", "create introduction from papers",
  "merge lit reviews", "papers to manuscript", "literature synthesis", "create papers database",
  "סינתזה של ספרות", "לשלב סקירות ספרות", "ליצור מבוא ממאמרים"
---

# Literature Synthesis

Convert multiple AI-generated literature reviews (Undermind, GPT, Gemini, etc.) into publication-ready manuscript sections.

## Workflow

### Step 1: Ingest Literature PDFs
Read all literature review PDFs in the target folder:
```
paper/
├── Undermind - [topic].pdf
├── [topic] GPT.pdf
├── [topic] Gemini.pdf
```

Extract from each:
- Full APA citations with DOIs
- Key findings
- Sample sizes and study designs
- Relevance to target manuscript

### Step 2: Create Papers Database (JSON)
```json
{
  "metadata": {
    "created": "YYYY-MM-DD",
    "purpose": "Literature database for [manuscript]"
  },
  "papers": [
    {
      "id": "author2024",
      "citation": "Author et al. (2024)",
      "full_reference": "Full APA 7th reference with DOI",
      "doi": "10.xxxx/xxxxx",
      "topic": "Main topic",
      "key_findings": "1-2 sentence summary",
      "relevance": "Why it matters for this manuscript",
      "sample": "N and population",
      "used_in_section": "Introduction/Discussion"
    }
  ]
}
```

### Step 3: Write Funnel-Structured Introduction
Structure paragraphs from broad to specific:
1. **General context** - Broad phenomenon (e.g., collective trauma)
2. **Core outcome** - Why this outcome matters (e.g., depression)
3. **Specific mechanism** - Key symptom/process (e.g., anhedonia)
4. **Historical evidence** - Prior research (e.g., 9/11 studies)
5. **Current context** - Recent/relevant events
6. **Gap identification** - What's missing in literature
7. **Present study** - Hypotheses and approach

### Step 4: Validate Citations
Cross-check:
- Every in-text citation has matching reference
- No orphan references (cited but not in text)
- Author names consistent
- Years match between citation and reference

Report discrepancies before finalizing.

## Quality Checklist

- [ ] All PDFs read and extracted
- [ ] Papers database created with full citations
- [ ] Introduction follows funnel structure
- [ ] Academic tone (no first-person until Present Study)
- [ ] All citations have DOIs where available
- [ ] Citation-reference validation passed
- [ ] References alphabetized (APA 7th)

## Integration with R Manuscript Generation

If using R `officer` package:
```r
references <- c(
  "Author, A. B. (Year). Title. Journal, Vol(Issue), pages. https://doi.org/xxx"
)

for (ref in references) {
  doc <- doc %>%
    body_add_par(ref, style = "Normal") %>%
    body_add_par("", style = "Normal")
}
```

## Output Files

| File | Purpose |
|------|---------|
| `papers_database.json` | Structured literature database |
| `generate_apa_manuscript.R` | R script with Introduction + References |
| `Manuscript_APA_Complete.docx` | Final Word document |

## Tips

- **Deduplication**: Same paper may appear in multiple AI reviews - keep one with best metadata
- **Missing DOIs**: Search CrossRef or Google Scholar
- **Citation style**: Use (Author, Year) not numbered references
- **Et al. rule**: 3+ authors = "et al." in text, full list in references
