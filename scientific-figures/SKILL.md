# Scientific Data Visualization Skill

Create effective, publication-ready scientific figures based on empirical research from "The Science of Visual Data Communication: What Works" (Franconeri et al., 2021, Psychological Science in the Public Interest).

## When to Use This Skill

Activate when:
- Creating figures for academic papers, posters, or presentations
- Reviewing visualizations before publication
- Designing data displays for scientific communication
- User asks to create charts, graphs, or scientific figures

---

## 1. Key Principles for Effective Scientific Data Visualization

### Visual Channels - Precision Hierarchy (p. 112-116)

Encode your most important data using channels with highest precision:

| Rank | Channel | Best For | Precision |
|------|---------|----------|-----------|
| 1 | **Position along common scale** | Continuous values | Highest |
| 2 | **Length** | Magnitude comparisons | High |
| 3 | **Area** | Relative sizes (use carefully) | Medium |
| 4 | **Angle/Slope** | Rates of change | Medium-Low |
| 5 | **Color intensity/saturation** | Categorical or ordinal | Low |

**Key insight**: Position is ~2x more precise than length, and length is ~3x more precise than area (p. 114).

### Visual Comparisons and Working Memory (p. 122-126)

- Humans can only hold **3-4 visual items** in working memory at once
- Comparisons across a graph happen **sequentially** (one pair at a time)
- **Closer = easier to compare**: Reduce distance between compared elements
- **Aligned = more precise**: Use common baselines where possible

### Grouping Cues for Comparison (p. 126-130)

Effectiveness ranking for grouping related data:
1. **Connecting lines** (strongest)
2. **Proximity** (close spacing)
3. **Common region** (shared background)
4. **Color** (same hue)
5. **Shape** (same symbol)

**Practical tip**: Use connecting lines for time series; use proximity and color for categorical comparisons.

### Graph Schemas - Leverage Familiarity (p. 130-133)

- Use **conventional graph types** (bar charts, line graphs, scatter plots)
- Avoid novel or "creative" formats that require learning
- **Line graphs** imply continuous change over ordered dimension
- **Bar charts** imply discrete categories
- Violating these conventions causes confusion

---

## 2. Do's and Don'ts for Scientific Figures

### DO:

| Action | Rationale | Reference |
|--------|-----------|-----------|
| Start y-axis at zero for bar charts | Bars encode magnitude via length from baseline | p. 116-118 |
| Use position for primary comparisons | Most precise visual channel | p. 112-114 |
| Keep legends close to data | Reduces memory load | p. 124-126 |
| Direct label data points when possible | Eliminates legend lookup | p. 126 |
| Use consistent scales across panels | Enables valid comparison | p. 118 |
| Show data distributions, not just means | Reveals underlying patterns | p. 141-143 |
| Use error bars or confidence intervals | Communicates uncertainty | p. 143-145 |

### DON'T:

| Avoid | Problem | Reference |
|-------|---------|-----------|
| Truncating y-axis on bar charts | Exaggerates differences by 2-3x | p. 116-118 |
| Using area/bubble size for precise values | Area perception is inaccurate | p. 114-115 |
| 3D effects on 2D data | Distorts perception, adds noise | p. 118-120 |
| Pie charts for precise comparisons | Angle perception is imprecise | p. 115-116 |
| Dual y-axes with different scales | Creates false correlations | p. 120-122 |
| Excessive animation | Overwhelms memory, loses details | p. 133-136 |
| Rainbow color scales | Not perceptually uniform | p. 136-140 |

---

## 3. Color Guidelines

### Accessibility (p. 136-140)

- **~8% of males and ~0.5% of females** have color vision deficiency
- Most common: **red-green confusion** (deuteranopia/protanopia)
- **Always test** your figures with a colorblindness simulator

### Safe Color Palettes

| Use Case | Recommended | Avoid |
|----------|-------------|-------|
| Categorical (≤7 groups) | Colorbrewer qualitative | Rainbow |
| Sequential (low→high) | Single-hue gradients (light→dark) | Red-green gradients |
| Diverging (neg↔pos) | Blue-white-red with neutral midpoint | Green-red |
| Binary contrast | Blue vs. orange | Red vs. green |

### Color Design Rules

