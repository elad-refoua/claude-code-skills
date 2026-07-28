# Citation System Guide

Canonical source for citation rules and references.csv format. Read by the writer agent on demand.

---

## Rule: Never Hardcode Citations

**NEVER** type a citation string directly into glue() text. Always use citation functions.

- WRONG: `"Brown's (2019) framework"`
- RIGHT: `"{cite_s('brown2019')} framework"`

---

## references.csv -- Single Source of Truth

Every manuscript folder contains `references.csv` with raw bibliographic data.

| Column | Description |
|--------|-------------|
| `key` | Unique citation key (e.g., `brown2019`) |
| `type` | article, book, chapter, report, unpublished |
| `authors` | Full author list, APA format |
| `authors_short` | In-text short form |
| `year` | Publication year |
| `title` | Article/chapter title |
| `journal` | Journal name (articles) |
| `volume` | Volume number |
| `issue` | Issue number |
| `pages` | Page range |
| `publisher` | Publisher (books) |
| `editors` | Editor names (chapters) |
| `book_title` | Book title (chapters) |
| `doi` | DOI (without https://doi.org/ prefix) |
| `url` | URL (if no DOI) |
| `relevance` | WHY this reference matters -- narrative compass |

---

## The `relevance` Column

Your narrative compass. Read before writing any section. It tells you:
- What argument the reference supports
- Where in the paper it belongs
- How it connects to the story arc

When adding a new reference, ALWAYS write a relevance paragraph.

---

## Citation Functions

```r
ref_style <- "apa7"  # Set once. Options: "apa7", "ama", "vancouver", "chicago"

cite(key)           # Narrative:     Brown (2019)     | AMA: Brown^1^
cite_p(keys)        # Parenthetical: (Brown, 2019)    | AMA: ^1^
cite_s(key)         # Possessive:    Brown's (2019)   | AMA: Brown's^1^
```

Multiple: `cite_p(c('key1', 'key2'))` -> `(Author1, Year; Author2, Year)`

---

## Multi-Style Support

Change `ref_style` at the top of the R script. Everything adapts:

| Style | In-text | Reference List |
|-------|---------|----------------|
| `apa7` | (Author, Year) | Alphabetical |
| `ama` | Superscript ^1^ | Numbered by appearance |
| `vancouver` | Brackets [1] | Numbered by appearance |
| `chicago` | (Author Year) | Alphabetical |

---

## Adding New References

1. Add row to CSV with all bibliographic fields
2. Write a `relevance` paragraph
3. Use `cite()` in manuscript text
4. `validate_citations()` confirms no errors

---

## DOI Verification with CrossRef

**Always verify bibliographic data against CrossRef** before finalizing references.csv.

### CrossRef MCP Tools

| Tool | Use |
|------|-----|
| `mcp__crossref__verify_doi` | Check a DOI exists and get authoritative metadata |
| `mcp__crossref__search_paper` | Find a paper's DOI by title/author/year |
| `mcp__crossref__fetch_metadata` | Get a CSV row ready to append to references.csv |
| `mcp__crossref__validate_references` | Bulk-check all DOIs in references.csv |

### Workflow: Adding a New Reference

1. Find the DOI (from paper, Google Scholar, or `search_paper`)
2. Run `fetch_metadata` with the DOI + a relevance paragraph
3. Append the returned CSV row to references.csv
4. Use `cite()` in the manuscript glue() text

### Workflow: Validating Before Submission

1. Run `validate_references` on the manuscript's references.csv
2. Fix any DISCREPANCY entries (year, journal, pages mismatches)
3. Resolve any MISSING DOI entries (search CrossRef, add DOI to CSV)
4. Re-run validation to confirm all VERIFIED

### Priority: CrossRef over WebSearch

For **bibliographic metadata** (year, journal, volume, issue, pages), CrossRef is authoritative. Use it instead of WebSearch. WebSearch is still preferred for **topic discovery** (finding relevant papers on a subject).

---

## Active Reference Management

Be proactive:
1. **Ask** when a section needs literature support
2. **Search** using WebSearch/Tavily for relevant papers; **verify** with CrossRef
3. **Offer Chrome** for deep searches (Google Scholar, PubMed)
4. **Accept deep research reports** -- extract papers, add to CSV with relevance
5. **Cross-check** before submission: every claim cited, no orphans, DOIs valid via `validate_references`

---

## Model Matching

| Task | Model |
|------|-------|
| Reading papers, extracting data | Haiku (paper-reader agent) |
| Searching for references | Haiku |
| Writing manuscript prose | Opus |
| Formatting references.csv | Haiku |
