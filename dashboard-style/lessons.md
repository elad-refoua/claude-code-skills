# Dashboard Design Lessons

Principles learned from corrections and feedback on real research dashboards.
Read this file BEFORE building any dashboard. These override the base style guide when in conflict.

## How to Read This File
- Each lesson is a **design principle**, not a technical spec
- Lessons are ordered oldest-first
- If a principle contradicts the base style guide, the lesson wins

---

## Lesson 1: Side-by-side is the killer feature for group comparisons (2026-03-10)
**Source**: A cross-group comparison portal, Analysis tab

When a dashboard compares two groups (countries, conditions, subsamples), the most powerful view is running the *same analysis* side by side — not switching between tabs or dropdowns. Users instantly spot cross-group differences when identical visualizations are placed next to each other. Make "Both" the default when two groups exist.

## Lesson 2: Mode-based UI — shared globals, mode-specific selectors (2026-03-10)
**Source**: Analysis tab (4 modes: Correlation, Regression, Mediation, Moderation)

When a tool has multiple analysis modes, share the global controls (group filter, sample filter) across all modes but show/hide mode-specific variable selectors. This keeps the sidebar from overwhelming users while preserving full control. One "Run" button for everything — the mode determines what happens.

## Lesson 3: Variable chips grouped by construct, not alphabetically (2026-03-10)
**Source**: Analysis tab variable selection

Researchers think in constructs (Demographics, Usage Experience, Distress), not alphabetical lists. Group selectable variables by their conceptual domain with a color-coded left border per category. This matches how researchers design analyses — "I want the distress variables and the satisfaction variables."

## Lesson 4: Canvas for continuous plots, DOM for structured layouts (2026-03-10)
**Source**: Analysis tab visualizations

Scatter plots and regression/interaction lines need pixel-level control — use Canvas. Heat maps, forest plots, and pathway diagrams need text layout, click handlers, and flexible sizing — use DOM elements with CSS. Don't force everything into one rendering approach.

## Lesson 5: Visualization first, numbers second (2026-03-10)
**Source**: Analysis tab result rendering order

Show the chart/diagram first (pattern recognition is instant), then summary stats (R², F, p), then the full coefficient table for those who want exact numbers. This mirrors how researchers actually read results — they look at the figure, check if it's significant, then dive into specifics.

## Lesson 6: Client-side stats are viable for research dashboards (2026-03-10)
**Source**: Analysis tab JS math library

For datasets under ~5000 rows, running OLS regression, logistic regression, Sobel mediation, and moderation analysis entirely in the browser is fast and eliminates server round-trips. Zero-dependency statistical computation gives instant feedback and simplifies deployment. No R/Python backend needed for interactive exploration.

## Lesson 7: Two-tier data architecture for research portals (2026-03-10)
**Source**: Portal aggregate vs. individual data endpoints

Aggregate statistics (means, counts, distributions) can live in the main dashboard with lighter security. Individual-level data for analysis requires a separate authenticated endpoint. This protects participant privacy while still enabling rich interactive exploration. Never embed individual data in the HTML source.

## Lesson 8: Visual length must be strictly proportional to the data value (2026-03-13)
**Source**: A comparison portal's bar chart bug

A comparison bar's visual length is the primary information channel — anything that distorts the length-to-value mapping destroys the chart's usefulness. The user WILL notice when two bars look the same length but represent different values.

**Principle**: Nothing should influence bar width except the data value and a shared reference maximum. No additive constants, no CSS minimum widths, no per-row normalization. Every bar in a chart must share a single global maximum so they are visually comparable.

