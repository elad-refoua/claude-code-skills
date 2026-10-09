---
name: jcr-lookup
description: "Documents the interface of a Clarivate JCR / Web of Science lookup script (jcr_lookup.py, not included) for journal Impact Factor, rank and quartile."
user_invocable: true
---

# JCR / Web of Science Lookup

Query journal metrics and article citations from Clarivate's official APIs.

## Triggers
- "impact factor", "IF of", "journal ranking", "JCR", "Web of Science"
- "what's the IF of", "rank of journal", "journal metrics", "WoS citations"
- "אימפקט פקטור", "דירוג כתב עת", "ציטוטים"
- "/jcr"

## Capabilities

### Journal Metrics (Journals API - active)
- Impact Factor (JIF) for any JCR year
- Exact ISI ranking (e.g., 25/288)
- Quartile (Q1-Q4)
- Category name
- 5-year IF, immediacy index, Eigenfactor

### Article Citations (Starter API - separate subscription)
- Times cited from Web of Science
- Per-article citation count by DOI
- Requires its own Clarivate Starter API subscription, approved separately from the Journals API

## Usage

The lookup script itself (`jcr_lookup.py`, which came from a CV-management skill) is not included in this repo. The commands below show the interface it exposes; point them at your own implementation.

### From command line:
```bash
# Single journal lookup
py <SET_YOUR_PATH>/jcr_lookup.py --journal "Nature Human Behaviour" --year 2024

# By ISSN
py <SET_YOUR_PATH>/jcr_lookup.py --issn 2397-3374 --year 2024

# Batch lookup of every journal in your own publication list
py <SET_YOUR_PATH>/jcr_lookup.py --all-published

# JSON output for programmatic use
py <SET_YOUR_PATH>/jcr_lookup.py --journal "JMIR Mental Health" --year 2024 --format json
```

### From Python (any agent/script):
```python
import sys
sys.path.insert(0, "<SET_YOUR_PATH>")  # folder that holds jcr_lookup.py
from jcr_lookup import lookup_journal, format_for_cv

metrics = lookup_journal("Nature Human Behaviour", year=2024)
# Returns: {'jif': '29.9', 'ranks': [{'category': '...', 'rank': 3, 'total': 78, ...}], ...}

cv_format = format_for_cv(metrics)
# Returns: "29.9;3/78"
```

## API Configuration
- **API Key**: your own Clarivate key (`<YOUR_API_KEY>`), read from an environment variable such as `CLARIVATE_API_KEY`; never commit it to a repo or shared folder
- **Journals API endpoint**: `https://api.clarivate.com/apis/wos-journals/v1`
- **Starter API endpoint**: `https://api.clarivate.com/apis/wos-starter/v1` (requires the separate Starter API subscription)
- **Auth header**: `X-ApiKey`
- **Rate limit**: 5 requests/second

## Known Journal ISSNs
The script maintains a lookup table of ISSNs inside `jcr_lookup.py`.
New journals are added automatically when queried by name.

## Important Notes
- **IF should match publication year** - use `--year` to specify the JCR year matching when the article was published
- JCR releases annually in June (e.g., JCR 2024 released June 2025)
- For papers published in the current year, use the most recent available JCR year
- Some university appointment and promotion files require the format `IF;Rank/Total;Citations`; `format_for_cv` produces the first two fields
