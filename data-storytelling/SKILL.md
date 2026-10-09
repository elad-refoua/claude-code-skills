---
name: data-storytelling
description: "Explorable data stories for a GENERAL reader: one mark per real thing, a guided scroll story where each step changes one encoding, the caveat placed at the moment it matters, the reader making the contested judgement and watching the data recount, and the method open from a glance down to the full prompts. Learned from 'Extremists on Both Sides' (Eyal Raz, The Seventh Eye + Shenkar, 2026), an example of data visualization at its best. Use for: a data story, scrollytelling, an explorable explanation, making research findings or a dataset accessible to the public, a story page for a paper, a data scene for a film, 'להנגיש נתונים', 'סיפור נתונים', 'ויזואליזציה לקהל רחב'. Boundary: an explorer for researchers who come to interrogate the data -> a dashboard skill (for example dashboard-style / dashboard-expert in this repo); a figure for a paper -> academic-figures."
---

# Data storytelling — the spirit of "both sides"

Learned from https://both-sides.the7eye.org.il, chosen as an example of data visualization at its best: not to copy that
page, but to learn its character - how it makes knowledge and data accessible - from its pages, its source code and its
published methodology.

The full teardown (architecture, layouts, interaction, palette, honesty devices, accessibility, the rules and what not
to copy) is in `references/both-sides-teardown.md`. Read it before building anything substantial. This file is the
character and the rules, plus what four real builds taught.

## The character, in seven sentences

1. **The reader is an adult who can handle the real thing.** Show every case, not an average of them. 12,283 events
   are 12,283 squares; the count is something you SEE, and any square opens to its own story.
2. **The story is told by change.** The same marks move from a timeline, to a packed block, to sized-by-magnitude, to
   the reader's own classification. Each step changes ONE encoding and has ONE card that says what changed.
3. **The caveat arrives at the moment it is needed, not in a footnote.** "One action may be one person, another
   hundreds of thousands" is the card that triggers the size view.
4. **The contested judgement belongs to the reader.** The page does not decide what "extreme" means; the reader drags
   action types into a box and the data recounts by THEIR definition.
5. **The method is open at every depth:** a source line on the card, a standing note in the legend, a method summary
   at the end, a full methodology page with the model prompts as they are in the code, and an address for errors that
   says what to send.
6. **Quiet, exact craft.** Paper-white ground, one body font, no gridlines, no chrome; colour only for categories,
   position for the groups being compared; motion that runs backwards exactly as it ran forwards.
7. **Nothing on the page is typed by hand.** Every count, date and summary is computed from the data at load, so a
   data refresh cannot leave a stale number behind.

## The design bar (measured on the site) - and what a first attempt got wrong

A first build (54 large squares, one per item of a CV) was judged "cool, but not impressive or tasteful enough compared
with that site". Correct data and clean gates are the floor; this is the bar. Measured on the live site:

| | the site | the first attempt (do not repeat) |
|---|---|---|
| Marks | thousands, ~3.5 px with 1.5 px gaps: a TEXTURE you read as a whole, then hover one | 54 squares of ~46 px: an infographic of blocks |
| Narrative type | each card is one or two sentences set in the DISPLAY face (Discordia 18.5/27.75), no headings | a heading, three paragraphs and bold numbers per card: a report |
| Body type | Assistant weight 300 (light), 18/26.6, ink #111 on paper #FDFCFF | Heebo 400 16.5 |
| Pace | ~17 steps, one idea each | 8 steps, several ideas each |
| Cards | white, 456 px, padding 21/29, radius 8, a 1.25 px SVG dash whose period divides the perimeter | a dashed CSS border and a drop shadow |
| Legend | a few small typed labels beside tiny swatches at the screen's edges, no box | a boxed panel of eleven rows |
| Motion | every change is a choreographed morph (fly, then grow in waves), labels type in, marks never fade | CSS transitions of whole blocks |
| Hero | a 40 px title in a narrow column beside two thin columns of small coloured squares | a card |

Rules that follow:
- **Choose data with SCALE.** The look depends on hundreds to thousands of honest units; with fewer than ~300, it becomes an
  infographic. If the data has no unit that large, pick other data (or the story is a chart, not this).
- **Write the story as many short cards**, one sentence of meaning each, in a display face at a modest size. No card headings.
  Numbers inside sentences, not bold callouts.
- **Canvas for the marks**, DOM only for the few interactive things; one draw loop; morph by interpolating from each mark's last
  painted position; waves (fly, then grow, biggest first).