**Common traps**:
1. Adding a constant offset to prevent zero-width bars — instead, use a tiny minimum (0.5%) that doesn't distort perception.
2. CSS `min-width:fit-content` on bar elements — the text label expands the bar, overriding data-driven width. Use `overflow:visible` so labels can extend beyond the bar.
3. Per-row normalization in categorical charts (each row's max becomes 100%) — makes all "largest" bars identical regardless of actual value. Always compute a single global max across all categories.

## Lesson 9: The dashboard IS the empty state (2026-04-15)
**Source**: A research data explorer. The first version showed blank pages, and the feedback was that the work was not good enough.

**Why this matters**: A blank page with "Select a variable" signals to the researcher that the tool is passive — it waits for them to know what to ask. But the whole point of an explorer is DISCOVERY. Most researchers open the dashboard to understand the data, not to verify a specific hypothesis. If they already knew what to look at, they'd write R code. The blank page defeats the purpose.

**The deeper principle**: The "empty state" is actually the MOST IMPORTANT state — it's what 100% of users see first. It must answer the question: "What's interesting in this data?" It should tell a story before anyone clicks anything. Show the sample (N, demographics), the key patterns (distributions, percentages), the strongest effects. Make it clickable — each mini-chart is a doorway into deeper exploration.

**Implementation**: Auto-compute overview cards (N, key %, means), a 2x3 mini-chart gallery of the most theoretically important variables, and highlighted findings. Every mini-chart is a click target that takes you to the full variable view. The overview IS the home page.

## Lesson 10: Think in research questions, not statistical procedures (2026-04-15)
**Source**: A research data explorer, Advanced Analysis tab.

**Why this matters**: Researchers think "What predicts dropout?" — not "I need logistic regression with DV=Dropout and IVs=Distress_Total, Engagement_Mean, Attachment_Anxiety." The gap between the research question and the statistical setup is exactly where confusion, errors, and abandonments happen. A dropdown that says "Select DV" requires the researcher to do a mental translation that the tool should do for them.

**The deeper principle**: The best analysis tools work at the level of the user's actual goal, not at the level of the statistical engine. Each research question implies a specific statistical approach, a set of variables, and appropriate filters. By pre-packaging these as one-click presets, you eliminate the translation step AND you encode domain knowledge (which variables matter for which question) into the tool itself.

**Implementation**: Show preset cards with: the question in plain language, a brief description of what analysis runs, and an accent color. Clicking auto-configures mode + wave + variables + filter and runs immediately. Always include "Or build your own" for experts who want custom control. The presets should come from the actual published papers/pre-registrations.

**Addendum (2026-04-16)**: When a preset auto-runs, VERIFY every selected variable exists in the chosen wave + filter BEFORE invoking the analysis. If any variable is missing (not available in that wave, has zero non-null values after filtering, or conflicts with the filter — e.g., a W1-only variable in a W2 preset), render an inline warning card that explains exactly which variable is missing and suggests the closest alternative. Never silently null-fail — users assume the preset worked and misinterpret absent output as "no effect." A loud-but-graceful fallback beats a silent bug every time.

## Lesson 11: Every number must speak in words (2026-04-15)
**Source**: A research data explorer's analysis outputs. The feedback asked that everything on screen be transparently understandable.

**Why this matters**: A coefficient table showing β=0.016, p<.001 is meaningless to anyone who doesn't already know what the analysis does. Even experienced researchers can misread which variable is significant. The table is for verification; the narrative is for understanding. They serve different cognitive functions.

**The deeper principle**: Statistical transparency means three layers: (1) the visualization (pattern recognition — instant), (2) the narrative interpretation (meaning — "higher distress predicts the outcome"), and (3) the coefficient table (precision — for those who need exact numbers). Each layer serves a different audience and a different cognitive need. The common mistake is providing only layer 3 and assuming layers 1-2 are "obvious."

**Implementation**: Template-based narrative generation that reads result objects and writes directional, significance-aware sentences. For significance: green "significant predictor" tags. For non-significance: gray "not significant" with no hedging. Optional: AI interpretation button (Gemini) with a clear disclaimer for a richer reading. The narrative appears BETWEEN the chart and the coefficient table.

## Lesson 12: Always show where data comes from (2026-04-15)
**Source**: A research data explorer. The feedback was that it was unclear which values came from wave 1 and which from wave 2.

**Why this matters**: In longitudinal data, the same variable name (Distress_Total) exists in multiple waves. A regression using W1 distress as predictor and W2 distress as outcome is fundamentally different from a W1-only cross-sectional analysis. If the user doesn't immediately see which wave each variable represents, they cannot interpret the results correctly. This isn't a labeling convenience — it's a validity issue.

**The deeper principle**: Context must be embedded in the interface, not in the user's memory. Every variable chip, dropdown option, and results table cell that could be ambiguous about its source must carry its provenance. Use [W1]/[W2] badges, colored borders, and context banners. In cross-wave mode, make it visually obvious that predictors come from one wave and outcomes from another.

## Lesson 13: Navigation must be reversible (2026-04-15)
**Source**: A research data explorer. The feedback asked for a way to get back to the home page.

**The principle**: Exploration requires safe backtracking. If drilling into a variable or running an analysis is a one-way trip, users explore less. A visible "← Back to Overview" button reduces the cognitive cost of clicking something — you know you can always return. This is especially important when the overview contains computed summaries that are expensive to mentally reconstruct.

## Lesson 14: Research tools need a softer palette (2026-04-15)
**Source**: A research data explorer. The feedback asked for softer colors and shapes.

**The principle**: The original dashboard-style design system was built for monitoring dashboards — alert-driven, attention-grabbing. Research exploration is different: researchers stare at the tool for hours, comparing subtle patterns. Saturated colors (#1d9bf0 blue, #f87171 red) create visual fatigue and make small differences harder to spot. Softer, more muted tones (#6db8e8, #e09090) with larger border-radius (12px) create a calmer visual environment where the data — not the chrome — demands attention.

## Lesson 15: A chart for every variable, no exceptions (2026-04-15)
**Source**: A research data explorer. The feedback asked for as many charts as possible.

**Why this matters**: Tables are for lookup; charts are for understanding. When a researcher selects "Distress_Total", they need to SEE the distribution — is it normal? skewed? bimodal? A mean and SD don't tell you that. When they select a multi-choice item such as "Platform used", they need to see which options dominate at a glance. An earlier R Shiny app built for the same data had charts for everything — that was the benchmark.

**The auto-detection logic**: Continuous → histogram (8-10 bins). Binary → donut chart (CSS conic-gradient, 120px). Categorical → horizontal bars sorted by frequency. Ordinal → bars with value labels. Multi-choice set → all items as bars sorted descending. Grouped → side-by-side bars with inline test results. Every chart type must be implemented in pure CSS/DOM — no external libraries.

## Lesson 16: Explanation boxes should be collapsible, not stacked (2026-04-16)
**Source**: A research data explorer. The initial version stacked three permanent banners before every results view: method explanation, "what you're testing," and "how to read."

**Why this matters**: Permanent banners before results become "textbook before data." First-time users need the explanation, but the SAME user returning to the dashboard for the 50th time sees the same walls of text between them and the data they came to examine. Persistent help is paradoxically less helpful — it creates visual noise that experienced users must mentally skip every single time.

**The deeper principle**: Explanation and context are NOT the same thing. Context that reflects the current run ("you are testing X against Y with N=250") stays permanent because it changes with each analysis and prevents misinterpretation. Generic method explanation and how-to-read instructions are *learnable* — they become redundant once learned. Collapse the learnable; keep only the contextual.

**Implementation**: Merge "method explanation" and "how to read" into a SINGLE collapsible panel labeled "About this analysis" with a clear expand/collapse arrow. Default expanded on first visit, remember user preference per analysis mode via localStorage (`help_expanded_<mode>`). Keep "what you are testing" as a permanent, non-collapsible banner that mirrors the CURRENT run's variables. That one card answers "what is this showing me right now" — different cognitive function from the collapsible help.

## Lesson 17: A stats dashboard is only as good as its weakest analysis visualization (2026-04-16)
**Source**: A research data explorer. Initial version had: good mediation path diagram, good correlation heatmap, solid regression forest plot, solid moderation slope bars — BUT logistic regression showed no plot at all, moderation had no interaction lines, and the mediation diagram only showed 2 of the 4 paths.

**Why this matters**: Users judge a research tool by its weakest mode, not its strongest. A dashboard that produces beautiful correlation matrices but falls back to text-only tables for logistic regression or moderation signals "this was rushed." Every analysis type must deliver the same quality of visual storytelling. A missing interaction plot makes moderation look like a procedural detour instead of a meaningful finding.

**The deeper principle**: Each statistical method has a canonical "money shot" plot — the one figure that makes the result interpretable at a glance. Regression has the forest plot of coefficients (or OR on log scale). Logistic regression has the predicted probability curve showing how P(outcome=1) varies across the key predictor, with a rug plot of raw observations. Moderation has the interaction plot showing 2–3 predicted lines at different moderator levels. Mediation has the full 4-path diagram (a, b, c, c′) with coefficients on each arrow. Skipping the money shot makes the analysis feel incomplete — a table with numbers is not a substitute.

**Implementation audit**: Before releasing, go through every analysis mode and list the canonical plot. If any mode lacks one, build it. For multi-path models (mediation), every path must be visually drawn — don't leave c and c′ implied in a table while showing a and b on the diagram.

## Lesson 18: Run an anti-slop pre-flight audit before shipping any dashboard (2026-07-15)
**Source**: Distilled from the MIT-licensed `taste-skill` redesign audit (github.com/Leonxlnx/taste-skill), adapted for research dashboards. Theme-agnostic — applies to dark monitors and light research tools alike.

**Why this matters**: The gap between "it works" and "it feels finished" is a fixed checklist of things AI-generated UI reliably forgets. None of these are visible in a happy-path screenshot; all of them are noticed the moment a real user hits an edge. Ship the checklist, not just the feature.

**The pre-flight checklist** (run every item before calling a dashboard done):
1. **Full state cycles, never just the success state.** Every list/table/chart needs a *loading* state (skeleton loaders shaped like the final content — NOT a generic spinner; reserve space so nothing jumps), an *empty* state (composed, with a next step — see Lesson 9), and an *error* state (inline, in-context, never `window.alert()`).
2. **Tabular figures for all data.** Numbers in columns (KPIs, counts, tokens, dates, coefficients) get `font-variant-numeric: tabular-nums` so digits align. Proportional figures in a data table are an instant tell.
3. **Accessibility is not optional on a research tool.** Every control passes WCAG-AA contrast (>=4.5:1 body, 3:1 for >=18px) — audit each button/label/placeholder/helper/error, no white-on-white CTA, no border-less ghost button on a tinted panel. Every interactive element has a *visible focus ring* (never removed to "look clean"). Icon-only buttons get `aria-label`.
4. **Consistency locks.** ONE accent color for the whole view (a semantic status hue is fine, a random second accent in section 7 is not). ONE corner-radius scale, followed everywhere. ONE theme end-to-end — no section inverts.
5. **Motion must be motivated.** Before adding any animation, name what it communicates (hierarchy / feedback / state-change / sequence). "It looked cool" is not a reason. Honor `prefers-reduced-motion`. Animate `transform`/`opacity`, never `width`/`height`/`top`/`left`.
6. **Copy self-audit before "done".** Re-read every visible string: no marketing fluff, no "!" in success messages, no "Oops!" (in any language), active voice, plain functional language. Every number is real data or clearly a sample — never AI-invented precision; a rendered number is verified like any other number.

**The deeper principle**: These are the same fingerprints regardless of aesthetic — a beautiful chart with a spinner-not-skeleton loader, a proportional-figure table, an invisible focus ring, or a fake `92%` reads as "rushed" no matter how good the palette is. Weakest-link logic (Lesson 17) applied to polish, not just to visualizations.

## Note (2026-07-24): Filter dropdowns break in their OPEN state
**Source**: A portal's filter panel. The feedback was that the filter options could not be seen properly once a dropdown was open.

- **Dropdown clipping by ancestor overflow**: a custom dropdown positioned absolutely inside a
  collapsible panel gets CLIPPED if ANY ancestor has overflow:hidden (often kept for a max-height
  collapse animation). Contrast fixes alone don't solve "can't see the options" — check the whole
  ancestor chain; give the OPEN state overflow:visible and keep hidden only for the closed/animating state.
- **Verify dropdowns OPEN, as a user, in a real browser** — the open state is where filter UIs break
  (clipping, z-index, contrast); a static screenshot of the closed page proves nothing about it.
- **WCAG-adaptive pill text**: when a category pill's brand color is too light for white text, derive a
  deeper shade of the SAME hue for the pill so the text clears 4.5:1, keep the lighter hue for swatches.

## Lesson 19: A Hebrew (or any non-ASCII) dashboard must be charset-proof, not charset-dependent (2026-08-10)
**Source**: A survey dashboard. On first look, every Hebrew word on the page was garbled.

**Why this matters**: The page was correct UTF-8. It still rendered as mojibake, because the thing
serving it did not declare a charset and the browser fell back to windows-1252. A Hebrew page whose
legibility depends on a `Content-Type` header you do not control is one deployment away from being
unreadable - and the failure is total, not cosmetic: every word turns to noise.

**The deeper principle**: Do not rely on the delivery layer to declare the encoding, and do not
assume the wrapper you are published into sets it. Make the artifact itself immune. Emit the file as
**pure ASCII** - Hebrew inside a `<script>` becomes a `\uXXXX` escape (valid in both JS and JSON, and
`json.dumps(..., ensure_ascii=True)` does the whole payload for free); Hebrew anywhere else becomes
an `&#NNNN;` character reference. An ASCII-only file decodes identically under UTF-8, windows-1252
and ISO-8859-1, so it cannot be broken by a header.

**How to verify it, not hope for it**: read the built file as bytes and assert `all(b < 128)`, then
decode it under three charsets and assert the three strings are identical. Then load it in a browser
from a server that deliberately sends **no** charset - that is the condition that broke it, so it is
the condition that has to pass. Counting rendered Hebrew characters and mojibake hits in
`document.body.innerText` turns "looks fine" into a number.

## Lesson 20: Index survey options by VALUE, never by array position (2026-08-10)
**Source**: A survey dashboard. The page threw `Cannot read properties of undefined (reading 'pct')`
on first render.

**Why this matters**: A distribution built from data contains only the options someone actually
chose. If nobody picked option 3, every option after it shifts down one slot. `items[3]` then reads
the *wrong row* - and reading the wrong row silently is far worse than the crash, because the number
still looks plausible. This is the same class of error as a bare positional index in an R pipeline.

**The principle**: Look options up by their coded value (`at(dist, 5)`), and have the helper return
a zero-filled row when the value is absent, so an unchosen option renders as 0% instead of throwing
or lying. Applies to every categorical chart, stat card and narrative sentence that names a specific
response option.

## Lesson 21: Bars in a chart share ONE origin - never an auto-sized label column (2026-08-10)
**Source**: A survey dashboard. The feedback asked that bars sitting next to each other start from
the same point, and flagged it as a rule for every future dashboard.

**Why this matters**: A bar chart makes one promise - length is comparable across rows. A label
column sized `auto` or `minmax(96px,auto)` is sized by the longest label in that row's grid, so
rows with different label lengths start their bars at different x positions. The lengths are then
no longer comparable by eye, which is the entire reason the chart exists. This is Lesson 8
(length must be proportional to value) attacked from the other side: there the FILL was distorted,
here the ORIGIN is.

**The principle**: inside one chart, every bar starts at the same x and ends on the same scale.
Fix the label column and the value column to explicit widths (`grid-template-columns: var(--lbl)
1fr var(--val)`); let long labels WRAP inside their fixed column, never push the bar. Keep the
value column fixed too, or the right edge ragged-ends and the bars lose their shared endpoint.

**When labels are sentences, don't shrink the label - move it.** For item-level charts (a
questionnaire item per row) put the label on its own line above a full-width bar. Same guarantee,
achieved by construction rather than by tuning a column width.

**Verify it, don't eyeball it**: in the browser, for each chart collect
`[...chart.querySelectorAll(".track")].map(t => Math.round(t.getBoundingClientRect().right))`
(`.left` in LTR) and assert the set has exactly one value. Report it as a gate, e.g.
"N charts checked, 0 misaligned".

## Lesson 22: Every chart carries its own n, and every difference carries a test (2026-08-10)
**Source**: A survey dashboard. The request was for an n on every chart and a significance test on
every difference shown.

**Why this matters**: In a real survey, people drop out at different points, so *there is no single
N*. A dashboard that prints one N in the header and none on the charts silently implies every panel
rests on the same base - and it does not. Worse, a dashboard that shows two means side by side is
making a claim about a difference; without a test, the reader supplies the significance themselves,
usually generously.

**The principle**: an n badge on every chart, reporting the base that chart was actually computed
on. And every difference the page *displays* gets a test with an effect size and a confidence
interval, not just a p. Where the comparison is within-subject (the same respondent rated both
things - almost always true in a survey), the test is PAIRED and runs on complete pairs only, so
the test's n is usually smaller than the chart's n. Say that out loud in the UI rather than letting
the two numbers look inconsistent.

**Also**: give every displayed proportion a Wilson 95% interval and every mean a t-based interval -
a percentage with no interval invites over-reading a 3-point gap. Correct within each family of
tests (Holm for a handful of planned comparisons, Benjamini-Hochberg for a correlation matrix),
report raw and corrected p side by side, and decide the verdict on the corrected one. In a
correlation heat map, draw the cells that do NOT survive correction hollow/dashed, so a dark cell
never reads as a strong finding when it is noise.

**No hedging vocabulary**: "significant" or "not significant" plus the exact p. Never "trending
toward significance", never "marginal".

## Lesson 23: A theme switch has to move the charts, not just the background (2026-08-10)
**Source**: A survey dashboard. The request was a button that switches the dashboard to a light
theme, with colours contrasting the current ones.

**Why this matters**: The base style system builds charts in pure CSS/DOM with the colour written
*inline* on each bar, donut segment and heat-map cell - that is what makes it dependency-free. It
also means the JS holds its own copy of the palette. Flip a CSS theme and the page background
changes while every chart stays in the old colours, which looks broken in a way a screenshot of the
header will never reveal.

**The principle**: the palette lives in exactly ONE place - CSS custom properties on `:root`, with
`:root[data-theme="light"]` redefining only the tokens. The JS reads them at render time
(`getComputedStyle(document.documentElement).getPropertyValue("--accent")`) and never hard-codes a
hex. Because the charts carry colour inline, the theme handler must *re-render*, not merely restyle:
wrap section-building in a `buildAll()` and call it again on switch. Tokenise everything, including
the things that hide - header gradient, sticky-nav background, badge backgrounds and borders, table
hover, the "2px solid" header underline, and the ink colour used for text drawn ON a filled bar
(`--on-fill`, which is near-black in dark mode and white in light mode).

**The light theme is a second design, not an inversion.** The request was for contrasting colours,
and rightly so. Dark here is *pale accents on a deep ground*; the light theme should be its opposite
in kind - *saturated ink on a cool paper ground* - with every accent darkened until it clears
WCAG-AA on white (#6db8e8 sky becomes #0d6d8f teal). A naive inversion produces washed-out pastels on
white that fail contrast and read as the same design with the lamp turned up.

**Verify by switching, not by looking**: click the button in a real browser and assert that a
CHART changed - read `document.querySelector(".fill").style.background` before and after and confirm
the rgb moved. Re-run the alignment gate (Lesson 21) in BOTH themes. Persist the choice in
`localStorage` inside try/catch (private mode throws), default to the project's primary theme, and
remember that a stale stored value from your own testing will make a clean load look wrong - clear
it before judging the default.

## Lesson 24: Verify a metric's LABEL against the live instrument, never against the spec (2026-08-10)
**Source**: A survey's live monitor, which for weeks reported an inflated "completed" count.

**Why this matters**: The monitor counted "answered a demographics question" and called it
"completed". That is a correct definition *if* the demographics block is last, which is what the
codebook said. In the live survey it was not, so the metric was really "got past the screener" - and
it was the number being used to track recruitment. No data was harmed and the statistics were fine -
the damage was entirely in a label.

**The principle**: a funnel metric is a claim about WHERE in the instrument a person got to. Derive
it from the live flow definition (Qualtrics `SurveyFlow`, the block order as exported), not from a
codebook, a build plan, or the order blocks appear in the editor. Documents drift; the flow is the
instrument. And prefer the platform's own completion flag over a proxy question wherever one exists.

**Two supporting habits**: (1) when a metric is a proxy, name it after the proxy - "answered the
demographics" - and let a separate row carry "finished". Showing both costs one line and makes the
error impossible. (2) When an existing dashboard's number is disputed, reproduce ITS rule on the
frozen data rather than quoting a remembered figure; that is how the disputed count was confirmed as
the monitor's own output rather than a misremembering.

## Lesson 25: A deployed dashboard someone else is watching is not yours to silently correct (2026-08-10)
**Source**: A survey monitor. After the wrong metric in Lesson 24 was found, the fix was deployed
first and reported afterwards, on a page that had already been shared outside the team.

**Why this matters**: Correcting a wrong number felt obviously right, and technically it was. But
the page had been shared outside the team, and a page that suddenly shows different numbers to
someone outside is a *relationship* event, not a maintenance one. Who sees which number, and when, and
with what explanation, belongs to the person who owns that relationship.

**The principle**: internal artifacts - local files, private analysis pages, a dashboard only the
researcher opens - can be fixed and reported. Anything already shared outward gets the finding and
a proposed fix FIRST, and the deploy waits for a yes. The stronger the urge to "just fix it because
it is wrong", the more certain it is that someone is relying on the current version.

**When you do take one down**, take it down completely and reversibly: delete the hosting project,
disable the scheduled job that feeds it (disable, do not delete), verify the URLs actually return
an error, and confirm out loud that the source and data remain in the repo and can be redeployed in
one command. Then mark it as removed in the project record so a later session does not advertise a
dead link.

## Lesson 26: A funnel starts where the participant starts, and never merges two departures (2026-08-10)
**Source**: A survey dashboard. The feedback was to start the funnel at the platform's first count
rather than at the export, to call it a participant funnel rather than "exclusions", and to continue
past the eligibility gate showing who left where.

**Why this matters**: Three separate framing errors, all of which hide people. (1) Starting the
funnel at the response export begins the story after some people have already vanished - sessions
that opened and never closed exist in the platform's counts but not in the export. (2) Calling it
"exclusions" describes the operation performed on rows; the reader wants to know what happened to
*people*. (3) Stopping the funnel at the eligibility gate hides the fact that the questionnaire
itself keeps losing people block by block - which is exactly the information needed to read any n
on the page.

**The principle**: one continuous participant funnel, from the first click to the last answer, with
every row phrased as a state a person reached; a "% of everyone who entered" column so all rows sit
on one scale; and it continues past eligibility through each block of the instrument. Where the
drop-off concentrates is usually the single most actionable finding on the whole dashboard - often
at one long item matrix.

**And never let two different departures share a row.** A filter like `screener != ELIGIBLE` kept
everyone who never *reached* the screener, because in pandas `NaN != ELIGIBLE` is True - silently
inflating the analysis base with people who had answered nothing at all. "Answered and was
ineligible" and "never got there" are different events and get different rows. Check every filter for what it does to missing values,
and verify the survivors of a suspicious group actually answered something downstream before
counting them.

**Related payoff**: when the demographics block sits EARLY in a survey, you hold full demographics
on your dropouts - the one thing surveys normally cannot know about themselves. Spend it: compare
finishers to leavers, correct for multiplicity, and state the result plainly. A sentence of the form
"finishers and leavers did / did not differ on <variables> after correction" is a real finding about
external validity and belongs on the dashboard in two sentences.
