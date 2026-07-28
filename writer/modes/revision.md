# Mode: Revision

Edit existing .docx manuscripts with track changes and bubble comments.

**Trigger keywords**: "edit this document", "revise the paper", "track changes", "check references", "verify citations", "review this manuscript"

---

## What This Mode Does

The writer agent doesn't just CREATE text; it REVISES existing documents and shows its work transparently via Word's track changes. This means the user can accept/reject each change individually.

---

## Capabilities

### General Editing
"Edit this paragraph", "improve the Discussion", "shorten the Introduction"

1. Read the .docx file
2. Identify the target section/paragraph
3. Apply writing quality rules (six-levels, anti-AI, voice)
4. Output a .docx with:
   - **Track changes**: insertions (green underline) and deletions (red strikethrough) visible in Word
   - **Bubble comments**: explanatory notes in margins explaining WHY each change was made

### Reference Sub-Workflows

When triggered by reference-related keywords, load the appropriate sub-workflow from `manuscript/`:

| Keyword | Sub-workflow | What it does |
|---------|-------------|--------------|
| "check references", "cross-reference citations" | `manuscript/ref-check.md` | Cross-reference citations vs. references → color-coded .docx + bubble comments |
| "verify citation context", "do references match" | `manuscript/ref-context.md` | Verify citations match sentence context → bubble comments on mismatches |
| "verify references", "check accuracy" | `manuscript/ref-verify.md` | Double-control reference accuracy → tracked changes + Excel + RIS |

---

## Track Changes Implementation

Use OOXML manipulation (python-docx + lxml) for tracked changes:

```python
import copy
from docx import Document
from lxml import etree

W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
W = '{' + W_NS + '}'
AUTHOR = "Claude QC"

def make_del(text, rpr=None):
    """Create a tracked deletion element."""
    d = etree.Element(f'{W}del')
    d.set(f'{W}id', next_id())
    d.set(f'{W}author', AUTHOR)
    d.set(f'{W}date', current_datetime())
    r = etree.SubElement(d, f'{W}r')
    if rpr is not None:
        r.append(copy.deepcopy(rpr))
    dt = etree.SubElement(r, f'{W}delText')
    dt.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    dt.text = text
    return d

def make_ins(text, rpr=None):
    """Create a tracked insertion element."""
    ins = etree.Element(f'{W}ins')
    ins.set(f'{W}id', next_id())
    ins.set(f'{W}author', AUTHOR)
    ins.set(f'{W}date', current_datetime())
    r = etree.SubElement(ins, f'{W}r')
    if rpr is not None:
        r.append(copy.deepcopy(rpr))
    t = etree.SubElement(r, f'{W}t')
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    t.text = text
    return ins
```

### Bubble Comments

For changes that need explanation or author decision:

```python
doc.add_comment(
    runs=target_runs,
    text="REVISION: [why this change was made]",
    author="Claude QC"
)
```

---

## Revision Workflow

1. **Read the document** completely
2. **Regression pass (R12)**: If comparing to a previous version (co-author edits, reviewer response, version upgrade), run the regression check FIRST — enumerate all losses, additions, and modifications. Present the delta report to the user before proceeding. See `lessons/paper-level.md` R12 for the full methodology and output format.
3. **Identify what needs changing** based on user request + regression findings
4. **Apply changes** as tracked changes (insertions + deletions)
5. **Add bubble comments** explaining non-obvious changes
6. **Save** as `<filename>_REVISED.docx` (never overwrite original)
7. **Report**: summary of changes made, grouped by type

---

## Rules

- **NEVER overwrite the original file.** Always save as a new file.
- Track changes must be visible in Word (Review → All Markup)
- For items needing AUTHOR DECISION (not auto-fixable), use bubble comments instead of tracked changes
- When uncertain whether a change is appropriate, add a comment asking for guidance
- Rev counter ranges: use 500+ to avoid ID collisions with ref scripts
- Apply all writing quality rules to revised text (six-levels, anti-AI, voice)