- **Typography is the brand:** one display face for the voice, one light body face, no bold except the title.
- **Legends whisper:** small labels at the edges, typed in when they first matter, never a boxed panel over the data.
- **Look at the screenshots side by side with the reference before showing anyone**; if it reads as a dashboard or an
  infographic, it is not done.

What the second build taught (~180,000 survey answers drawn as dots; a blind reviewer called v1 "still an infographic"):
- **With 100k+ marks, the dots cannot be seen at full view: show one up close first.** A camera close-up step (the same layout
  scaled about a point, dots 5-7x) with one dot labelled by what it is; then pull back. After that the texture is believed.
- **One flat colour per category.** A light-to-dark ramp inside a block turns the block into a gradient-filled bar; position
  already carries the value.
- **Dot size vs pitch:** a 1 px dot in a 2 px pitch reads as a pastel wash. Use pitch >= 3 with a 1 px gap, or solid at pitch 2;
  win the space by tightening gaps and labels, not by shrinking dots.
- **Never let a value start mid-column** (staircases) and never give every value its own column (white seams): one column start
  per group, a gutter between groups, values running on inside a group.
- **The reader's choice needs a visible payoff in one place:** the moved marks gather into ONE pile, the changed numbers sit next
  to their names, count up from the old value with the old value ghosted, and the card says the change in a sentence.
- **Cards go under the picture, centred; a fixed side panel reads as a dashboard.** Do NOT pin them (position: sticky): pinned
  cards felt "stuck, not flowing" - the page scrolls a screen with nothing moving, then the card vanishes. Let them scroll with
  the page, one every half screen, opacity tied to each card's own position as it nears the picture.
- **No box around the words** (the feedback: "livelier, less boxy, let the words flow"): free-standing centred text in the
  display face at ~23 px, words arriving one by one with the scroll, the key phrase in its category colour. Gate it: a 120 px
  scroll moves the card 120 px; every word visible at the reading position.
- **The closer look of a reviewer pays:** one blind reviewer given only the screenshots, the reference screenshots and this
  section found all three main defects; one round, then fix.
- **Engine that holds 180k marks at 60 fps:** one canvas, a Uint32 pixel buffer, every dot written per frame, positions as
  Float32Arrays, layouts computed in device pixels; counts-only data, so marks are generated from cells (group x item x bin).
- **Screenshots scaled down show moire on fine dot grids**; judge texture at 100%.

