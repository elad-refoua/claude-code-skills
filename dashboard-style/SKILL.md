---
name: dashboard-style
description: "An opinionated dark, data-dense dashboard design system. Apply when building dashboards, data monitors, comparison tools, or data explorers. Triggers: 'dashboard', 'monitor', 'data explorer', '/playground for dashboard'. Boundary: a guided data STORY for a general reader (scrollytelling, explorable explanation, findings for the public) is the data-storytelling skill; its spirit (one mark per real thing, caveat at the moment it matters, method open) applies to dashboards too."
---

# Dashboard Design System

Apply these rules when building any dashboard, data monitor, comparison tool, or data explorer — whether via `/playground`, standalone HTML, or any visualization tool.

## Before you build

1. **Ask what the reader knows, and what you are about to assume they know.** A dashboard is the
   purest case of that gap: you have read the data and the reader has not. Each gap shows up as a
   specific defect —
   - a variable name or internal tag used as a chart title (`q17_screener`, `scale_f2`) instead of
     the question the participant was actually asked;
   - a number with no base, no unit and no comparison, so the reader cannot tell whether it is big;
   - "the gap", "this factor", "it" — pronouns pointing at something only the builder can identify;
   - a coined label for a construct the reader has never met, presented as if it were standard;
   - an invented meaning for an identifier you did not actually look up;
   - a page that stacks several decisions on the reader at once with no order of importance.

   The test, for every panel: **could someone who never opened the data file read this panel and
   say, correctly, what it shows and what it does not?** If a label only makes sense to the person
   who wrote the cleaning script, it is wrong — rename it to what the participant saw. Pair it with
   Lesson 11 (every number speaks in words) and Lesson 22 (every chart carries its n, every
   difference carries a test): those are the mechanical half, this test is the judgement half.

2. **Read `~/.claude/skills/dashboard-style/lessons.md`** — design principles learned from feedback
   on previous dashboards. Lessons override this base guide when the two conflict.

## Learning Protocol

**After the user corrects a dashboard**: Extract the PRINCIPLE behind the correction and append it to `lessons.md`.

### What to save (PRINCIPLES):
- "Prefer showing raw numbers alongside percentages — never percentages alone"
- "When two groups are compared, always show both side by side, never one after the other"
- "Statistical test details belong in expandable panels, not in the main view"

### What NOT to save (TECHNICAL REQUESTS):
- "Change the bar color to #abc123" — this is a one-time request, not a principle
- "Make this table wider" — layout tweak for a specific dashboard
- "Add a filter for date range" — feature request, not a design principle

### The test: Would this apply to the NEXT dashboard I build?
- Yes → save as principle in `lessons.md`
- No, it's specific to this dashboard → don't save

## Design Philosophy
- **Dark data-dense research UI** — Twitter/X dark mode meets Tailwind slate
- **High information density** — numbers everywhere, filter by need
- **Zero dependencies** — no Chart.js, no D3, pure CSS/HTML divs for all charts
- **Self-contained single HTML file** with inline CSS/JS
- **Auth-gated** — login screen first, dashboard behind it
- **Expandable detail** — compact by default, expand for documentation/stats

## Color System

**The palette lives in CSS custom properties on `:root`, and nowhere else.** Charts are built in
CSS/DOM with colour written inline on each bar, so any JavaScript that keeps its own hex copies will
silently ignore a theme change. JS reads the tokens at render time:
`getComputedStyle(document.documentElement).getPropertyValue("--accent")`. Hard-coded hex in JS is a
defect. (Lesson 23.)

Tokenise the values that hide, or the second theme will break on them: header gradient, sticky-nav
background, badge background AND border, table row-hover, the 2px table-header underline, and
`--on-fill` — the ink colour for text drawn ON a filled bar or heat-map cell (near-black in dark,
white in light).

### 3-Level Background Depth
| Layer | Hex | Role |
|-------|-----|------|
| Page | `#0f1419` | Deepest background |
| Panel/card | `#16202a` | Cards, sidebar, sections |
| Inner/input | `#0f1419` | Inputs revert to deepest |
| Expanded panel | `#0d1520` | Slightly darker than card for depth |

