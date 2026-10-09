# Teardown: "קיצונים משני הצדדים" (both-sides.the7eye.org.il)

Read 2026-10-08 as TEXT only (curl to stdout, nothing executed, no site files saved), by a reading agent for the
data-storytelling skill, plus the methodology page read directly in the browser. Behaviour is inferred from the code and
its (very thorough) comments. File and function names are cited so a claim can be re-checked; their code is not copied.
Numbers are as of the read date (the site refreshes weekly).

---

## 0. The data: `/events.json`

A 5.2 MB flat JSON array, 13,876 records, 2023-01-01 to 2026-10-02 (the methodology page, dated 5 October 2026, says
12,283 events shown; the file holds more rows than the page displays). Unsorted; `initPage7` sorts by date and splits by side.

| field | type | notes |
|---|---|---|
| `rowId` | `"row-N"` | stable source-row id, unique; the join key for translations and the tutorial squares |
| `side` | `"left"` / `"right"` | derived from `actor` server-side |
| `actor` | 6 lowercase English keys | settlers 7,337; protesters against government 2,781; peace movements 2,399; arab israelis 581; haredi jews 474; right wing protesters 304 |
| `category` | Hebrew string, 10 values | the join key; non-violent demonstration 5,084 ... pogrom 20 |
| `date` | `YYYY-MM-DD` | |
| `descHeMedium` | Hebrew text, 30-342 chars (median 110) | edited, translated description |
| `crowd` | int or null | 3,871 numeric, **10,005 null (72%)**, range 1-500,000, heaped at 50 / 300 / 3,000 |

Translations: `events-en.json`, `events-ar.json`, maps rowId -> text. Example (glossed): a Haredi protest in Jerusalem
blocking traffic, crowd 300; two settlers vandalising graves, crowd null - so null does not only mean "no number reported".

## 1. Architecture

- **No framework, no D3, no build step.** ~18 classic script tags, one global scope. `server.py` only for local dev
  (xlsx -> JSON, a localhost-gated reload poller).
- **Canvas for the ~14k data marks, DOM for the few** (200 hero dots, 8 tutorial squares, 6 legend rows, tooltips, drag
  pills), **SVG only for the dashed borders** (`updateTextCardFrameDashes`, `updateTooltipDash`).
- **Which scene owns the canvas:** an IntersectionObserver with rootMargin -50%/-50% fires when a `.text-section` crosses
  the viewport centre; `PAGES[currentPage]` picks the draw function (`nav.js setActivePage`).
- **Threshold beats:** `watchCardThreshold` watches a card's top crossing a fraction of the viewport (per-fold table
  `FOLD_FRAC_DESKTOP/MOBILE`, mostly 0.75); down = trigger(1), up = trigger(0); `makeTrigger(duration, onTick, onSettle)`
  plays a fixed-duration animation on wall-clock time; a new leg starts from the current point, so reversing mid-way is
  seamless; scrolling is never blocked; the first call primes state so a mid-page reload does not replay passed beats.
- **Scrubbed motion only where position is the content:** a 560vh empty section maps scroll fraction to a date
  (`page7-scrub.js`), smoothstep ease-in over the first 15%, ends half a viewport early so the lagged fill settles.
- **Scroll-coupled fades** where motion must track scroll both ways (`fold13ScrollT`).
- **No CSS sticky for the chart:** the canvas is fixed, cards scroll over it.
- **Easing:** sine in-out (`p9Ease`) because it is symmetric (a reversed beat looks identical); cubic-out for pops. Rule:
  slice raw 0..1 progress into beats and re-ease each slice; never ease an eased slice.
- **Durations:** group transitions 1,900 ms; size morph fly 1,311 ms then tiers grow 421 ms each, staggered 131 ms,
  biggest first; timeline-to-grid glide 1,700 ms; legend filter shrink 380 / cascade 350 / fly 550 ms; hover swell 120 ms;
  hover dim ramp 90 ms; tooltip grows 400 ms, text types 9 ms/char.
- **Smooth with 14k marks:** one Path2D per colour filled in one call (individual fillRect had been ~48% of draw time);
  skip redundant fillStyle; cache isMobile()/viewportH() (live innerWidth reads were 14.4% of CPU on a throttled phone);
  draw at most once per frame; per-row cursor memo instead of per-dot performance.now(); vertical cull; snap to whole
  device pixels; memoised dash lengths; passive scroll listeners handled once per frame; mobile height-only resize ->
  repaint plus a debounced relayout. No workers.

