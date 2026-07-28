# Dashboard Design Lessons

Principles learned from Elad's corrections and feedback on dashboards.
Read this file BEFORE building any dashboard. These override the base style guide when in conflict.

## How to Read This File
- Each lesson is a **design principle**, not a technical spec
- Lessons are ordered newest-first
- If a principle contradicts the base style guide, the lesson wins

---

## Lesson 1: Side-by-side is the killer feature for group comparisons (2026-03-10)
**Source**: Cross-Cultural Portal Analysis tab

When a dashboard compares two groups (countries, conditions, subsamples), the most powerful view is running the *same analysis* side by side — not switching between tabs or dropdowns. Users instantly spot cross-group differences when identical visualizations are placed next to each other. Make "Both" the default when two groups exist.

## Lesson 2: Mode-based UI — shared globals, mode-specific selectors (2026-03-10)
**Source**: Analysis tab (4 modes: Correlation, Regression, Mediation, Moderation)

When a tool has multiple analysis modes, share the global controls (group filter, sample filter) across all modes but show/hide mode-specific variable selectors. This keeps the sidebar from overwhelming users while preserving full control. One "Run" button for everything — the mode determines what happens.

## Lesson 3: Variable chips grouped by construct, not alphabetically (2026-03-10)
**Source**: Analysis tab variable selection

Researchers think in constructs (Demographics, MHAI Experience, DASS), not alphabetical lists. Group selectable variables by their conceptual domain with a color-coded left border per category. This matches how researchers design analyses — "I want the distress variables and the satisfaction variables."

## Lesson 4: Canvas for continuous plots, DOM for structured layouts (2026-03-10)
**Source**: Analysis tab visualizations

Scatter plots and regression/interaction lines need pixel-level control — use Canvas. Heat maps, forest plots, and pathway diagrams need text layout, click handlers, and flexible sizing — use DOM elements with CSS. Don't force everything into one rendering approach.

## Lesson 5: Visualization first, numbers second (2026-03-10)
**Source**: Analysis tab result rendering order

Show the chart/diagram first (pattern recognition is instant), then summary stats (R², F, p), then the full coefficient table for those who want exact numbers. This mirrors how researchers actually read results — they look at the figure, check if it's significant, then dive into specifics.

## Lesson 6: Client-side stats are viable for research dashboards (2026-03-10)
**Source**: Analysis tab JS math library

For datasets under ~5000 rows, running OLS regression, logistic regression, Sobel mediation, and moderation analysis entirely in the browser is fast and eliminates server round-trips. Zero-dependency statistical computation gives instant feedback and simplifies deployment. No R/Python backend needed for interactive exploration.

## Lesson 8: Visual length must be strictly proportional to the data value (2026-03-13)
**Source**: Cross-Cultural Portal bar chart bug

A comparison bar's visual length is the primary information channel — anything that distorts the length-to-value mapping destroys the chart's usefulness. The user WILL notice when two bars look the same length but represent different values.

**Principle**: Nothing should influence bar width except the data value and a shared reference maximum. No additive constants, no CSS minimum widths, no per-row normalization. Every bar in a chart must share a single global maximum so they are visually comparable.

