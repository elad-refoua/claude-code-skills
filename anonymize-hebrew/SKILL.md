---
name: anonymize-hebrew
description: |
  Hebrew-aware PII anonymization for text files, Word docs, and PDFs.
  Removes names, IDs, phones, emails, locations, and workplaces using
  word-boundary-aware regex that won't corrupt Hebrew words.

  TRIGGERS: "anonymize", "remove PII", "scrub PII", "scrub identifying information",
  "anonymize hebrew", "anonymize this document", "remove identifying information",
  "privacy scrub", "strip names from", "prepare for cloud"
---

# Hebrew PII Anonymization

## When to Use
- Before sending Hebrew text to any cloud AI service
- Scrubbing student/participant data from research documents
- Preparing documents for external review without identifying info
- Any time Hebrew text contains personal information that must be removed

## Workflow

### Step 1: Determine Input
Ask the user for:
1. **File path(s)** — single file or folder of files (.txt, .docx, .pdf)
2. **Known names** (optional) — a list or mapping.json with names to specifically target
3. **Output location** — default: `anonymized/` subfolder next to input

### Step 2: Read the File(s)
- `.txt` — read directly (UTF-8)
- `.docx` — use `python-docx` to extract text (see read-docx skill if available)
- `.pdf` — use `pdfplumber` to extract text

### Step 3: Generate and Run Anonymization Script

Generate a Python script using the patterns below. The script MUST:

1. Set UTF-8 output: `sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')`
2. Apply replacements in THIS ORDER (longest match first within each category):

```
Priority 1: 9-digit Israeli ID numbers → [ID]
Priority 2: Israeli phone numbers (landline + mobile) → [PHONE]
Priority 3: Email addresses → [EMAIL]
Priority 4: Known names from user-provided list → [NAME]
            - Only standalone matches (word-boundary aware)
            - Only names >= 4 chars to avoid Hebrew word corruption
            - Sort by length descending (longest first)
Priority 5: Context-based Hebrew first names → [PERSON]
            - Only after relational markers: של, עם, אצל, חבר/ה, אח/ות, בן/בת זוג, אמא, אבא, סבתא, הורים
            - Match against known Hebrew first names list
Priority 6: Israeli locations → [LOCATION]
            - Word-boundary aware, longest first
Priority 7: Workplace patterns → [WORKPLACE]
            - "חברת X", "ארגון X", "עמותת X", "מפעל X", "בית חולים X", "צה"ל", "משרד X"
            - "X בע"מ" / "X בע״מ"
            - NOT "חברה" (means "friend" in Hebrew — only "חברת" with construct state)
Priority 8: Clean up consecutive tags: [NAME] [NAME] → [NAME]
```

### Step 4: Hebrew Word Boundary Pattern

CRITICAL: Standard `\b` does NOT work for Hebrew. Use this pattern:

```python
# Hebrew-aware word boundary: preceded/followed by whitespace or punctuation
boundary_before = r'(?<![^\s,.:;\-\u2013(])'
boundary_after  = r'(?![^\s,.:;\-\u2013)])'

# Usage:
pattern = re.compile(boundary_before + re.escape(name) + boundary_after)
result = pattern.sub('[NAME]', result)
```

Why: Short Hebrew names like "אור" (Or, 2 chars) appear inside words like "תיאוריות" (theories). The boundary pattern prevents corrupting these words.

Rule: Only replace standalone names >= 4 chars. For names 2-3 chars, only replace after context markers (Priority 5).

### Step 5: QA Check

After anonymization, scan the output for leaks:
- Any remaining 9-digit numbers
- Any known names still present (>= 4 chars)
- Any email patterns
- Any Israeli mobile phone patterns (05X-XXX-XXXX)

Report: `[filename] N replacements, M QA issues`

### Step 6: Save Output

- Save anonymized text to output folder
- Print summary: files processed, total replacements, QA issues
- If user requested mapping: save `mapping.json` with `{filename: {original_names: [...], original_ids: [...]}}`

## Reference Data