## 2. The unit-visualization layouts

1. **Hero -> camps -> legend** (folds 1-4): 200 hero dots; 12 take group colours and fly into two camp columns; labels
   type in; the groups glide into a side mini-legend that stays. The reader watches the legend being built.
2. **Tutorial squares** (fold 5): 8 grey squares under "each square represents one physical political action" are 8
   REAL events (the 4 earliest per camp, keyed by rowId); they take their colours and fly to their own dots on the timeline.
3. **Timeline** (fold 8): on desktop the year axis runs vertically down the centre; each row is a fixed span of days
   (solved per viewport, max 8); each camp's dots grow outward from the axis, so **row width = event count** - a mirrored
   histogram of unit squares. Overflowing days spill down; small deterministic random gaps keep texture; months cascade in
   with a pop as the scrub reaches them; 9 headline events annotate the axis on desktop, 6 on mobile; an end card shows the
   last-updated date patched from the data; at the end the field zooms out to fit. Square size solved per viewport
   (desktop up to 3.5 px with a 1.5 px gap; mobile the largest square that fits the bigger camp at 86% fill).
4. **Packed block sized by crowd** (fold 9): arriving turns it on. **Tiers, not a ramp** ("a few sizes read, a ramp
   doesn't"): cuts 100 / 2,500 / 25,100 / 100,000 / 250,000 -> sides of 1, 2, 3, 6, 9, 14 cells, aligned with the
   methodology's word-to-number mapping. A skyline packer per camp (`p7GridPlace`) picks for each n x n block the run of
   rows with the lowest cost (reach + stranded cells + push away from other big blocks); 1-cell squares backfill holes;
   packing is lazy and cached. The lattice is quantised to device pixels once. Morph: fly first, then grow in tier waves,
   biggest first, growth capped at 2x what fits so nothing overlaps mid-flight; off = the exact mirror.
5. **Uniform again, then the "legitimate zone"** (folds 10-11): shrink in place smallest tier first (biggest-first froze
   the field ~700 ms, "which reads as the trigger being broken"), then the field glides to a bottom zone.
6. **Extreme vs legitimate** (fold 12): above a divider, "extreme" dots fill row by row per camp in colour bands; the
   shared column count only grows; below, on desktop every event keeps a permanent slot so moving a category leaves gaps
   rather than reflowing; on mobile an 8-row bar per camp shrinks from its outer end.
7. **Closing** (folds 13-15): extreme dots spread into a seeded shuffled field, then pair into cross-camp "dominoes" that
   recolour into a mix of all six colours.

**Identity across layouts:** each event is one object; every layout is a Map keyed by it; every transition captures
where the mark was LAST PAINTED (also mid-flight) and interpolates to the new target; a scene hand-over mid-flight sets
the new animation's start back by the elapsed time so the flight continues on the same clock; marks never fade.

## 3. Interaction

- **Desktop tooltip:** date (DD.MM.YYYY) and description, not the crowd number; the hovered square swells to its crowd
  tier and pushes neighbours aside (exact within 12 cells, fading to nothing by 30); squares without a crowd figure don't
  swell; everything else dims to 27% with a 90 ms ramp (an instant dim flickered); box filled with the group colour, white
  text, a luminance cap found by bisection and re-checked after rounding, and a hand-picked override for the yellow
  (darkened yellow reads olive-brown, a different colour); one square corner sits on the dot; mirrors near edges.
- **Touch:** docked tooltip clamped to 3 lines with more/less; press-and-hold 300 ms (<10 px movement) opens a 96 px 4x
  loupe 60 px above the finger, a nearest-neighbour copy of the main canvas; nearest dot within 44 px; instruction copy
  differs per device.
- **Keyboard on the canvas:** focusable while the timeline is live; up/down step by date, left/right jump to the
  nearest-dated event in the other camp, Home/End, Esc; drives the same hover code; announces "date - group: description"
  in a polite live region after 250 ms.
- **Legend filter:** rows are role=button with aria-pressed; removing a group shrinks its dots first, then the rest fly
  to close gaps; restoring is the reverse; the filter persists and stays marked after it can no longer be changed.
- **"Show event size" toggle:** appears at the moment squares return to one size; switches uniform <-> tiered, also on
  the drag fold.
- **Drag to define "extreme":** ten pills in fixed slots (removal leaves a hole, no reflow; the mild "non-violent
  demonstration" deliberately not in the first slot), each with an info tooltip carrying its definition; desktop drag or
  click, mobile tap, keyboard Enter/Space with aria-pressed and aria-describedby. Recount: the category's dots migrate up
  into the extreme blocks; the per-camp "N events" labels HOLD the old number while dots fly, then count up with easing;
  dropped category names float in the central gap; a live region speaks the category, "k of 10 classified as extreme"
  and the per-camp counts. **Scroll gate:** the closing is unreachable until at least one category is marked; wheel,
  keys and touch blocked, locked folds `inert`, and the reason announced.

## 4. Visual system

| Camp (side) | Group | Colour |
|---|---|---|
| Change bloc (left) | Arab Israeli actors | #31CE1C |
| | Judicial-overhaul and government-policy opponents | #6B89FF |
| | Hostage-deal supporters and war opponents | #FF1A94 |
| Netanyahu coalition (right) | Settler movements | #F9B624 |
| | Conservative right-wing groups | #F024FF |
| | Haredi protesters | #454545 |

- Camps are told apart by POSITION, not hue family; colour lookup by actor key (matching by hex once silently failed).
- Paper `#FDFCFF` (also the canvas clear colour), ink `#111`, muted `#767676`, hairline `#E1E1E1`.
- Type: Discordia (licensed Hebrew display face) for title cards and the hero; Assistant (variable 300-800) for all body,
  UI and canvas labels; Josefin Slab only for the author's monogram; Arabic: Tajawal titles, IBM Plex Sans Arabic body,
  titles bumped to match Hebrew optically.
- Text cards: white, opaque, fit-to-text up to 456 px, radius 8, padding 21/29, centred, a 1.25 px SVG dashed outline
  (2/2) whose dash period is stretched to divide the perimeter exactly, redrawn by a ResizeObserver. The tooltip shares
  the dashed vocabulary.
- Almost no chrome: no gridlines or ticks, one year axis with a few annotation cards, a small side legend whose labels
  un-type once the timeline starts, logos in a corner, a globe button for language. Spacing in px/vh, never dvh.

## 5. Honesty and method devices inside the page

1. Scope before data ("we focus on groups acting physically in public space only").
2. The encoding stated first, with 8 real events.
3. The source at first contact (ACLED and "המבצר", linked), then the date range, and that the legend filters.
4. The magnitude caveat in the card that fires the size view.
5. A caveat when size is removed ("for the numerical comparison, all squares one size; use the button to show size").
6. The contested judgement handed to the reader ("the line between legitimate and extreme is not always agreed").
7. A permanent legend note: inclusion, sources, editing and translation, that classification and crowd estimates came
   from OpenAI language models, and "this analysis is the project's responsibility, not the data sources'".
8. An outro method summary: statements without physical action excluded; an event in both sources counted once; an event
   goes to the group doing the main action, not victims or responding forces; the most severe action decides the
   category on a 10-step ladder built for the project; models with many rounds of manual correction; a group label does
   not describe a whole public; "the database reflects what was reported, not everything that happened"; the full method
   link; an error address that says what to include (event date, assigned group, the correction).
9. The methodology page (read in the browser): ACLED 14,451 records pulled on a stated date, raw data not republished per
   ACLED's terms, the ACLED paper cited; "המבצר" 3,778 records; 5 events added by hand; records whose only source was the
   PLO negotiations department dropped (3,806) unless also in "המבצר" (230 kept); dedup "המבצר" vs ACLED by same place
   within +-1 day, models flag match / different / uncertain, borderline cases settled by hand (1,714 duplicates; 87
   internal); ACLED record kept by rule. Seven model stages (actor, split, category, Hebrew translation, crowd, rewrite of
   "המבצר" lines into the same style, English/Arabic), each with its own written prompt, published in an appendix by code
   filename with the run order; each decision stores a short reason, a confidence and a review flag; the crowd stage
   stores the quote the number came from; prompts refined over many rounds; a manual fix is date-stamped and re-runs skip
   it. Crowd: main actor's side only, the highest estimate, vague words mapped to fixed values IN CODE (dozens 50,
   hundreds 300, thousands 3,000, tens of thousands 30,000, hundreds of thousands 300,000; "tens" = 30), ranges to their
   upper end, missing left missing; crowd known for 3,604 of 12,283. A severity ladder built "with reference to" CAMEO,
   the Goldstein scale and the UK ONS crime severity score, with border rules written out; "pogrom" given an operational
   definition where every condition must appear explicitly. Limitations: coverage differs by region, period and group;
   two selection rules act on the same group in opposite directions; a category simplifies; event count is not people
   or casualties; model processing may err.
10. Nothing hand-typed: the screen-reader summary, the last-updated date and all counts are computed from events.json.

## 6. Accessibility, direction, languages, mobile, reduced motion

- Canvas `role="img"` with aria-label inside a labelled region; an off-screen summary built from the same data (camp
  totals, per-group counts, category breakdown, date range, key axis events); canvas, legend rows and pills keyboard
  operable; one shared live region (cleared and rewritten so a repeat is still read); focus-visible rings; landmarks;
  the language switch is a disclosure, not an ARIA menu; locked folds `inert`.
- Reduced motion read live; one choke point (`makeTrigger` returns the end state at once); CSS transitions 0.01 ms;
  deliberately NOT disabled: the scrubbed timeline fill, "it is the content, not decoration".
- Three static pages (`/`, `/en/`, `/ar/`) sharing assets through `<base href="../">`, each with its own card text,
  hreflang and share tags; `tr()`/`trf()` look strings up by the Hebrew string, with `{slot}` placeholders so each
  language orders the sentence; ACLED's leading "On 6 January 2023, ..." stripped from English descriptions because the
  tooltip shows the date; RTL via `dir` on html for Hebrew/Arabic, per block for English; chart geometry identical.
- Mobile: one cached 600 px breakpoint; square size and density solved per phone; docked tooltip; loupe for hover; tap
  for drag; a legend bar with a panel; shorter mobile headlines; no sideways scroll; after rotation the reader's place
  is restored by scroll FRACTION.

## 7. Other clever things

- Content and draw code apart: each fold is a plain section with one h2 in a card; a fold can be parked with `hidden`
  and the fold numbers renumber; one array of draw functions, one table of trigger lines.
- Fonts load before layout, and layout is measured again after the swap.
- Every animation constant is a global var driven by a live slider panel; the chosen value is written back with a date
  ("manual/-baked 2026-09-19"); rejected alternatives are recorded as "Removed - don't reintroduce".
- Pipeline: xlsx -> server.py -> JSON; camp derived from actor; the axis end date moves with each weekly refresh.

## What not to copy (detail)

- **Unknown drawn as small.** `p7BulgeTier` returns tier 0 for null crowd, identical to "under 100". Missing is lopsided
  by camp (about 86% of right-camp events vs 53% of left-camp, counted from events.json), so the size view partly encodes
  reporting gaps and nothing on the page says so.
- No size key; a 1:6,000 crowd range becomes ~1:196 in area across 6 tiers, unstated; the tooltip never prints crowd.
- The closing domino field is padded to a fixed 9,250 dots with non-events (`P12_DOT_COUNT`).
- `user-scalable=no, maximum-scale=1` disables pinch-zoom on 1-3 px marks.
- A forced interaction gates the ending (accessible and announced, but use at most once).
- Engineering shape: page7.js is 510K, hundreds of global tuning constants, special-case hand-offs between files,
  comments doubling as a change log. Reusable shape instead: scenes as `layout(records) -> targets`, one tween engine
  keyed by id, one trigger primitive.
- Typewriter reveals everywhere; hand-placed Figma coordinates; the 5.2 MB JSON with every description loaded up front.
- Coverage asymmetry lives only on the methodology page although it affects the headline count; it deserves a card.
- Site-specific: the camps and bloc names, Hebrew-string-as-key translation (good only when the source language is
  fixed), partner branding, the licensed Discordia face, the model pipeline itself.

Stale or unverified: one comment calls the size grid "desktop only" though mobile has its own toggle row; index.html
says "a real text alternative is still owed" though one exists; `p7FilterSoloOnSide` not traced.