### Text Hierarchy (5 levels)
| Level | Hex | Use |
|-------|-----|-----|
| Primary | `#e7e9ea` | Body text |
| Secondary | `#8b98a5` | Labels, subtitles |
| Muted | `#64748b` | Timestamps, footnotes |
| Data | `#c0c8d0` | Table cells |
| Disabled | `#475569` | Disabled states |

### Borders
- Standard: `#2f3542` (1px solid everywhere)
- Focus/active: `#1d9bf0`
- Table header underline: `#475569` (2px)

### Semantic Accent Colors
| Meaning | Hex | Background |
|---------|-----|------------|
| Primary / Blue | `#1d9bf0` | `#1d3a5c` |
| Secondary / Orange | `#f0883e` | — |
| Success / Normal | `#4ade80` | `#1a3a2a` |
| Warning / Mild | `#a3e635` | `#2a3a1a` |
| Caution / Moderate | `#facc15` | `#3a3a1a` |
| Severe / Orange | `#fb923c` | `#3a2a1a` |
| Error / Extreme | `#f87171` | `#3a1a1a` |
| Special / Purple | `#a78bfa` | — |

Badge pattern: dark saturated background + bright same-hue text, always.

### Light theme (optional, `:root[data-theme="light"]`)
Offer it behind a button when the dashboard will be read in a bright room or printed. It is a
**second design, not an inversion**: dark is *pale accents on a deep ground*, so light is *saturated
ink on a cool paper ground*, with every accent darkened until it clears WCAG-AA on white
(`#6db8e8` sky -> `#0d6d8f` teal). Naive inversion gives washed-out pastels that fail contrast.

Because charts carry colour inline, the theme handler must **re-render**, not restyle: wrap
section-building in `buildAll()` and call it again on switch. Persist in `localStorage` inside
try/catch, default to dark. Reference light tokens:

| Token | Light value |
|-------|-------------|
| `--bg` / `--panel` / `--inner` | `#eef1f5` / `#ffffff` / `#e8edf3` |
| `--line` / `--line-strong` / `--hover` | `#ccd5e0` / `#94a3b4` / `#e4ebf4` |
| `--tx` / `--tx2` / `--tx3` | `#16202b` / `#4a5a6b` / `#6b7a8a` |
| `--accent` / `--accent-bg` | `#0d6d8f` / `#d6ecf5` |
| `--good` / `--warn` / `--crit` / `--warm` / `--violet` | `#1a7a4f` / `#8a6005` / `#b2394a` / `#a5530f` / `#5a45a8` |
| `--on-fill` | `#ffffff` |

### Bar Fill Gradients (NEVER flat colors)
- Blue: `linear-gradient(90deg, #1d6fb0, #1d9bf0)`
- Orange: `linear-gradient(90deg, #c06020, #f0883e)`
- Vertical: `linear-gradient(180deg, #38bdf8, #0284c7)`

## Typography
- **Font**: `-apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif`
- **Title**: 22px bold, colored span for emphasis
- **Section title**: 13-15px, primary accent color
- **Card label**: 10px uppercase, letter-spacing 0.8px, muted
- **Card number**: 24-30px bold, semantically colored
- **Card subtitle**: 11px muted
- **Table header**: 11px weight 600, muted
- **Table cell**: 12px
- **Badge**: 10-11px weight 600

## Component Patterns

### Cards
```css
background: #16202a;
border-radius: 10px;
border: 1px solid #2f3542;
padding: 14px 16px;
```
Structure: tiny-label -> big-number -> small-subtitle

### Sections
```css
background: #16202a;
border-radius: 10px;
padding: 16px 18px;
border: 1px solid #2f3542;
margin-bottom: 18px;
```
Title: accent color, border-bottom 1px solid border-color

### Badges
```css
padding: 2px 9px;
border-radius: 10px;
font-size: 10-11px;
font-weight: 600;
```