### Hebrew First Names (120+)
```python
HEBREW_FIRST_NAMES = {
    # Female
    'נועה', 'תמר', 'מיכל', 'שירה', 'הילה', 'ליאת', 'עדי', 'דנה', 'מאיה',
    'אורלי', 'רותם', 'שרון', 'הדס', 'אפרת', 'ענת', 'גלית', 'לימור', 'אורית',
    'רונית', 'יעל', 'רחל', 'שרה', 'לאה', 'מרים', 'חנה', 'רבקה', 'אסתר',
    'אביגיל', 'עינב', 'נעמה', 'ליאור', 'אלה', 'נגה', 'עדן', 'רוני', 'שלומית',
    'אורה', 'גילה', 'טלי', 'יפית', 'קרן', 'ניצן', 'שגית', 'סיגל', 'אילנה',
    'מורן', 'ליהי', 'לינוי', 'אוריה', 'ליבי', 'חגית', 'דליה', 'נאוה', 'בתיה',
    'אמילי', 'סופי', 'ליא', 'אריאלה', 'מעיין', 'ליאל', 'אילה', 'עלמה',
    'איילת', 'סתיו', 'לוטם', 'הדר', 'שחף', 'ים', 'אביה', 'מוריה', 'יונית',
    'רננאל', 'תכלת', 'זיו', 'אור', 'לי', 'אורין', 'שירז', 'לילך',
    # Male
    'דוד', 'משה', 'יוסף', 'אברהם', 'יצחק', 'יעקב', 'שמואל', 'אליהו',
    'דניאל', 'יונתן', 'אורי', 'עמית', 'גיל', 'רון', 'אלון', 'ניר', 'עידו',
    'יותם', 'נדב', 'עופר', 'אייל', 'בועז', 'אסף', 'גלעד', 'עומר', 'איתי',
    'מתן', 'נועם', 'יובל', 'אלעד', 'בנימין', 'הלל', 'נתנאל', 'עודד',
    'דביר', 'יאיר', 'טל', 'כפיר', 'סער', 'תומר', 'גבע', 'אביעד', 'דקל',
    'ידידיה', 'יואב', 'אריאל', 'בן', 'עמנואל', 'שי', 'רועי', 'אדם',
}
```

### Hebrew Last Names (40+)
```python
HEBREW_LAST_NAMES = {
    'כהן', 'לוי', 'מזרחי', 'פרץ', 'ביטון', 'דהן', 'אברהם', 'פרידמן',
    'שפירא', 'גולדברג', 'גולדשטיין', 'רוזנברג', 'רוזנצווייג', 'ברקוביץ',
    'וייס', 'שוורץ', 'קליין', 'גרוס', 'פישר', 'מילר', 'שמיט', 'בכר',
    'אזולאי', 'חדד', 'עמר', 'מלכה', 'אוחיון', 'גבאי', 'סויסה', 'בן דוד',
    'בן משה', 'בן שמואל', 'בן אור', 'דדון', 'אלקובי',
}
```

### Israeli Locations (40+)
```python
ISRAELI_LOCATIONS = {
    'תל אביב', 'ירושלים', 'חיפה', 'באר שבע', 'רמת גן', 'פתח תקווה',
    'ראשון לציון', 'נתניה', 'אשדוד', 'חולון', 'בני ברק', 'רחובות',
    'הרצליה', 'כפר סבא', 'רעננה', 'מודיעין', 'אשקלון', 'בת ים',
    'הוד השרון', 'גבעתיים', 'קריית אתא', 'נצרת', 'עכו', 'טבריה',
    'צפת', 'אילת', 'דימונה', 'ערד', 'קריית שמונה', 'נהריה',
    'עפולה', 'יבנה', 'לוד', 'רמלה', 'קריית גת', 'שדרות',
    'גבעת שמואל', 'כפר יונה', 'זכרון יעקב', 'פרדס חנה',
}
```

### Context Markers for Short Names
```python
# Only replace Hebrew names 2-3 chars after these relational markers
CONTEXT_MARKERS = r'(?:של|עם|אצל|חבר[תי]*|אח[ותיה]*|ב[ני]?[ת]?\s?זוג[תי]*|אמ[אי]|אב[אי]|סבת[אי]?|הורי[יה]?)'
```

### Workplace Patterns
```python
WORKPLACE_PATTERNS = [
    r'(?:חברת|ארגון|עמותת|מפעל|מרפאת|בית חולים|בי"ח|צה"ל|משרד)\s+[\u0590-\u05FF]{2,15}',
    r'[\u0590-\u05FF]{2,15}\s+(?:בע"מ|בע״מ)',
]
```

## Known Pitfalls

1. **"חברה" vs "חברת"**: "חברה" means both "company" and "friend" in Hebrew. Only use "חברת" (construct state) for workplace detection.
2. **Short names inside words**: "אור" (Or) appears in "תיאוריות" (theories), "אור" (light). Never replace names < 4 chars without context.
3. **Course/institution numbers**: 9-digit course codes (e.g., 866021201) look like ID numbers. If the user provides known non-ID numbers, exclude them.
4. **Reversed RTL in PDFs**: Some PDFs store Hebrew text reversed. The regex still works on reversed text, but QA check may need manual review.
5. **Windows console**: Always set `sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')` or Hebrew output will crash.

## Example Usage

User: "Anonymize the files in submissions/ before I send them to Claude for grading"

Response:
1. Ask: "Do you have a list of known names (e.g., mapping.json)? Or should I detect names from the text only?"
2. Generate anonymization script targeting `submissions/` → `anonymized/`
3. Run script
4. Report: "47 files processed, 312 replacements, 0 QA issues. Output in anonymized/"
