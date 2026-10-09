# data-storytelling

Explorable scroll data stories for a general reader: one mark per real thing, a guided scroll where each step changes one
encoding, the caveat at the moment it matters, the reader making the contested judgement, and the method open at every depth.

## What It Does

- Teaches Claude the character of a great data story (learned from "Extremists on Both Sides" by Eyal Raz, The Seventh Eye
  with Shenkar): every case shown as its own mark, the story told by change, quiet exact craft.
- Gives the build rules: short flowing cards (no pinned boxes, no dashboard panels), choreographed morphs that run backwards
  exactly as forwards, one packing rule per chart, words that turn a contrasting colour over the marks.
- Includes a canvas engine recipe that holds ~180,000 marks at 60 fps (one canvas, a Uint32 pixel buffer, Float32 positions,
  layouts in device pixels).
- Ships deterministic gates: drawn marks equal records, contrast measured from the canvas itself, no typed numbers (every
  printed number must come from the data), every view holds every record.
- Covers honesty and privacy for research data: aggregates only, no one participant followed down the levels, causal words
  checked, statistics matched to the source analysis in its own software.

## Requirements

None. The pages it produces are single HTML files; the optional screenshot gates use Python + Playwright.

## Usage

In Claude Code, say:
- "Make a data story from this dataset"
- "Build a scrollytelling page for these findings"
- "An explorable explanation of this paper's results"
- "סיפור נתונים", "להנגיש נתונים", "ויזואליזציה לקהל רחב"

For an explorer that researchers use to interrogate data, use a dashboard skill instead (dashboard-style / dashboard-expert);
for a figure in a paper, academic-figures.

## How It Works

`SKILL.md` holds the character, the design bar, the build rules and the lessons from four real builds, plus four questions
to answer in writing before building. `references/both-sides-teardown.md` is a full teardown of the reference site
(architecture, layouts, interaction, palette, honesty devices, accessibility, and what not to copy). Learn the technique;
the reference site's code and words remain its authors'.