### Variable Chips (interactive)
```css
padding: 4px 10px;
border-radius: 14px;
font-size: 11px;
cursor: pointer;
border: 1px solid #2f3542;
/* Active: */ background: #1d3a5c; border-color: #1d9bf0; color: #1d9bf0;
/* Category left border: 3px solid [category-color] */
```

### Buttons
- Standard: `background: #334155; color: #94a3b8; border-radius: 6px; font-size: 12px`
- Primary: `background: #1d9bf0; color: #fff` OR `background: #0c4a6e; color: #38bdf8`
- Danger: `background: #450a0a; color: #f87171`
- All: `transition: all .15s`, no box-shadow

### Mode Toggle (segmented)
```css
display: flex;
border: 1px solid #2f3542;
border-radius: 6px;
overflow: hidden;
/* Children: */ flex: 1; border-right: 1px solid #2f3542;
/* Active: */ background: #1d3a5c; color: #1d9bf0; font-weight: 600;
```

### Tables
- `border-collapse: collapse; width: 100%; font-size: 12px`
- Row hover: `background: #334155; transition: background .12s`
- Zebra: `tr:nth-child(even) td { background: rgba(22,32,42,.5) }`
- No outer border, subtle row separators

### Bar Charts (CSS only)
```css
/* One shared geometry per chart. The label and value columns are FIXED widths, never auto:
   an auto column is sized by the longest label, so bars in different rows would start at
   different x positions and their lengths could no longer be compared by eye. */
.chart { --lbl: 180px; --val: 104px }
.row   { display: grid; grid-template-columns: var(--lbl) 1fr var(--val);
         gap: 10px; align-items: center; margin-bottom: 7px }
.row .lbl { font-size: 12px; color: var(--tx-data); line-height: 1.35; overflow-wrap: anywhere }
.track { height: 19px; background: var(--inner); border-radius: 5px; overflow: hidden }
.fill  { height: 100%; border-radius: 5px; transition: width .45s cubic-bezier(.2,.7,.3,1) }
.row .val { font-size: 11.5px; text-align: left; white-space: nowrap }

/* Sentence-length labels get their own line and a full-width bar beneath - same guarantee,
   achieved by construction rather than by tuning a column width. */
.chart.stacked .row { display: block }
.chart.stacked .barline { display: grid; grid-template-columns: 1fr var(--val); gap: 10px }
```
**Alignment rule (Lesson 21):** inside one chart every bar starts at the same x and ends on the same
scale. Never `min-width: fit-content` on the fill — the label expands the bar and overrides the data
width. Always gradient fill, never flat. One GLOBAL max per chart, never per-row normalisation
(Lesson 8).

**Verify, do not eyeball:** for each chart collect
`[...chart.querySelectorAll(".track")].map(t => Math.round(t.getBoundingClientRect().right))`
(`.left` in LTR) and assert the set has exactly one value. Run it in BOTH themes.

### Sample-size badge (every chart, no exceptions)
```css
.nbadge { font-size: 10.5px; font-weight: 600; color: var(--tx3); background: var(--inner);
          border: 1px solid var(--line-soft); border-radius: 9px; padding: 1px 7px }
```
Sits in the card title. Carries the base THAT chart was computed on — in a real survey people drop
out at different points, so there is no single N and a header-only N misleads. (Lesson 22.)

### Significance chip + test table
```css
.sig      { font-size: 10px; font-weight: 700; padding: 1px 7px; border-radius: 9px }
.sig.yes  { background: var(--good-bg); color: var(--good); border: 1px solid var(--good-line) }
.sig.no   { background: var(--chip-bg); color: var(--tx3); border: 1px solid var(--line) }
```
Every difference the page DISPLAYS gets a test, an effect size and a confidence interval — not just
a p. Within-subject comparisons (the norm in a survey) use a PAIRED test on complete pairs, so the
test's n is smaller than the chart's n; say so in the UI. Correct within each family (Holm for a
handful of planned comparisons, Benjamini-Hochberg for a correlation matrix), show raw and corrected
p, and decide the verdict on the corrected one. Give every displayed proportion a Wilson 95%
interval and every mean a t interval. In a heat map, draw cells that fail correction hollow/dashed.
No "trending toward significance". (Lesson 22.)

