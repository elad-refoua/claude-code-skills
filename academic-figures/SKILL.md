---
name: academic-figures
description: "Create publication-quality academic paper figures. Combines HTML/CSS layout precision with Gemini AI polish. Use for: create figure, paper figure, academic diagram, architecture diagram, make figure for paper."
---

# Academic Figures — Publication-Quality Figure Pipeline

Unified workflow for creating figures for academic papers. Combines exact layout control (HTML/CSS) with AI visual polish (Nano Banana 2) and scientific design principles.

## Triggers

Activate when the user says any of:
- "create figure", "paper figure", "make a figure"
- "academic diagram", "architecture diagram"
- "make figure for paper", "figure for the manuscript"
- "publication-quality figure", "journal figure"

---

## The Pipeline (6 Steps)

### Step 1: Understand the Concept

Before touching any tool, clarify with the user:
- **What does this figure communicate?** (the one core message)
- **What elements are needed?** (boxes, arrows, labels, icons, layers)
- **What is the target venue?** (column width, format requirements)
- **Any reference figures?** (style inspiration from other papers)

Write a brief concept description before proceeding. If anything is ambiguous, ask.

### Step 2: Build Layout in HTML/CSS

Create a standalone HTML file with:
- Exact text labels (every word matters — Gemini will change them if you rely on prompts alone)
- Correct spatial structure (boxes, arrows, flow direction)
- Approximate colors and typography
- Proper dimensions for the target venue (e.g., 800x500px for a single-column ACL figure)

```html
<!-- Example structure -->
<!DOCTYPE html>
<html>
<head>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Inter', sans-serif; margin: 0; padding: 20px; background: #fff; }
    /* ... layout styles ... */
  </style>
</head>
<body>
  <!-- Figure content with exact labels -->
</body>
</html>
```

Save the HTML to the project's working directory (e.g., `figure1_concept.html`).

### Step 3: Screenshot via Playwright

Use Playwright to render the HTML and capture a pixel-perfect screenshot:

```
1. browser_navigate → file:///path/to/figure1_concept.html
2. browser_take_screenshot → saves reference image
```

Verify the screenshot looks correct before proceeding. This screenshot becomes the reference for Gemini.

### Step 4: Polish with Nano Banana 2

Pass the screenshot as a reference asset with a SHORT prompt:

```bash
cd ~/.claude/skills/nano-banana-poster/scripts

npx tsx generate_poster.ts --aspect 16:9 \
  --assets "/path/to/screenshot.png" \
  "Polish this academic diagram into a beautiful, publication-ready figure. Keep the exact same layout, labels, and structure. BioRender style: flat design, soft rounded shapes, pastel colors, clean arrows, white background."
```

Key rules for the prompt:
- **SHORT prompts work better** — 1-2 sentences maximum
- **Always reference the asset** — "Polish this diagram" not "Create a diagram"
- **Specify style** — "BioRender style" or "clean academic style"
- **Emphasize preservation** — "Keep the exact same layout, labels, and structure"

### Step 5: Generate 3+ Attempts, Self-Review

**NEVER show the user the first attempt.** Always:

1. Generate at least 3 attempts (run the command 3 times)
2. Read/view each output image yourself
3. Check each attempt for:
   - Are all labels correct and readable?
   - Is the layout preserved from the reference?
   - Are arrows/connections accurate?
   - Is the text legible at target print size?
4. Pick the best attempt(s) to show the user
5. If none are good enough, adjust the HTML reference and try again

### Step 6: Iterate Based on Feedback

After the user reviews:
- For **layout changes**: go back to Step 2 (edit the HTML)
- For **style changes**: adjust the NB2 prompt in Step 4
- For **text changes**: always go back to HTML (Step 2) — never rely on Gemini to fix text
- For **fine-tuning**: minor CSS tweaks + re-screenshot + re-polish

---

## Design Principles

### Color

| Guideline | Details |
|-----------|---------|
| Soft palette | Pastels and muted tones; avoid pure saturated colors |
| Accessible | Colorblind-safe (test with Coblis simulator) |
| Redundant coding | Color + shape/pattern for key distinctions |
| Limited palette | Maximum 5-7 colors per figure |
| Grayscale test | Figure must be readable without color |

Recommended palette base (BioRender-inspired):
- Light blue: `#E3F2FD` / accent `#1976D2`
- Light green: `#E8F5E9` / accent `#388E3C`
- Light orange: `#FFF3E0` / accent `#F57C00`
- Light purple: `#F3E5F5` / accent `#7B1FA2`
- Light gray: `#F5F5F5` / accent `#616161`

### Typography

- **Font**: Inter (Google Fonts) — clean sans-serif with excellent readability
- **Hierarchy**: Title (18-20px bold) > Section labels (14-16px semibold) > Body text (11-13px regular) > Annotations (10-11px)
- **Minimum size**: 8pt for any text at final print size
- **Horizontal text only** — avoid rotated or vertical labels

### Layout

- **Generous whitespace** — breathing room between elements
- **Balanced composition** — visual weight distributed evenly
- **Clear flow direction** — left-to-right or top-to-bottom (unless RTL content)
- **Alignment** — elements on consistent grid lines
- **Direct labels** over legends when possible (reduces cognitive load)

### Accessibility

- Readable at single-column width (~7.7cm / ~3in for ACL/ACM venues)
- High contrast text (WCAG AA: 4.5:1 ratio minimum)
- No information conveyed by color alone
- All text embedded (not rasterized at low resolution)

---

## When to Use What