1. **Use redundant coding**: Combine color with shape, pattern, or labels
2. **Ensure luminance contrast**: Colors should differ in brightness, not just hue
3. **Limit to 7±2 colors**: More becomes indistinguishable
4. **Test in grayscale**: Figure should be readable without color
5. **Use perceptually uniform scales**: Viridis, Cividis, or Colorbrewer palettes

### Intensity Illusions (p. 140)

- **Same color appears different** against different backgrounds
- Small colored areas look less saturated than large areas
- Adjacent colors influence perceived hue (simultaneous contrast)

**Solution**: Use direct labels and avoid relying solely on color intensity for quantitative encoding.

---

## 4. Layout Guidelines

### Spatial Organization (p. 122-130)

1. **Align compared elements** on common baseline
2. **Minimize distance** between items to compare
3. **Group related data** using proximity or enclosure
4. **Reading order**: Left-to-right, top-to-bottom in Western contexts
5. **Place legends inside plot area** when space permits

### Panel/Subplot Design

```
GOOD: Small multiples with shared axes
┌────┐ ┌────┐ ┌────┐
│ A  │ │ B  │ │ C  │  ← Same scale, easy comparison
└────┘ └────┘ └────┘

BAD: Inconsistent scales or orientations
┌────┐ ┌──────┐ ┌──┐
│ A  │ │  B   │ │C │  ← Different sizes confuse
└────┘ └──────┘ └──┘
```

### White Space and Clutter

- **Remove chart junk**: Unnecessary gridlines, borders, backgrounds
- **Data-ink ratio**: Maximize ink devoted to data vs. decoration
- **Breathing room**: Don't crowd elements; use margins

### Aspect Ratio (p. 120)

- **Line graphs**: Slopes appear steeper with taller aspect ratios
- **Banking to 45°**: Average line slope should be ~45° for optimal slope perception
- Standard ratios: 4:3 or 16:9 for presentations; ~1.5:1 for print

---

## 5. Typography Guidelines

### Text Hierarchy

| Element | Size | Weight | Case |
|---------|------|--------|------|
| Title | Largest | Bold | Title Case |
| Axis labels | Medium | Regular | Sentence case |
| Tick labels | Small | Regular | As appropriate |
| Annotations | Small | Regular/Italic | Sentence case |
| Legend | Small | Regular | Match data labels |

### Font Selection

- **Sans-serif** for screen/digital: Arial, Helvetica, Open Sans
- **Serif acceptable** for print: Times, Cambria
- **Maintain consistency** across all figures in a paper
- **Minimum 8pt** for any text (check journal guidelines)

### Label Placement

1. **Direct labeling** > Legend lookup (reduces memory load)
2. **Horizontal text** preferred (avoid vertical or angled when possible)
3. **Position labels near data** they describe
4. **Avoid overlapping** text and data points

### Annotation Best Practices

- Use **callouts** to highlight key findings
- Keep annotations **brief** (not paragraphs)
- Use **consistent terminology** with main text
- Include **statistical values** (r, p, n) when relevant

---

## 6. Common Mistakes to Avoid

### Perceptual Distortions (p. 116-122)

| Mistake | Distortion | Fix |
|---------|------------|-----|
| Y-axis truncation (bars) | 2-3x exaggeration of differences | Start at zero |
| Area scaling by radius | Perceived size grows as r², not r | Scale by area |
| 3D perspective | Obscures data, adds depth cues | Use 2D |
| Inconsistent baselines | Invalid comparisons | Align on common axis |

### Illusions in Line Graphs (p. 120-122)

- **Aspect ratio** changes perceived slope
- **Nearby lines** make parallel lines seem to converge
- **Background patterns** interfere with trend perception

### Dual-Axis Traps (p. 120-122)

- Two y-axes with different scales **create false correlations**
- Arbitrary alignment can suggest causation
- **Alternative**: Normalize data or use small multiples

### Pie Chart Problems (p. 115-116)

- Angle and area perception is imprecise
- Comparing slices across pies is nearly impossible
- **Better alternatives**: Bar charts, dot plots, tables

### Animation Pitfalls (p. 133-136)

- Working memory can't retain changing displays
- Key frames may be missed
- **Use animation only for**: revealing data progressively, engaging audiences
- **Prefer**: Static small multiples for analysis

### Uncertainty Mistakes (p. 143-145)

