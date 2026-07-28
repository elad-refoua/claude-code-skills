---
name: jcr-lookup
description: "Look up journal Impact Factor, ranking, and article citations from Web of Science / JCR. Uses Clarivate APIs. Available from any project."
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

### Article Citations (Starter API - pending approval)
- Times cited from Web of Science
- Per-article citation count by DOI
- Status: waiting for Clarivate approval of Starter API subscription

## Usage

### From command line:
```bash
# Single journal lookup
py ~/.claude/skills/update-cv/scripts/jcr_lookup.py --journal "Nature Human Behaviour" --year 2024

# By ISSN
py ~/.claude/skills/update-cv/scripts/jcr_lookup.py --issn 2397-3374 --year 2024

# All of Elad's published journals
py ~/.claude/skills/update-cv/scripts/jcr_lookup.py --all-published

# JSON output for programmatic use
py ~/.claude/skills/update-cv/scripts/jcr_lookup.py --journal "JMIR Mental Health" --year 2024 --format json
```

### From Python (any agent/script):
```python
import sys, os
sys.path.insert(0, os.path.expanduser('~/.claude/skills/update-cv/scripts'))
from jcr_lookup import lookup_journal, format_for_cv

metrics = lookup_journal("Nature Human Behaviour", year=2024)
# Returns: {'jif': '29.9', 'ranks': [{'category': '...', 'rank': 3, 'total': 78, ...}], ...}

cv_format = format_for_cv(metrics)
# Returns: "29.9;3/78"
```

## API Configuration
- **API Key**: `~/.claude/config/clarivate_credentials.txt`
- **Journals API endpoint**: `https://api.clarivate.com/apis/wos-journals/v1`
- **Starter API endpoint**: `https://api.clarivate.com/apis/wos-starter/v1` (pending)
- **Auth header**: `X-ApiKey`
- **Rate limit**: 5 requests/second

## Known Journal ISSNs
The script maintains a lookup table of ISSNs in `~/.claude/skills/update-cv/scripts/jcr_lookup.py`.
New journals are added automatically when queried by name.

## Important Notes
- **IF should match publication year** - use `--year` to specify the JCR year matching when the article was published
- JCR releases annually in June (e.g., JCR 2024 released June 2025)
- For papers published in the current year, use the most recent available JCR year
- The BIU appointment file format requires: `IF;Rank/Total;Citations`