| Approach | Best For | Limitations |
|----------|----------|-------------|
| **HTML/CSS alone** | Simple diagrams where exact text control is critical; when NB2 keeps mangling labels | No artistic polish; looks like a web page |
| **Nano Banana 2 alone** | Illustrations, conceptual art, non-technical imagery, icons | Cannot control exact text placement or labels |
| **HTML then NB2 (RECOMMENDED)** | Technical diagrams that need to look polished — architecture figures, flow diagrams, system overviews | Requires multiple attempts; Gemini may still alter some labels |
| **HTML then PDF** | Camera-ready figures where exact text is non-negotiable; tables, structured layouts | No AI polish; relies entirely on CSS design skills |

### NEVER use:
- **matplotlib/seaborn** for architecture/conceptual figures (they are for data visualization, not diagrams)
- **Long text prompts to Gemini** for creating diagrams from scratch (it will ignore your specifications)
- **Gemini without a reference image** for anything with specific labels or structure

---

## BioRender Style Guide

BioRender is the gold standard for scientific figures. Emulate this style:

- **Flat design** — no gradients, shadows, or 3D effects
- **Soft rounded shapes** — rounded rectangles (border-radius: 12-16px), pill shapes
- **Pastel backgrounds** with strong accent borders/icons
- **Simple iconography** — minimal detail, instantly recognizable
- **Clean connecting arrows** — straight or single-curve, with clear arrowheads
- **White or very light background** — never dark backgrounds for print
- **Consistent stroke width** — 2-3px for borders and arrows
- **Generous padding** inside boxes (16-24px)

When prompting NB2, explicitly say "BioRender style" — the model recognizes this aesthetic.

---

## Critical Lessons Learned

These are hard-won lessons from creating figures for the CLPsych paper and other projects:

### Gemini Cannot Create Precise Diagrams from Text Alone
No matter how detailed your prompt, Gemini will invent its own labels, rearrange your layout, and ignore structural specifications. The ONLY reliable way to get exact content is to build it in HTML first and pass a screenshot as reference.

### Always Build the Layout First
The HTML/CSS step is not optional for technical figures. It is the single source of truth for labels, structure, and spatial relationships. Skip it and you will waste hours re-generating.

### Always Generate 3+ Attempts
Quality varies significantly between NB2 runs. One attempt may have perfect layout but mangled text; another may have crisp text but wrong colors. Generate at least 3, review all, pick the best.

### Always Self-Review Before Showing the User
Read each generated image carefully. Check every label, every arrow, every connection. Gemini frequently:
- Misspells or replaces labels (especially non-English text)
- Merges or splits boxes
- Reverses arrow directions
- Drops elements entirely

### Short Prompts Beat Long Ones
With NB2, a 1-2 sentence prompt with a good reference image vastly outperforms a 10-paragraph specification with no reference. The reference image does the heavy lifting.

### Reference Images Are Essential for Technical Content
Without `--assets`, Gemini produces generic clip-art that bears no resemblance to your intended figure. The screenshot reference is what makes the pipeline work.

### Iterate on HTML, Not on Prompts
When something is wrong with the output, the fix is almost always to improve the HTML reference, not to write a more detailed Gemini prompt. Better input image = better output.

### Multiple Versions Are Normal
The CLPsych Figure 1 went through 30+ iterations (concept previews, NB2 attempts, layout revisions). This is expected for publication figures. Do not promise "one-shot" results.

---

## Tools Reference

### Nano Banana 2 (Gemini Image Generation)
- **Model**: `gemini-3.1-flash-image-preview`
- **Script**: `~/.claude/skills/nano-banana-poster/scripts/generate_poster.ts`
- **Usage**: `npx tsx generate_poster.ts [--aspect RATIO] [--assets "path"] "prompt"`
- **Aspect ratios**: `3:2` (default), `16:9` (wide, good for figures), `1:1` (square)
- **Output**: `poster_0.jpg`, `poster_1.jpg`, etc. in current directory

### HTML to PDF
- **Script**: `~/.claude/skills/html-to-pdf/scripts/html-to-pdf.js`
- **Usage**: `node html-to-pdf.js input.html output.pdf [options]`
- **Options**: `--format=A4`, `--landscape`, `--margin=20mm`, `--scale=1.5`
- **Use when**: camera-ready output needed without AI polish

### Playwright Screenshot
- **Tool**: `browser_take_screenshot` (via Playwright MCP)
- **Workflow**: `browser_navigate` to `file:///path/to/figure.html`, then `browser_take_screenshot`
- **Use when**: capturing HTML layout as reference image for NB2

---

## Venue-Specific Dimensions

| Venue | Column Width | Full Width | Recommended HTML Size |
|-------|-------------|------------|----------------------|
| ACL/EMNLP/CLPsych | 7.7cm (~3in) | 16cm (~6.3in) | 800x500px (single) / 1600x500px (full) |
| APA journals | 8.5cm (~3.35in) | 17.5cm (~6.9in) | 850x530px / 1750x530px |
| Nature/Science | 8.9cm (~3.5in) | 18.3cm (~7.2in) | 890x560px / 1830x560px |
| General poster | varies | A0 (84x119cm) | 2400x3400px |

Always confirm target venue requirements before starting.

---

## Quick Reference Checklist

Before declaring a figure done:

- [ ] All labels are correct and spelled properly
- [ ] Layout matches the intended structure
- [ ] Arrows point in the correct direction
- [ ] Text is legible at target print size (zoom to actual size and check)
- [ ] Colors are accessible (colorblind-safe, grayscale-readable)
- [ ] White/light background suitable for print
- [ ] Resolution is sufficient (300 DPI minimum for print)
- [ ] Figure communicates its core message without the caption
- [ ] Style is consistent with other figures in the same paper
- [ ] File format matches venue requirements (PDF/PNG/EPS)