| Mistake | Problem | Better Alternative |
|---------|---------|-------------------|
| Error bars without definition | Ambiguous (SD? SE? CI?) | Label explicitly |
| Bar + error bar | Hides distribution | Violin plot, box plot |
| Omitting uncertainty | Overconfidence in point estimates | Always show variability |

---

## 7. Pre-Publication Checklist

### Data Integrity
- [ ] Y-axis starts at zero for bar charts (or truncation is clearly marked)
- [ ] Scales are consistent across compared panels
- [ ] Area encodings scale by area, not diameter
- [ ] No 3D effects distorting 2D data
- [ ] Error bars/uncertainty measures are defined in caption

### Accessibility
- [ ] Tested with colorblindness simulator (Coblis, Color Oracle)
- [ ] Readable in grayscale
- [ ] Redundant coding (color + shape/pattern) for key distinctions
- [ ] Sufficient contrast (WCAG AA: 4.5:1 for text)
- [ ] All text ≥8pt (journal minimum)

### Clarity
- [ ] Chart type matches data type (categorical → bar; continuous → line)
- [ ] Legend is close to data or direct labels used
- [ ] Minimal chart junk (unnecessary gridlines, borders removed)
- [ ] Title and axes clearly labeled with units
- [ ] Statistical values included where appropriate

### Comparison Support
- [ ] Items to compare are spatially close
- [ ] Grouped data uses strong grouping cues (lines, proximity)
- [ ] Small multiples preferred over animation
- [ ] Familiar graph schemas used (no novel formats requiring learning)

### Technical Requirements
- [ ] Resolution: ≥300 DPI for print
- [ ] Format: Vector (PDF, SVG) preferred; PNG for raster
- [ ] Fonts embedded or converted to outlines
- [ ] File size within journal limits
- [ ] Consistent style across all manuscript figures

### Caption Requirements
- [ ] Describes what is shown (not interpretation)
- [ ] Defines all abbreviations
- [ ] Specifies what error bars represent
- [ ] Notes sample sizes
- [ ] Includes statistical test details if relevant

---

## Quick Reference: Channel Selection Guide

```
QUESTION: What type of comparison?

├─ Precise magnitude comparison
│   └─ USE: Position on common scale (bar chart, dot plot)
│
├─ Trend over continuous variable
│   └─ USE: Position + connected lines (line graph)
│
├─ Part-to-whole relationships
│   └─ USE: Stacked bar or treemap (NOT pie chart)
│
├─ Distribution shape
│   └─ USE: Histogram, density plot, violin plot
│
├─ Correlation between variables
│   └─ USE: Scatter plot
│
├─ Categorical comparison (few groups)
│   └─ USE: Grouped bar chart or dot plot
│
└─ Uncertainty/variability
    └─ USE: Error bars (defined!), confidence bands, violin plots
```

---

## References

Franconeri, S. L., Padilla, L. M., Shah, P., Zacks, J. M., & Hullman, J. (2021). The science of visual data communication: What works. *Psychological Science in the Public Interest, 22*(3), 110-161.

### Additional Resources
- Colorbrewer: https://colorbrewer2.org/
- Coblis Colorblindness Simulator: https://www.color-blindness.com/coblis-color-blindness-simulator/
- Data-to-Viz: https://www.data-to-viz.com/

---

## Example Usage in Claude Code

When user asks to create a figure:

1. **Identify data type** (categorical, continuous, distribution)
2. **Choose appropriate chart** using Channel Selection Guide
3. **Apply color guidelines** (accessible palette, redundant coding)
4. **Check layout** (proximity, alignment, legends)
5. **Run through checklist** before finalizing
6. **Generate code** using matplotlib, seaborn, ggplot2, or user's preferred library

Example prompt response:
```
Based on scientific visualization principles (Franconeri et al., 2021):

For comparing means across 4 groups with uncertainty:
- Use: Grouped bar chart with error bars
- Y-axis: Start at zero
- Colors: Colorblind-safe palette (e.g., Colorbrewer Set2)
- Error bars: Clearly labeled as 95% CI
- Direct labels if space permits
```

## Implementation Tools

For **creating** figures (not just designing them), use the `academic-figures` skill which provides the full pipeline:
- HTML/CSS layout → Playwright screenshot → Nano Banana 2 polish
- BioRender-style aesthetic for scientific diagrams
- See: `~/.claude/skills/academic-figures/SKILL.md`

For **AI image generation**, use `nano-banana-poster` with the HTML→NB2 pipeline documented there.
