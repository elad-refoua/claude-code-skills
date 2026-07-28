---
name: dashboard-style
description: "Elad's dashboard design system. Apply when building dashboards, data monitors, comparison tools, or data explorers. Triggers: 'dashboard', 'monitor', 'data explorer', '/playground for dashboard'."
---

# Elad's Dashboard Design System

Apply these rules when building any dashboard, data monitor, comparison tool, or data explorer — whether via `/playground`, standalone HTML, or any visualization tool.

## Learning Protocol

**Before building**: Read `~/.claude/skills/dashboard-style/lessons.md` — it contains design principles learned from Elad's feedback. Lessons override the base style guide when in conflict.

**After Elad corrects a dashboard**: Extract the PRINCIPLE behind the correction and append it to `lessons.md`.

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
.bar-track { height: 18px; background: #0f1419; border-radius: 4px; overflow: hidden }
.bar-fill { height: 100%; border-radius: 4px; display: flex; align-items: center;
            padding: 0 6px; font-size: 10px; font-weight: 600; color: #fff;
            transition: width .4s ease; min-width: fit-content }
```
Label embedded inside fill. Always gradient fill, never flat.

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
1. No external dependencies — everything inline
2. No box-shadow anywhere (depth from bg color alone)
3. Bar fills are always gradients
4. Badges use dark-bg + bright-text (same hue)
5. 3-level background depth system
6. Numbers big and bold, labels small and muted
7. Auth screen always present (even if password is simple)
8. Transitions on all interactive elements (.15s)
9. System font stack, no custom fonts
10. Hebrew-capable when needed (RTL-aware, `dir` attribute)