**Common traps**:
1. Adding a constant offset to prevent zero-width bars — instead, use a tiny minimum (0.5%) that doesn't distort perception.
2. CSS `min-width:fit-content` on bar elements — the text label expands the bar, overriding data-driven width. Use `overflow:visible` so labels can extend beyond the bar.
3. Per-row normalization in categorical charts (each row's max becomes 100%) — makes all "largest" bars identical regardless of actual value. Always compute a single global max across all categories.

## Lesson 7: Two-tier data architecture for research portals (2026-03-10)
**Source**: Portal aggregate vs. individual data endpoints

Aggregate statistics (means, counts, distributions) can live in the main dashboard with lighter security. Individual-level data for analysis requires a separate authenticated endpoint. This protects participant privacy while still enabling rich interactive exploration. Never embed individual data in the HTML source.

## Lesson 9: The dashboard IS the empty state (2026-04-15)
**Source**: AI PSYCH Explorer. "עשית עבודה לא טובה" — the first version showed blank pages.

**Why this matters**: A blank page with "Select a variable" signals to the researcher that the tool is passive — it waits for them to know what to ask. But the whole point of an explorer is DISCOVERY. Most researchers open the dashboard to understand the data, not to verify a specific hypothesis. If they already knew what to look at, they'd write R code. The blank page defeats the purpose.

**The deeper principle**: The "empty state" is actually the MOST IMPORTANT state — it's what 100% of users see first. It must answer the question: "What's interesting in this data?" It should tell a story before anyone clicks anything. Show the sample (N, demographics), the key patterns (distributions, percentages), the strongest effects. Make it clickable — each mini-chart is a doorway into deeper exploration.

**Implementation**: Auto-compute overview cards (N, key %, means), a 2x3 mini-chart gallery of the most theoretically important variables, and highlighted findings. Every mini-chart is a click target that takes you to the full variable view. The overview IS the home page.

## Lesson 10: Think in research questions, not statistical procedures (2026-04-15)
**Source**: AI PSYCH Explorer Advanced Analysis tab.

**Why this matters**: Researchers think "What predicts AI-MH use?" — not "I need logistic regression with DV=AI_MH and IVs=DASS_Total, ANTRO_Mean, ECR_AI_Anxiety." The gap between the research question and the statistical setup is exactly where confusion, errors, and abandonments happen. A dropdown that says "Select DV" requires the researcher to do a mental translation that the tool should do for them.

**The deeper principle**: The best analysis tools work at the level of the user's actual goal, not at the level of the statistical engine. Each research question implies a specific statistical approach, a set of variables, and appropriate filters. By pre-packaging these as one-click presets, you eliminate the translation step AND you encode domain knowledge (which variables matter for which question) into the tool itself.

**Implementation**: Show preset cards with: the question in plain language, a brief description of what analysis runs, and an accent color. Clicking auto-configures mode + wave + variables + filter and runs immediately. Always include "Or build your own" for experts who want custom control. The presets should come from the actual published papers/pre-registrations.

**Addendum (2026-04-16)**: When a preset auto-runs, VERIFY every selected variable exists in the chosen wave + filter BEFORE invoking the analysis. If any variable is missing (not available in that wave, has zero non-null values after filtering, or conflicts with the filter — e.g., a W1-only variable in a W2 preset), render an inline warning card that explains exactly which variable is missing and suggests the closest alternative. Never silently null-fail — users assume the preset worked and misinterpret absent output as "no effect." A loud-but-graceful fallback beats a silent bug every time.

## Lesson 11: Every number must speak in words (2026-04-15)
**Source**: AI PSYCH Explorer analysis outputs. Elad: "שכל דבר שרואים שיבינו מה הוא בשקיפות"

**Why this matters**: A coefficient table showing β=0.016, p<.001 is meaningless to anyone who doesn't already know what the analysis does. Even experienced researchers can misread which variable is significant. The table is for verification; the narrative is for understanding. They serve different cognitive functions.

**The deeper principle**: Statistical transparency means three layers: (1) the visualization (pattern recognition — instant), (2) the narrative interpretation (meaning — "higher distress predicts AI-MH use"), and (3) the coefficient table (precision — for those who need exact numbers). Each layer serves a different audience and a different cognitive need. The common mistake is providing only layer 3 and assuming layers 1-2 are "obvious."

**Implementation**: Template-based narrative generation that reads result objects and writes directional, significance-aware sentences. For significance: green "significant predictor" tags. For non-significance: gray "not significant" with no hedging. Optional: AI interpretation button (Gemini) with a clear disclaimer for a richer reading. The narrative appears BETWEEN the chart and the coefficient table.

## Lesson 12: Always show where data comes from (2026-04-15)
**Source**: AI PSYCH Explorer. "אני לא מבין מתי זה W1 מתי W2"

**Why this matters**: In longitudinal data, the same variable name (DASS_Total) exists in multiple waves. A regression using W1 DASS as predictor and W2 DASS as outcome is fundamentally different from a W1-only cross-sectional analysis. If the user doesn't immediately see which wave each variable represents, they cannot interpret the results correctly. This isn't a labeling convenience — it's a validity issue.

**The deeper principle**: Context must be embedded in the interface, not in the user's memory. Every variable chip, dropdown option, and results table cell that could be ambiguous about its source must carry its provenance. Use [W1]/[W2] badges, colored borders, and context banners. In cross-wave mode, make it visually obvious that predictors come from one wave and outcomes from another.

## Lesson 13: Navigation must be reversible (2026-04-15)
**Source**: AI PSYCH Explorer. "צריך שיהיה אפשר להחזיר לעמוד הבית"

**The principle**: Exploration requires safe backtracking. If drilling into a variable or running an analysis is a one-way trip, users explore less. A visible "← Back to Overview" button reduces the cognitive cost of clicking something — you know you can always return. This is especially important when the overview contains computed summaries that are expensive to mentally reconstruct.

## Lesson 14: Research tools need a softer palette (2026-04-15)
**Source**: AI PSYCH Explorer. "שהצבעים והצורות יהיו רכות יותר"

**The principle**: The original dashboard-style design system was built for monitoring dashboards — alert-driven, attention-grabbing. Research exploration is different: researchers stare at the tool for hours, comparing subtle patterns. Saturated colors (#1d9bf0 blue, #f87171 red) create visual fatigue and make small differences harder to spot. Softer, more muted tones (#6db8e8, #e09090) with larger border-radius (12px) create a calmer visual environment where the data — not the chrome — demands attention.

## Lesson 15: A chart for every variable, no exceptions (2026-04-15)
**Source**: AI PSYCH Explorer. "אני רוצה שיהיה גרפים ככל הניתן"

**Why this matters**: Tables are for lookup; charts are for understanding. When a researcher selects "DASS_Total", they need to SEE the distribution — is it normal? skewed? bimodal? A mean and SD don't tell you that. When they select "Tool" (multi-choice), they need to see which tools dominate at a glance. The Shiny app Elad built earlier had charts for everything — that's the benchmark.

**The auto-detection logic**: Continuous → histogram (8-10 bins). Binary → donut chart (CSS conic-gradient, 120px). Categorical → horizontal bars sorted by frequency. Ordinal → bars with value labels. Multi-choice set → all items as bars sorted descending. Grouped → side-by-side bars with inline test results. Every chart type must be implemented in pure CSS/DOM — no external libraries.

## Lesson 16: Explanation boxes should be collapsible, not stacked (2026-04-16)
**Source**: AI PSYCH Explorer. The initial version stacked three permanent banners before every results view: method explanation, "what you're testing," and "how to read."

**Why this matters**: Permanent banners before results become "textbook before data." First-time users need the explanation, but the SAME user returning to the dashboard for the 50th time sees the same walls of text between them and the data they came to examine. Persistent help is paradoxically less helpful — it creates visual noise that experienced users must mentally skip every single time.

**The deeper principle**: Explanation and context are NOT the same thing. Context that reflects the current run ("you are testing X against Y with N=413") stays permanent because it changes with each analysis and prevents misinterpretation. Generic method explanation and how-to-read instructions are *learnable* — they become redundant once learned. Collapse the learnable; keep only the contextual.

**Implementation**: Merge "method explanation" and "how to read" into a SINGLE collapsible panel labeled "About this analysis" with a clear expand/collapse arrow. Default expanded on first visit, remember user preference per analysis mode via localStorage (`help_expanded_<mode>`). Keep "what you are testing" as a permanent, non-collapsible banner that mirrors the CURRENT run's variables. That one card answers "what is this showing me right now" — different cognitive function from the collapsible help.

## Lesson 17: A stats dashboard is only as good as its weakest analysis visualization (2026-04-16)
**Source**: AI PSYCH Explorer. Initial version had: good mediation path diagram, good correlation heatmap, solid regression forest plot, solid moderation slope bars — BUT logistic regression showed no plot at all, moderation had no interaction lines, and the mediation diagram only showed 2 of the 4 paths.

**Why this matters**: Users judge a research tool by its weakest mode, not its strongest. A dashboard that produces beautiful correlation matrices but falls back to text-only tables for logistic regression or moderation signals "this was rushed." Every analysis type must deliver the same quality of visual storytelling. A missing interaction plot makes moderation look like a procedural detour instead of a meaningful finding.

**The deeper principle**: Each statistical method has a canonical "money shot" plot — the one figure that makes the result interpretable at a glance. Regression has the forest plot of coefficients (or OR on log scale). Logistic regression has the predicted probability curve showing how P(outcome=1) varies across the key predictor, with a rug plot of raw observations. Moderation has the interaction plot showing 2–3 predicted lines at different moderator levels. Mediation has the full 4-path diagram (a, b, c, c′) with coefficients on each arrow. Skipping the money shot makes the analysis feel incomplete — a table with numbers is not a substitute.

**Implementation audit**: Before releasing, go through every analysis mode and list the canonical plot. If any mode lacks one, build it. For multi-path models (mediation), every path must be visually drawn — don't leave c and c′ implied in a table while showing a and b on the diagram.
