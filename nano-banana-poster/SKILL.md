---
name: nano-banana-poster
description: "Generate images and posters with Google Gemini. Use for: create image, generate visual, AI image generation, marketing poster."
setup: "./SETUP.md"
---

# Nano Banana Poster Generator

Generate images using Google's Gemini model with optional reference assets.

## Quick Start

```bash
cd ~/.claude/skills/nano-banana-poster/scripts

# Basic generation (default 3:2 horizontal)
npx tsx generate_poster.ts "A futuristic city at sunset"

# With aspect ratio (3:2 horizontal, 2:3 vertical, 16:9 wide, 9:16 tall)
npx tsx generate_poster.ts --aspect 3:2 "A wide landscape poster"
npx tsx generate_poster.ts -a 9:16 "A vertical story format"

# With reference assets
npx tsx generate_poster.ts --assets "my-logo" "Create banner with logo"

# Combined: aspect ratio + assets
npx tsx generate_poster.ts --aspect 16:9 --assets "logo" "YouTube thumbnail"
```

**Note:** Use `npx tsx` instead of `npx ts-node` for better ESM module support.

## Aspect Ratio

**IMPORTANT:** Always use the default 3:2 aspect ratio unless the user explicitly requests a different format (like "vertical", "story", "square", etc.). Do NOT change the aspect ratio on your own.

Control image dimensions with `--aspect` or `-a`:

| Ratio | Use Case |
|-------|----------|
| `3:2` | Horizontal **(DEFAULT - use this unless user specifies otherwise)** |
| `1:1` | Square - Instagram, profile pics |
| `2:3` | Vertical - Pinterest, posters |
| `16:9` | Wide - YouTube thumbnails, headers |
| `9:16` | Tall - Stories, reels, TikTok |

```bash
npx tsx generate_poster.ts --aspect 3:2 "Your prompt"
npx tsx generate_poster.ts -a 16:9 "Your prompt"
```

## Adding Assets

Use `--assets` with full paths to include reference images:

```bash
# Single asset
npx tsx generate_poster.ts --assets "/full/path/to/image.jpg" "Your prompt"

# Multiple assets (comma-separated)
npx tsx generate_poster.ts --assets "/path/a.jpg,/path/b.png" "Use both images"
```

**Supported formats:** `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`

**IMPORTANT:** Assets are NOT automatically included. You must explicitly pass them via `--assets`.

## Save to Gallery

Save good results for future style reference:

```bash
npx tsx generate_poster.ts --save-to-gallery "my-style" "prompt"
```

Creates `assets/gallery/my-style.jpg` + `.meta.json` with prompt info.

## API Configuration

Create `scripts/.env`:
```
GEMINI_API_KEY=your_api_key_here
```

## Hebrew/RTL Content

When generating images with Hebrew text:

**ALWAYS include in prompt:**
```
CRITICAL: All text must be in Hebrew.
CRITICAL: Layout direction is RTL (right-to-left).
Flow, reading order, and visual hierarchy must go from RIGHT to LEFT.
```

This ensures text renders correctly and visual flow matches Hebrew reading direction.

## Technical Diagrams & Academic Figures

Gemini CANNOT create precise technical diagrams from text descriptions alone — it will ignore your labels and invent its own content. For diagrams with specific labels, structure, and layout:

### The Working Pipeline

1. **Build the layout in HTML/CSS first** — get exact structure, labels, colors right as code
2. **Screenshot the HTML** (via Playwright `browser_take_screenshot` or Puppeteer)
3. **Pass the screenshot as `--assets`** reference image
4. **Use a SHORT polish prompt**: `"Polish this academic diagram into a beautiful, publication-ready figure. Keep the exact same layout, labels, and structure."`
5. **Generate 3+ attempts** — quality varies between runs, pick the best
6. **Check each attempt yourself** before showing the user

### What Works
- Short prompts + reference image = Gemini follows the layout
- "Polish/enhance this diagram" works much better than "create this diagram"
- Multiple attempts (3+) to get the best variation
- HTML→screenshot→NB2 pipeline gives exact content control + AI visual polish

### What Does NOT Work
- Long detailed prompts describing diagrams from scratch — Gemini ignores them
- No reference image for technical content — Gemini invents random diagrams
- Passing HTML files as assets (they're not images — screenshot first!)
- Single attempts — always generate at least 3

### Example (Academic Paper Figure)
```bash
# Step 1: Build HTML with exact labels → screenshot via Playwright
# Step 2: Polish with NB2
npx tsx generate_poster.ts --aspect 16:9 \
  --assets "/path/to/screenshot.png" \
  "Polish this academic diagram into a beautiful, publication-ready figure. Keep the exact same layout, labels, and structure."
```

### BioRender Style (Best for Academic Figures)

The **BioRender aesthetic** produces the best results for scientific paper figures:
1. Build HTML with BioRender style: pastel colors (lavender #E8DEF8, mint #C8E6C9, peach #FFE0B2), flat icons, rounded shapes (16-20px radius), pill badges, generous spacing
2. Screenshot it via Playwright
3. Polish with NB2: `"Polish this scientific diagram into a beautiful BioRender-style figure. Keep all labels, layout, and structure exactly the same."`
4. Generate 3+ attempts, pick the best

This approach was validated and approved — always use it for paper figures. See also: `academic-figures` skill for the full pipeline.

## Model

Currently uses **Nano Banana 2** (`gemini-3.1-flash-image-preview`) — the latest and fastest Gemini image model. Updated from the older `gemini-3-pro-image-preview`.

## Output

- Files saved as `poster_0.jpg`, `poster_1.jpg`, etc.
- Aspect ratio: Configurable via `--aspect` (default: 3:2)
- Quality: 1K (1024px on longest edge)