What the third build taught (~20,000 diary moments moving across four maps; the blind reviewer again said "stacked-bar
infographic and dashboard" in the middle, and was right):
- **Words over the dots turn a contrasting colour** (the feedback: "when the text rises over the dots, make it a contrasting
  colour, maybe white"): each word reads the share of drawn pixels under it from the frame's own buffer (two thresholds, so the
  rim does not flicker) and gets white with a soft dark glow of stacked text shadows, no box. Compare the buffer UNSIGNED
  (`>>>0`): a signed packed colour never equals the buffer and every pixel reads as a dot. Gate it from the canvas
  (`getImageData`), not from the page's decision.
- **One packing rule per chart.** Nearest-free-slot around jittered targets drew three encodings at once (sparse scatter,
  saturated squares, corner discs). A round pile per cell, target = the cell's centre, reads as one rule: area = count.
- **A packed cloud's size is the packing, not the data.** To show between-person spread, give each person ONE mark at the
  binned mean (moments fly into it) instead of packing all moments around person cells.
- **A pile of "no answer" marks at person-mark size reads as people.** Gather such a group into one mark with its count.
- **Highlight inside the same layout**: a second colour key per mark (+6) whose palette is either the same colour or DIM;
  the key never changes, so lighting a subset and returning are both smooth.
- **Stacked bands**: each colour band starts a new row and its partial row is centred, or the bands make staircases.
- **On a phone, draw at the device's own resolution (DPR up to 3)** when the marks are few enough; capped at 2, dots at
  pitch 2 merge into solid bars.
- **No typed numbers, by construction**: every number the page prints passes through one function that records it; the gate
  extracts every number from the rendered text and fails on any that the page did not record.
- **Every view holds every record**: missing answers go to a labelled pile, so the dot count is equal in every view (gate).

What the fourth build taught (a level-by-level tour of a multilevel dataset: all -> groups -> waves -> people -> each person
around their own mean, 21 variables; three reviewers at once - design, honesty, language - each found what the others did not):
- **In RTL, `border-inline-start` is the RIGHT edge.** A mean line drawn as a label's start border sat a text-width away
  from its value. Use `border-left` at the value, and gate the LINE (the side that carries the border), not the box's left.
- **A level of people should show people:** one block per person (area = their moments) at the bin of their mean, packed in
  shelves, from a count table of person sizes per bin (no id). A histogram of moments at person means hides them.
- **A tour needs a ladder:** a quiet line of the levels with the current one dark; and a caveat step should change the
  picture too (dim what the card is not about).
- **Never follow one participant down the levels** on a research page: that is one person's series, a raw row.
- **Statistics shown on the page get parity with the source analysis, in the source's own software.** A three-level
  model in Python (statsmodels, vc_formula) silently missed 3 of 18 rows that lme4 reproduces exactly; the two-level fits
  matched, which is why it looked fine. Fit in R/lme4 when the source analysis fits in lme4, and gate against its saved table.
- **Causal words are the honesty reviewer's first catch**: "the change is the treatment" with no comparison group; say what
  else could move it (time, who stayed) and show the control group moving too.

## Before building: four questions (answer them in writing, in the project's DESIGN.md)

1. **What is ONE mark?** (an event, a participant, a session, a paper, a message). If no honest unit exists, this is
   not a unit visualization; use an ordinary chart.
2. **What is the one comparison the story is for?** Name the two (or few) groups; they get POSITION. Subgroups get
   colour.
3. **What is contested, and can the reader set it?** A cutoff, a definition, a category. If yes, that is the ending.
4. **What would mislead if shown without a word, and where exactly does that word go?** List each caveat with the step
   it belongs to.

## Rules (the craft)

Each rule names the site feature that shows it; details and code references are in the teardown.

1. **Teach the encoding with real records.** "Each square is one action", shown with 8 real events that then fly into
   their places in the full chart.
2. **A mark never loses its identity.** Key every layout by record id; every transition starts from where the mark was
   last painted (also mid-flight); marks never fade in or out, they move, shrink or grow. A vanishing mark reads as
   lost data.
3. **One encoding change per step, one card per change.** Time -> packed -> sized -> uniform -> reader-classified.
4. **Caveat in the card immediately before the view it qualifies.**
5. **Count with uniform units; magnitude is an opt-in toggle.** Area must never silently compete with count.
6. **Magnitude in a few ordinal tiers that match how the source states it** (dozens / hundreds / thousands), with a
   key, and with UNKNOWN drawn differently from SMALL (see "What not to copy" #1).
7. **Position separates the groups being compared; colour marks subgroups.** A mirrored layout around a central axis
   makes row width equal count. Colours are looked up by data key, never by hex.
8. **Let the reader define the contested category and recount live.** Hold the old count while marks move, then count
   up to the new one; announce it to screen readers.
9. **Scrub only where position IS the content** (a timeline filling with dates). Elsewhere, fixed-length beats
   triggered when a card crosses a line, which reverse cleanly. Never block scrolling, except at most once, at the one
   decision the argument needs, and say why.
10. **Backwards must equal forwards.** Symmetric easing (sine in-out), mirrored clocks, each beat re-eased from raw
    progress (never ease an eased slice), and a hand-over mid-flight continues the same clock.
11. **Three accessible layers for a canvas chart:** a text summary computed from the same data; keyboard stepping that
    matches the layout (up/down = time, left/right = group, Home/End, Esc); live announcements that carry the numbers.
12. **Reduced motion in one place:** the trigger engine lands on end states at once; keep only motion that is itself
    the data.
13. **Contrast floor in code** for colour-filled labels; hand-override a colour whose darkened version changes
    category (yellow turns brown).
14. **Touch is its own design:** docked tooltip, long-press magnifier, tap instead of drag, instructions written per
    device ("hover" vs "press and hold").
15. **Thousands of marks -> canvas with discipline:** one path per colour, cached layout reads, paint once per frame,
    snap to device pixels, skip what is off screen. Few elements that need focus or CSS -> DOM.
16. **Layer the method from glance to full depth** (character sentence 5).
17. **Generate every derived number from the data at load** (character sentence 7).
18. **Anchor a timeline with a few events the reader already knows,** without implying they caused anything.
19. **Keep reader-set state visible after it stops being editable** (filtered groups stay marked in the legend).
20. **Tune by eye with live knobs, then write the chosen value down with its date and reason** beside the constant.

## The method layer, when a model helped make the data

The site classified 12k+ events with a language model and published how. This is the standard for any data your pages
show that a model coded, translated or extracted (it is also what a reviewer of an LLM-coded study asks):

- **Publish the prompts as they are in the code**, named by file, with the run order.
- **Every model decision carries a short reason, a confidence and a needs-review flag**, stored beside the record.
- **Every extracted number carries the quote it came from** (a chain of custody from source to number).
- **A manual correction is stamped with its date, and re-runs skip it**, so a later run never overwrites a human fix.
- **Deterministic conversions happen in code, not in the model** ("dozens" -> 50, "thousands" -> 3,000), and are
  listed on the method page.
- **Missing stays missing.** A value not reported is marked missing, never estimated from the category.
- **A loaded term gets an operational definition with every condition explicit**, and the record is classified by
  what its description actually establishes.
- **The limitations name the selection rules that pull in opposite directions on the same group** - and if a
  limitation changes the headline comparison, it gets a card IN the story, not only on the method page.
- **Dates on every number** ("as of 5 October 2026, 12,283 events").

## What not to copy (from the teardown)

1. **Unknown drawn as small.** 72% of the site's events have no crowd figure and are drawn at the smallest tier, the
   same as "under 100"; the missing share differs by camp (about 86% vs 53% by the teardown's count), so the size view
   partly encodes reporting gaps, unannounced. **Always draw unknown distinctly (outline or hatch) or exclude it and
   print how many were excluded.**
2. **No size key, and the tooltip never prints the magnitude.** Give a key; say "order of magnitude".
3. **Decorative marks that look like data** (the closing field is padded with non-events). Once marks stop being
   data, they must look different.
4. **Disabled pinch-zoom** with 1-3 px marks (WCAG 1.4.4).
5. **A forced interaction** that holds the ending hostage: at most once, only where the argument needs the reader.
6. **The engineering shape** (a 510K file, hundreds of global constants, special-case hand-offs). Build instead:
   scenes as `layout(records) -> targets`, one tween engine keyed by id, one trigger primitive, one draw loop.
7. Typewriter effects everywhere; a 5 MB data file with every description loaded up front (load text on demand).

## Research and personal data: what changes

- **Data from human participants.** A page that leaves your machine carries aggregates only (count tables, no ids, no
  times). A "one mark per participant" view is fine as positions and colours; **a tooltip or any text that shows an
  individual's responses is a raw row and does not belong on a page that others will see.** Clinical data never, in any
  form. Treat any public host as permanent: unpublished results stay private until their owner decides otherwise.
- **Personal records** (a CV, a list of papers or projects) - one mark per paper, per study, per participant-session
  (counts only).
- **Film** - the same spirit works for a data scene in a video: one mark per thing, one encoding change per beat, the
  caveat spoken at the moment the picture needs it.
- **Right-to-left languages** (Hebrew, Arabic): `dir="rtl"`, digit runs isolated, labels in the words the reader would use
  for the thing, never a variable name.

## Gates (deterministic, run on the built page before anyone sees it)

1. **Marks = records:** count the marks the page draws (expose a debug count) and assert it equals the record count of
   the data file it loaded; print both and the file name, so a check of the wrong file is visible.
2. **No hand-typed numbers:** every number in the HTML text is either produced by the page's own code from the data or
   listed in an allow-list with its source; a script greps the rendered text and fails on any other number.
3. **Unknown is not small:** if a magnitude encoding exists, assert that records with a missing value render with the
   "unknown" style, and print how many.
4. **Every caveat fires at its step:** a list of (caveat id, step) from DESIGN.md, checked against the page's steps.
5. **Contrast, reduced motion, keyboard, 375 px width:** opened in a real browser, screenshots kept.
6. **Privacy gate for research pages:** no text field from an individual record reaches the DOM.
7. **The publishable folder holds only what may be published** (the page and its data). Build reports, join reports and
   screenshots go to a separate git-ignored folder that is never served: a join report lists exactly the unmatched and
   unpublished items. (A report naming unpublished items once sat beside index.html and in git; a commit review caught it.)
8. **A build never imports or executes code from a shared or synced folder** (a team drive, a lab share): read what you
   need from it as data (`ast.literal_eval` on a literal table, a JSON file) and re-implement the rule, with a parity diff
   against one run of the original. Putting a shared folder first on `sys.path` lets any file there replace a standard
   module.

## Credit

Technique learned from "קיצונים משני הצדדים" by Eyal Raz (research, design, development; eyalraz.com) with Moshon
Zer-Aviv and Oren Persico, for The Seventh Eye with Shenkar. Their code and words are theirs: learn the technique,
never copy their code or text into your pages.
