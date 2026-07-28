---
name: read-docx
description: "Extract text from Word documents (.docx files) with full support for tables, headers, and Hebrew. Use when asked to read or analyze .docx file content on Windows."
---

# Read DOCX Files Skill

Extract text from `.docx` files with proper handling for tables, Hebrew text, and document structure.

## Method 1: Python (Preferred - Better Tables & Structure)

Use `python-docx` for clean extraction with table support:

```python
from docx import Document
from pathlib import Path

def read_docx(file_path):
    """Extract text from DOCX with tables rendered as markdown."""
    doc = Document(file_path)
    output = []

    for element in doc.element.body:
        if element.tag.endswith('p'):  # Paragraph
            para = next((p for p in doc.paragraphs if p._element == element), None)
            if para and para.text.strip():
                output.append(para.text)
        elif element.tag.endswith('tbl'):  # Table
            table = next((t for t in doc.tables if t._element == element), None)
            if table:
                output.append(render_table_markdown(table))

    return '\n\n'.join(output)

def render_table_markdown(table):
    """Convert Word table to markdown."""
    rows = []
    for i, row in enumerate(table.rows):
        cells = [cell.text.strip().replace('\n', ' ') for cell in row.cells]
        rows.append('| ' + ' | '.join(cells) + ' |')
        if i == 0:  # Header separator
            rows.append('|' + '|'.join(['---'] * len(cells)) + '|')
    return '\n'.join(rows)

# Usage
text = read_docx("document.docx")
print(text)
```

### One-liner for simple extraction:

```bash
py -c "from docx import Document; d=Document('FILE.docx'); print('\n'.join(p.text for p in d.paragraphs if p.text.strip()))"
```

### Install if needed:

```bash
py -m pip install python-docx --quiet
```

## Method 2: PowerShell (Fallback - No Dependencies)

For when python-docx isn't available:

```powershell
Add-Type -AssemblyName System.IO.Compression.FileSystem
$docxPath = "PATH_TO_DOCX_FILE"
$zip = [System.IO.Compression.ZipFile]::OpenRead($docxPath)
$entry = $zip.Entries | Where-Object { $_.FullName -eq "word/document.xml" }
$stream = $entry.Open()
$reader = New-Object System.IO.StreamReader($stream)
$content = $reader.ReadToEnd()
$reader.Close()
$zip.Dispose()

# Better regex for paragraphs and tables
$text = $content -replace '</w:p>', "`n"
$text = $text -replace '</w:tr>', "`n"
$text = $text -replace '</w:tc>', " | "
$text = [regex]::Replace($text, '<[^>]+>', '')
$text = $text -replace '[ \t]+', ' '
$text = $text -replace '\n\s*\n+', "`n`n"
Write-Output $text.Trim()
```

## Handling Hebrew Paths

If the file path contains Hebrew characters:

```bash
# Copy to temp location first
powershell -Command "Copy-Item 'נתיב/עברי/קובץ.docx' -Destination 'temp_doc.docx'"
# Then read from temp
py -c "from docx import Document; print('\n'.join(p.text for p in Document('temp_doc.docx').paragraphs))"
# Cleanup
del temp_doc.docx
```

## Quick Reference

| Need | Command |
|------|---------|
| Full text + tables | Use Python method above |
| Just paragraphs | `py -c "from docx import Document; print('\n'.join(p.text for p in Document('FILE.docx').paragraphs))"` |
| Just tables | `py -c "from docx import Document; [print(t.cell(r,c).text) for t in Document('FILE.docx').tables for r in range(len(t.rows)) for c in range(len(t.columns))]"` |
| Count pages (approx) | `py -c "from docx import Document; print(len(Document('FILE.docx').paragraphs) // 30, 'pages')"` |

## Output Options

1. **Plain text** - Default, good for analysis
2. **Markdown** - Use table renderer for better formatting
3. **Save to file** - Redirect output: `> extracted.txt`

## Reading Documents with Tracked Changes

When a document has tracked changes (w:ins, w:del), standard `para.text` only returns original runs.
To get the **visible text** (original + insertions, excluding deletions):

```python
from docx import Document

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

def get_visible_text(para):
    """Get visible text: original runs + tracked insertions, skip deletions."""
    text = ''
    for child in para._element:
        if child.tag == f'{W}r':
            t = child.find(f'{W}t')
            if t is not None and t.text:
                text += t.text
        elif child.tag == f'{W}ins':
            for r in child.findall(f'{W}r'):
                t = r.find(f'{W}t')
                if t is not None and t.text:
                    text += t.text
        # Skip w:del elements entirely
    return text

doc = Document("manuscript.docx")
for i, para in enumerate(doc.paragraphs):
    text = get_visible_text(para)
    if text.strip():
        print(f"P{i}: {text}")
```

### Auditing tracked changes:
```python
# Count all tracked changes by author
for child in para._element:
    if child.tag == f'{W}ins':
        author = child.get(f'{W}author', '')
        # This is an insertion by `author`
    elif child.tag == f'{W}del':
        author = child.get(f'{W}author', '')
        # This is a deletion by `author`
```

## Limitations

- Images are not extracted (only text)
- Complex nested tables may not render perfectly
- Track changes/comments require the `get_visible_text()` helper above
- For PDFs or scanned documents, use different tools

## Alternatives for Complex Documents

If the document has complex formatting or images:
- Ask user to export as PDF → use `/html-to-pdf` skill
- Use `docling` library for advanced parsing: `pip install docling`
- Use MS Word automation (requires Word installed)
