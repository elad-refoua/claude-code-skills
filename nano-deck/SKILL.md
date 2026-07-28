---
name: nano-deck
description: |
  Generate complete presentations using Gemini 3.1 Flash (Nano Banana 2) image generation.
  Takes an existing PPTX or slide descriptions, generates AI-designed slides, and assembles into PPTX.
  Includes style consultation, mandatory user review of slide descriptions, and post-generation fix cycle.

  TRIGGERS: "create presentation with nano banana", "nano deck", "generate presentation",
  "rebuild presentation", "AI presentation", "nano banana presentation",
  "צור מצגת", "בנה מצגת עם ננו בננה", "מצגת AI"
---

# Nano Deck - AI Presentation Generator

Generate complete presentations using Gemini 3.1 Flash image generation (Nano Banana 2).
Each slide is an AI-generated image assembled into a PPTX file.

## Pipeline Overview

```
1. READ source → 2. STYLE CONSULTATION → 3. DESCRIBE slides → 4. USER REVIEW → 5. GENERATE → 6. ASSEMBLE → 7. REVIEW & FIX
```

## Phase 1: Read Source Presentation

If working from an existing PPTX, use the `/read-pptx` skill to export all slides as PNG
and view them. Take detailed notes on EACH slide:
- Exact Hebrew text (copy precisely - don't paraphrase)
- Layout structure (what goes where)
- Visual elements (icons, images, diagrams)
- Color scheme and style
- **Directional elements**: pyramids (which end is top/bottom), timelines (direction), hierarchies

### CRITICAL - Common Pitfalls to Avoid
- **Pyramids/hierarchies**: ALWAYS note which item is at the TOP (smallest) and BOTTOM (widest).
  NEVER reverse the order. If a model has levels 1-5, confirm which is the foundation vs apex.
- **RTL text**: Hebrew text flows right-to-left. Numbered lists start from the right.
- **Section transitions**: Note the EXACT style (hand-drawn, minimal, etc.)
- **Tool/product names**: Copy EXACTLY - don't substitute or generalize
- **Citations**: Copy author names, years, and journal names precisely
- **Statistics**: Copy exact numbers - don't round or approximate

## Phase 2: Style Consultation (MANDATORY)

**Before writing any prompts, discuss the visual direction with the user.**

Present style options using AskUserQuestion. Cover these areas:

### 2a. Overall Visual Style
Ask the user to choose or describe their preferred look:
- **Dark tech** - Dark backgrounds, glowing accents, futuristic feel
- **Light & clean** - White/light backgrounds, minimal, professional
- **Colorful gradient** - Rich gradients, vibrant colors, modern
- **Hand-drawn / sketch** - Organic, warm, approachable
- **Glassmorphism** - Frosted glass cards, depth effects, translucent layers
- **Custom** - User describes their own vision

### 2b. Color Palette
- Suggest 2-3 palette options based on the chosen style
- Ask if there are brand colors or specific colors to use/avoid
- Note: keep enough contrast for Hebrew text readability

### 2c. Slide Element Preferences
- **Icons**: Flat, 3D, emoji-style, outlined, or none?
- **Backgrounds**: Solid, gradient, textured, or illustrated?
- **Text style**: Large & bold, elegant, handwritten feel?
- **Cards/containers**: Rounded, sharp, floating, bordered?

### 2d. Special Requests
- Any reference images or existing slides they especially like?
- Elements to definitely include or avoid?
- Tone: formal, casual, playful, academic?

### 2e. Build Style Prefix
Based on the user's answers, compose the STYLE prefix string that will be prepended
to every slide prompt. This ensures visual consistency across the entire deck.

Save the chosen style to `nano_deck/style_guide.md` for reference during generation.

**Prompt template:**
```
Before I start writing slide prompts, let's nail down the visual style.

I have a few questions about the look and feel you want:
1. Overall style (dark tech, light & clean, colorful, glassmorphism, etc.)?
2. Any specific colors or brand palette?
3. Preferences for icons, backgrounds, text style?
4. Any slides from the original you especially like the look of?

This will keep all slides visually consistent.
```

## Phase 3: Create Slide Descriptions

Write a structured description for EACH slide in a review document.
Format each slide as:

```
### Slide N: [short_name]
**Type:** title / content / data / transition / tool-cards / diagram
**Original text (key elements):**
- [exact Hebrew text from the slide]

**Layout description:**
[How elements are arranged]

**Visual elements:**
[Icons, images, diagrams, colors]

**Confidence:** HIGH / MEDIUM / LOW
**Notes:** [Any uncertainties or questions for the user]
```

Mark slides as LOW confidence when:
- You can't read text clearly from the exported PNG
- Complex diagrams with specific spatial relationships
- Content you're reconstructing from memory rather than reading directly
- Charts/data with specific numbers

## Phase 4: User Review (MANDATORY)

**NEVER skip this step.** Present the slide descriptions to the user BEFORE generating.

1. Save descriptions to `nano_deck/slide_descriptions.md`
2. Ask the user to review, focusing on:
   - Content accuracy (especially names, numbers, model structures)
   - Correct ordering of hierarchies/pyramids
   - Any LOW confidence slides that need clarification
   - Missing content or wrong emphasis
3. Help resolve any uncertainties through discussion
4. Get explicit approval before proceeding to generation

**Prompt template:**
```
I've written descriptions for all [N] slides in nano_deck/slide_descriptions.md.

PLEASE REVIEW before I generate. Key things to check:
- Are hierarchies/pyramids in the correct order (top vs bottom)?
- Are tool names, citations, and statistics accurate?
- Are there any [LOW confidence] slides you can clarify?

I'll wait for your approval before generating.
```

## Phase 5: Generate Slides

### Setup
```python
# Install dependencies
py -m pip install google-genai --quiet
```

### API Configuration
- **Model:** `gemini-3.1-flash-image-preview`
- **API Key:** Read from `~/.claude/skills/nano-banana-poster/scripts/.env`
- **Response modalities:** `["IMAGE", "TEXT"]`
- **Rate limiting:** 6 seconds between calls
- **Retries:** 3 attempts per slide

### Style Prefix
Prepend a consistent style block to every prompt. Example:
```
Create a single presentation slide. 16:9 widescreen format (landscape).
Style: [describe consistent visual language across all slides]
CRITICAL: All text MUST be in Hebrew, written RIGHT-TO-LEFT.
CRITICAL: This is a SINGLE slide, clean and uncluttered.
CRITICAL: Numbers, English brand names stay in English/LTR.
```

### Generation Script Structure
```python
"""Generate presentation slides with Nano Banana 2."""
import os, time, json
from pathlib import Path
from google import genai

API_KEY = "..."  # from .env
MODEL = "gemini-3.1-flash-image-preview"
OUTPUT_DIR = Path("nano_deck/slides")
STYLE = """..."""  # consistent style prefix

SLIDES = [
    {"num": 1, "name": "title", "prompt": "..."},
    # ... all slides
]

def generate_slide(client, prompt, output_path, retries=3):
    for attempt in range(1, retries + 1):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=STYLE + prompt,
                config={"response_modalities": ["IMAGE", "TEXT"]},
            )
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    data = part.inline_data.data
                    if isinstance(data, str):
                        import base64
                        data = base64.b64decode(data)
                    with open(output_path, 'wb') as f:
                        f.write(data)
                    return True
        except Exception as e:
            print(f"  Attempt {attempt} failed: {e}")
            time.sleep(15 * attempt)
    return False

# Main loop - skips existing slides, logs results
```

### Key Features
- **Skip existing:** Don't regenerate slides that already exist (unless `--force`)
- **Resume safe:** Can restart after interruption
- **Progress logging:** Save results to `generation_log.json`
- **Range support:** `--start N --end N` to generate subsets

## Phase 6: Assemble PPTX

```python
from pptx import Presentation
from pptx.util import Inches, Emu

prs = Presentation()
prs.slide_width = Inches(13.333)  # 16:9
prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]

for img in sorted(Path("slides").glob("slide_*.jpg")):
    slide = prs.slides.add_slide(blank)
    slide.shapes.add_picture(str(img), Emu(0), Emu(0),
                             prs.slide_width, prs.slide_height)

prs.save("output.pptx")
```

## Phase 7: Review & Fix

After assembly, offer the user a review cycle:

1. **Quick visual check:** Open the PPTX, screenshot key slides
2. **Side-by-side comparison:** Compare generated vs original for critical slides
3. **Fix individual slides:** Regenerate specific slides with corrected prompts
   - Delete the old slide image
   - Run generation for just that slide number
   - Reassemble PPTX

**Prompt template:**
```
The presentation is ready with [N] slides.
Want me to open it and compare key slides with the original?
Or tell me which slide numbers need corrections and what to fix.
```

## Cost Estimate

Per slide: ~$0.04-0.08 (Gemini 3.1 Flash image generation)
Typical 60-slide deck: ~$5-10 including retries
Free tier may cover ~15-20 slides/day

## Lessons Learned

### Hebrew Text
- Nano Banana 2 renders Hebrew perfectly - long sentences, mixed Hebrew+English, all work
- Always add "CRITICAL: All text MUST be in Hebrew, RTL direction" to prompts
- Specify exact text in quotes in the prompt - don't describe vaguely

### Common Errors
- **Reversed hierarchies**: ALWAYS verify pyramid/hierarchy direction with the user
- **Made-up content**: Never invent statistics, citations, or tool names
- **Wrong model labels**: Copy acronym expansions exactly from source
- **Missing slides**: Some slides may fail silently - always verify count matches

### What Works Best
- Describe layout precisely (positions, sizes, colors)
- Specify exact text in quotes
- Include style references ("glassmorphism", "hand-drawn", "data visualization")
- One slide = one focused prompt, not combined
