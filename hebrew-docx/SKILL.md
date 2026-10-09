---
name: hebrew-docx
description: "Create Hebrew/RTL Word documents with proper bidirectional settings using python-docx. Use when generating Word documents with Hebrew text to ensure correct punctuation placement and text direction."
---

# Hebrew Word Documents (RTL) Skill

## Overview
This skill provides instructions for creating properly formatted Hebrew/RTL Word documents using python-docx.

## Critical RTL Requirements

Hebrew text in Word documents requires **THREE levels of RTL settings**:
1. **Document-level** - Set RTL for document sections
2. **Paragraph-level** - bidi + justification for each paragraph
3. **Run-level** - RTL for each text run
4. **Font settings** - Set font for complex scripts (cs)

Without ALL of these, text may appear left-aligned or with punctuation on the wrong side.

## Complete Required Code Pattern

```python
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def set_document_rtl(doc):
    """Set RTL at document level - CALL THIS FIRST."""
    for section in doc.sections:
        sectPr = section._sectPr
        bidi = OxmlElement('w:bidi')
        bidi.set(qn('w:val'), '1')
        sectPr.append(bidi)

def set_paragraph_rtl(paragraph):
    """Set paragraph to RTL direction for proper Hebrew display.

    This is REQUIRED for:
    - Punctuation to appear on the correct (left) side
    - Numbers to display correctly within Hebrew text
    - Proper text flow direction
    """
    pPr = paragraph._p.get_or_add_pPr()

    # Set bidi (bidirectional) to true - THIS IS THE KEY
    bidi = OxmlElement('w:bidi')
    bidi.set(qn('w:val'), '1')
    pPr.append(bidi)

    # CRITICAL: Also set explicit justification to right
    jc = OxmlElement('w:jc')
    jc.set(qn('w:val'), 'right')
    pPr.append(jc)

    # Also set alignment via python-docx API
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT

def set_run_rtl(run):
    """Set run-level RTL for mixed content."""
    rPr = run._r.get_or_add_rPr()
    rtl = OxmlElement('w:rtl')
    rtl.set(qn('w:val'), '1')
    rPr.append(rtl)

def set_hebrew_font(run, font_name='David', font_size=11):
    """Set font with proper complex script (Hebrew) support."""
    run.font.name = font_name
    run.font.size = Pt(font_size)
    # CRITICAL: Set font for ALL script types
    run._element.rPr.rFonts.set(qn('w:cs'), font_name)    # Complex scripts (Hebrew)
    run._element.rPr.rFonts.set(qn('w:ascii'), font_name)  # ASCII
    run._element.rPr.rFonts.set(qn('w:hAnsi'), font_name)  # High ANSI
```

## Complete Usage Example

```python
import sys
sys.stdout.reconfigure(encoding='utf-8')

from docx import Document

doc = Document()

# STEP 1: Set document-level RTL
set_document_rtl(doc)

# STEP 2: Set margins (optional)
for section in doc.sections:
    section.right_margin = Cm(2)
    section.left_margin = Cm(2)

# STEP 3: Create paragraph with Hebrew text
p = doc.add_paragraph()
run = p.add_run('שלום עולם! זה טקסט בעברית.')

# STEP 4: Apply ALL RTL settings
set_paragraph_rtl(p)  # Paragraph-level
set_run_rtl(run)      # Run-level
set_hebrew_font(run, 'David', 12)  # Font with cs support

doc.save('hebrew_document.docx')
```

## Helper Function for Easy Use

```python
def add_hebrew_paragraph(doc, text, font_size=11, bold=False, center=False):
    """Add a properly formatted RTL Hebrew paragraph."""
    p = doc.add_paragraph()
    run = p.add_run(text)

    # Font settings
    run.font.name = 'David'
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run._element.rPr.rFonts.set(qn('w:cs'), 'David')
    run._element.rPr.rFonts.set(qn('w:ascii'), 'David')
    run._element.rPr.rFonts.set(qn('w:hAnsi'), 'David')

    # RTL settings
    set_paragraph_rtl(p)
    set_run_rtl(run)

    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    return p

# Usage:
doc = Document()
set_document_rtl(doc)
add_hebrew_paragraph(doc, 'כותרת', font_size=18, bold=True, center=True)
add_hebrew_paragraph(doc, 'טקסט רגיל בעברית')
doc.save('output.docx')
```

## Common Mistakes to Avoid

1. **Missing document-level RTL** - Text appears left-aligned even with paragraph settings
2. **Using only alignment** - `paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT` alone does NOT fix RTL
3. **Forgetting w:jc element** - Explicit justification element needed in addition to bidi
4. **Not setting cs font** - Hebrew characters may render incorrectly without `w:cs` font setting
5. **Not setting each paragraph** - Every Hebrew paragraph needs ALL RTL settings
6. **Forgetting run-level RTL** - Mixed content (Hebrew + numbers/English) needs run-level settings

## Hebrew Font Recommendations

For best Hebrew display, use fonts with good Hebrew support:
- David (classic Hebrew font)
- Arial
- Calibri
- Times New Roman
- Narkisim
- Miriam

## Template-Based Documents

When using a template (like letterhead):
```python
doc = Document('letterhead_template.docx')
set_document_rtl(doc)  # Always set this first!

# Clear and rewrite paragraphs
for p in doc.paragraphs:
    p.clear()

# Add Hebrew content using helper function
add_hebrew_paragraph(doc, 'שורה ראשונה')
add_hebrew_paragraph(doc, 'שורה שנייה')

doc.save('output.docx')
```

## Encoding Notes

Always set UTF-8 encoding when printing/debugging:
```python
import sys
sys.stdout.reconfigure(encoding='utf-8')
```

## Quick Reference

| Issue | Solution |
|-------|----------|
| Text stuck to left | Add `set_document_rtl(doc)` first |
| Punctuation on wrong side | Add `w:bidi` AND `w:jc` elements |
| Text flows left-to-right | Set ALL three levels: document, paragraph, run |
| Mixed content issues | Use `set_run_rtl()` on each run |
| Font doesn't show Hebrew | Set `w:cs` font attribute |
| Numbers reversed | Ensure run-level RTL is set |

## Checklist for Hebrew Documents

- [ ] `set_document_rtl(doc)` called first
- [ ] `set_paragraph_rtl(p)` for every paragraph
- [ ] `set_run_rtl(run)` for every run
- [ ] Font set with `w:cs` attribute for complex scripts
- [ ] UTF-8 encoding for console output
