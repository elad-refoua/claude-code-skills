---
name: manuscript-submit
description: End-to-end journal manuscript submission — from adaptation to upload. Covers reference verification, APA formatting, journal selection, and Elsevier submission system automation.
triggers:
  - "submit paper"
  - "submit manuscript"
  - "upload to journal"
  - "journal submission"
  - "העלאת מאמר"
  - "הגשת מאמר"
  - "תגיש את המאמר"
  - "תעלה לג'ורנל"
---

# Manuscript Submission Skill

## Overview
Full pipeline: adapt paper → verify references → format → upload to journal submission system.

## Step 1: Journal Selection
- Check Q ranking (target Q1 journals when possible)
- Check cost: use your institution's OA agreements to find free publishing options
- Check word limits and article types
- Check turnaround time

## Step 2: Paper Adaptation
- Remove venue-specific language (e.g., CLPsych → general audience)
- Define technical terms for target audience (LLM, system prompt, RLHF, hallucination)
- Match reference format to journal style (ACL → APA, etc.)
- Handle self-citations per journal's blind review policy:
  - **Elsevier double-blind**: Cite own work in THIRD PERSON, author line "Anonymous"
  - **ACL conferences**: Use "Anonymous (year)" + "[Details omitted]"
- Add required elements: keywords, highlights, title page, cover letter, CRediT, funding, AI declaration

## Step 3: Reference Verification (CRITICAL)
**Every reference must be verified individually. This is non-negotiable.**

### Process:
1. One agent per reference (max 3 parallel)
2. Read actual PDF first page → extract exact author names, title, journal, volume, pages, DOI
3. Compare against paper's citation — flag ALL discrepancies
4. Verify claims: check that statistics, quotes, and findings cited in the paper match the source
5. Cross-check on Google Scholar for DOI errors and publication status changes
6. Build Excel audit trail

### Common AI Hallucination Errors (from March 2026 project):
- **Wrong author first names** (17 found in one paper!)
- **Fabricated quotes** attributed to papers that don't contain them
- **Wrong journals** (e.g., OSF Preprints when actually accepted in Psychological Science)
- **Wrong volume/issue/pages**
- **Mischaracterized effect sizes** (d=.23 is small, not medium-to-large)

## Step 4: APA 7th Formatting

Key rules:
- No "Introduction" heading — body starts with title repeated
- Author line only on title page, NOT in manuscript body
- Highlights: max 85 characters per bullet (Elsevier)
- References: 21+ authors → list first 19, then ..., then last
- En-dashes for page ranges (107–157)
- Spell out "and" in journal titles (not &)
- In parenthetical citations use & (not "and")

## Step 5: Submission System Upload

### Elsevier (submit.elsevier.com)
- URL pattern: `https://submit.elsevier.com/JOURNALCODE`
- Steps: Article type → Files → Metadata → Authors → Open Access → Classifications → Additional Info → Review
- Required files: Abstract, Manuscript (anonymized), Title Page (with authors)
- Optional files: Cover Letter, Highlights, Supplementary materials

### Playwright Automation for Elsevier
- Use Playwright MCP (not Chrome MCP) for file uploads
- Chrome MCP can't handle file picker dialogs
- Close Chrome before launching Playwright if needed
- Submission URL with UUID is saved — session persists

### Disabled React Form Bypass (Elsevier's author form)

```javascript
// Key technique: nativeInputValueSetter for React forms
const ns = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
ns.call(input, value);
input.dispatchEvent(new Event('input', { bubbles: true }));
input.dispatchEvent(new Event('change', { bubbles: true }));
```

- Remove `disabled` attributes before interacting
- Find inputs by label text (React uses dynamic IDs)
- Institution search: type and wait for API dropdown, then click menuitem
- Contributor roles: search by name, click option, chain with setTimeout
- Always confirm after filling

## Step 6: Pre-Submission Checklist
- [ ] Word count within limit
- [ ] Abstract within word limit
- [ ] All references have DOIs (if available)
- [ ] References alphabetically sorted
- [ ] No orphan references (every ref cited, every citation has ref)
- [ ] Declaration of Competing Interests in manuscript
- [ ] Generative AI declaration (if used)
- [ ] CRediT author contributions on title page
- [ ] Funding acknowledgment on title page
- [ ] Highlights under character limit
- [ ] Double-blind: no identifying info in manuscript body
- [ ] All claims verified against source papers

## Submission Preferences
- Q1 journals preferred
- Free publishing (subscription track or institution-covered OA)
- Minimal edits — surgical corrections, not rewrites
- One correction at a time, get approval before applying
- Agent per reference for verification
- Max 3 parallel agents