### Participant funnel
One continuous list from the first click to the last answer. Start at the platform's session count,
not at your data export — sessions that opened and never closed exist in the platform's counts and
not in the export. Phrase every row as a state a PERSON reached ("gave consent", "passed the
screener"), never as an operation on rows ("exclusions"). Continue PAST the eligibility gate through
each block of the instrument: where drop-off concentrates is usually the most actionable finding on
the dashboard. Add a "% of everyone who entered" column so all rows share one scale. Never let two
different departures share a row. (Lesson 26.)

### Donut Charts (CSS conic-gradient)
120px diameter, 68px center hole (panel background color), no SVG

### Login Screen
```css
/* Background: */ linear-gradient(135deg, #0f1419, #1a2530)
/* Card: */ border-radius: 12px; padding: 40px; max-width: 360px; text-align: center
/* Title: */ colored span for project name
/* Input: */ full-width, dark bg, centered text
/* Button: */ full-width, primary accent, white text, 600 weight
/* Error: */ #f87171, 12px, hidden by default
```

### Expandable Panels
```css
.detail-toggle { font-size: 11px; color: #1d9bf0; cursor: pointer;
                 background: #0f1419; border: 1px solid #2f3542; border-radius: 4px }
.detail-panel { display: none; background: #0d1520; border: 1px solid #2f3542;
                border-radius: 8px; padding: 12px }
.detail-panel.open { display: block }
```

## Layout Patterns
- **Sidebar + Content**: `grid-template-columns: 300px 1fr` (responsive -> 1fr at 900px)
- **Card Grid**: `repeat(auto-fit, minmax(440px, 1fr))`
- **Stat Cards**: `repeat(auto-fit, minmax(145px, 1fr))`
- **Spacing**: 12-18px gaps, 14-18px padding, 18px section margin

## Interaction Patterns
- Hover: brighten one shade, never add shadows
- Active toggle: class-based, instant (no animation)
- Expand/collapse: `.open` class toggle, `display: none/block`
- Bar animation: `transition: width .4s ease`
- Loading spinner: `border-top-color: [accent]; animation: spin .8s linear infinite`

## Key Invariants (ALWAYS follow these)
1. Every panel passes the reader test in "Before you build" — no chart title, label or narrative
   sentence may assume knowledge the reader does not have
2. No external dependencies — everything inline
3. No box-shadow anywhere (depth from bg color alone)
4. Bar fills are always gradients
5. Badges use dark-bg + bright-text (same hue)
6. 3-level background depth system
7. Numbers big and bold, labels small and muted
8. Auth gate on anything carrying individual-level data. Aggregate-only pages (means, counts,
   distributions) may ship without one — see Lesson 7's two-tier rule — but individual rows never
   go in the HTML source, and free text and e-mail addresses never leave the analysis script
9. Transitions on all interactive elements (.15s)
10. System font stack, no custom fonts
11. Hebrew-capable when needed (RTL-aware, `dir` attribute). **A Hebrew page ships as pure
    ASCII**: `\uXXXX` escapes inside `<script>` (`json.dumps(..., ensure_ascii=True)` does the
    payload), `&#NNNN;` everywhere else. A file with no byte above 0x7F decodes identically under
    UTF-8, windows-1252 and ISO-8859-1, so no server or wrapper can turn it into mojibake. Verify:
    read the built file as bytes, assert `all(b < 128)`, then decode under three charsets and assert
    the strings match. (Lesson 19.)
12. Look survey options up by VALUE, never by array position — a distribution contains only the
    options someone chose, so an unchosen option shifts every index after it (Lesson 20)
13. Verify a metric's LABEL against the live instrument definition, never against a codebook or
    build plan — documents drift, the flow is the instrument (Lesson 24)
14. A dashboard already shared outward is not yours to silently correct: report the finding and the
    proposed fix, deploy on a yes (Lesson 25)
