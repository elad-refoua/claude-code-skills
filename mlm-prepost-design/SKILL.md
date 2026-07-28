---
name: mlm-prepost-design
description: Field-grounded statistical defaults for multilevel pre-post designs in behavioral/clinical science. Use when planning, pre-registering, analyzing, or writing up within-subjects pre-post studies analyzed with MLM (mixed-effects models). Covers random effects structure, effect size reporting, multiple comparisons, power, missing data, multi-site handling, and verified key references. All references verified by DOI lookup.
---

# MLM Pre-Post Design — Field-Standard Defaults

Use these defaults for within-subjects pre-post studies analyzed with multilevel models unless project context overrides them. Grounded in a verified literature review (2026-04-16) across behavioral/clinical science, therapist training, and multi-site trial methodology.

## When to Use This Skill

Triggers: "multilevel model", "MLM pre-post", "within-subjects design", "random effects", "mixed-effects", "lme4", "pre-registration analysis plan", "effect size MLM", "power for within-subjects", "multi-site trial", "site covariate", "pre-post intervention", "training analysis", "simulation training analysis".

## Primary Model Specification

```r
library(lme4)
library(lmerTest)   # for Satterthwaite / Kenward-Roger df
library(sjPlot)
library(simr)
library(mice)
library(performance)

# Multi-unit (e.g., multi-module, multi-scale) pre-post design
# Start with the maximal random-effects structure per Barr et al. 2013
m_primary <- lmer(
  outcome ~ condition * time + site + (1 + time | participant) + (1 | unit),
  data = long_data, REML = TRUE
)

# Heterogeneity check across multiple units within condition
m_heterogeneity <- lmer(
  outcome ~ unit * time + site + (1 + time | participant),
  data = long_data %>% filter(condition == target), REML = TRUE
)

# Exploratory cross-site interaction — report at α = .05 two-sided
m_3way <- lmer(
  outcome ~ condition * time * site + (1 + time | participant) + (1 | unit),
  data = long_data, REML = TRUE
)

# Diagnostics
performance::check_model(m_primary)
performance::r2(m_primary)  # Nakagawa-Schielzeth R²
```

## Field-Standard Decisions

### Random Effects Structure

| Design | Default | Notes |
|---|---|---|
| Single outcome, 2 timepoints per person | `(1 + time \| participant)` where feasible; fall back to `(1 \| participant)` if singular. | Barr et al. 2013 "keep it maximal". |
| Multiple units × 2 timepoints | `(1 + time \| participant) + (1 \| unit)` | k ≥ 5 units preferred; 6 is borderline. |
| 3+ timepoints | `(1 + time \| participant)` with random slope | Standard repeated-measures. |
| Clustered by site | Site as FIXED effect if k = 2-4; RANDOM if k ≥ 5. | Small k → random variance unstable. |

**Convergence fallback sequence** (pre-register this chain before data analysis):
1. Maximal model.
2. Drop random slope on time.
3. Treat unit as fixed dummies instead of random intercept.
4. Drop unit entirely; rely on `(1 | participant)`.

### Effect Size Reporting

Always report:
1. **Unstandardised β + 95% CI** for the fixed effect of interest (primary).
2. **Cohen's d_RS = β ÷ σ_residual** (Westfall et al. 2014). Always specify the denominator.
3. **Variance Partition Coefficient (VPC)** for each random component.
4. **Nakagawa-Schielzeth marginal and conditional R²** via `performance::r2`.

Do NOT report a generic "Cohen's d from the mixed model" without specifying the denominator.

### Multiple Comparisons Hierarchy

Pre-register a clear hierarchy:
1. **Primary:** uncorrected. One-tailed α = .05 only when theory predicts direction; two-tailed otherwise.
2. **Secondary confirmatory family:** Holm-Bonferroni, family-wise α = .05. State the family members explicitly.
3. **Exploratory:** uncorrected, labelled. Do not re-promote to confirmatory post-hoc.

### Multi-Site Handling

Default pipeline:
1. Pool sites with `site` as a fixed-effect covariate (treatment coded, with documented reference level).
2. Pre-register the `condition × time × site` three-way interaction as a confirmatory check at α = .05 two-sided. **Do not use α = .10** — that's an escape hatch.
3. Always report site-stratified and pooled estimates side by side, regardless of interaction significance.

### Power

- `simr::powerSim(nsim = 1000, seed = [fixed])`.
- Document assumed variance components (ICC participant, ICC unit, residual SD) and their source.
- Run a sensitivity grid across plausible ICC values; report MDES range.
- Acknowledge when ICC values are informed priors rather than empirical estimates.

### Reliability Thresholds (for self-report scales)

- **α ≥ .80:** good
- **.70 ≤ α < .80:** acceptable for new scales
- **.60 ≤ α < .70:** flagged; interpret with caution
- **α < .60:** flagged; discuss as below threshold
- **Item-total r < .30:** item flagged for review
- Report α (or McDonald's ω) per scale per timepoint. Do not drop items post-hoc unless pre-registered.

### Missing Data Policy

- **Primary analysis:** MLM with ML estimation (handles missing at random under MAR).
- **Item-level threshold:** > 20% missing within a scale → drop that scale-observation. One item missing (20%) → average remaining items.
- **Participant-level threshold:** > 10% participant-total missing → MICE multiple imputation sensitivity (`mice`, 20 imputations, Rubin's rules pooling).
- **Document MAR assumption** and acknowledge MNAR is not fully handled; consider pattern-mixture models for dropout-prone designs.
- **Complete-case** analysis reported in an appendix.

### Outlier Handling

- No > 3-SD removal on in-range responses.
- **Response-level exclusions:** speeders (< 30% of median completion time, median frozen before exclusions), straight-liners (within-scale SD = 0 across all items — mechanical definition), attention-check failures.
- **Participant-level influence:** flag Cook's D > 4/n; report sensitivity analysis excluding flagged participants.
- Pre-register ALL exclusion criteria with mechanical thresholds; no "upon inspection" discretion.

### Transformation

- Default: analyse Likert means as approximately Gaussian. Robust to moderate non-normality (Norman 2010).
- If residuals show material non-normality, retain linear model and report as limitation. Do not transform post-hoc.
- For skewed or zero-inflated outcomes, pre-register the GLMM family (e.g., beta-regression for proportions, ordinal for ordered-category data).

## Software Specification

Always specify in pre-reg and paper:
- R version (e.g., R ≥ 4.3)
- `lme4` version (≥ 1.1.35)
- `lmerTest` for p-values (Satterthwaite default; Kenward-Roger via `contestMD`)
- `emmeans` for estimated marginal means and contrasts
- `performance` for diagnostics and R²
- `simr` for power simulations
- `mice` for multiple imputation
- Report `sessionInfo()` in every analysis script

## Verified Key References (DOIs confirmed 2026-04-16)

1. **Bakker, M., Veldkamp, C. L. S., van Assen, M. A. L. M., et al. (2020).** Ensuring the quality and specificity of preregistrations. *PLOS Biology, 18*(12), e3000937. DOI: [10.1371/journal.pbio.3000937](https://doi.org/10.1371/journal.pbio.3000937)
   - Pre-reg specificity checklist; common failures.

2. **Barr, D. J., Levy, R., Scheepers, C., & Tily, H. J. (2013).** Random effects structure for confirmatory hypothesis testing: Keep it maximal. *Journal of Memory and Language, 68*(3), 255-278. DOI: [10.1016/j.jml.2012.11.001](https://doi.org/10.1016/j.jml.2012.11.001)
   - Random-effects specification.

3. **Brysbaert, M., & Stevens, M. (2018).** Power analysis and effect size in mixed effects models: A tutorial. *Journal of Cognition, 1*(1), 9. DOI: [10.5334/joc.10](https://doi.org/10.5334/joc.10)
   - MLM effect size, VPC, power for repeated measures.

4. **Feaster, D. J., Mikulich-Gilbertson, S., & Brincks, A. M. (2011).** Modeling site effects in the design and analysis of multi-site trials. *American Journal of Drug and Alcohol Abuse, 37*(5), 383-391. DOI: [10.3109/00952990.2011.600399](https://doi.org/10.3109/00952990.2011.600399)
   - Multi-site fixed vs. random; interactions.

5. **Green, P., & MacLeod, C. J. (2016).** SIMR: An R package for power analysis of generalized linear mixed models by simulation. *Methods in Ecology and Evolution, 7*(4), 493-498. DOI: [10.1111/2041-210X.12504](https://doi.org/10.1111/2041-210X.12504)
   - Simulation-based power.

6. **Luke, S. G. (2017).** Evaluating significance in linear mixed-effects models in R. *Behavior Research Methods, 49*(4), 1494-1502. DOI: [10.3758/s13428-016-0809-y](https://doi.org/10.3758/s13428-016-0809-y)
   - Satterthwaite vs. Kenward-Roger.

7. **Nakagawa, S., & Schielzeth, H. (2013).** A general and simple method for obtaining R² from generalized linear mixed-effects models. *Methods in Ecology and Evolution, 4*(2), 133-142. DOI: [10.1111/j.2041-210x.2012.00261.x](https://doi.org/10.1111/j.2041-210x.2012.00261.x)
   - Marginal and conditional R².

8. **Westfall, J., Kenny, D. A., & Judd, C. M. (2014).** Statistical power and optimal design in experiments in which samples of participants respond to samples of stimuli. *Journal of Experimental Psychology: General, 143*(5), 2020-2045. DOI: [10.1037/xge0000014](https://doi.org/10.1037/xge0000014)
   - Standardised effects in crossed random-effects designs.

9. **Hsieh, H.-F., & Shannon, S. E. (2005).** Three approaches to qualitative content analysis. *Qualitative Health Research, 15*(9), 1277-1288. DOI: [10.1177/1049732305276687](https://doi.org/10.1177/1049732305276687)
   - Conventional content analysis for mixed-methods supplementary qualitative work.

## Common Mistakes to Avoid

| Mistake | Fix |
|---|---|
| Reporting "Cohen's d = 0.45" without specifying the denominator | Always clarify: d_RS = β ÷ σ_residual (or σ_baseline, σ_total — name the denominator). |
| Random slopes with only 2 timepoints without sufficient N | Start maximal; fall back if singular. Pre-register the fallback chain. |
| Bonferroni across primary + secondary + exploratory together | Apply correction within tiers only. |
| Treating k = 2 site data as random effects | k ≤ 4 → fixed. Random needs k ≥ 5 for stable variance. |
| Dropping items post-hoc for "low α" without pre-registration | Pre-register the threshold and the rule. |
| Listwise deletion as primary | ML in MLM (MAR) is primary; complete-case as sensitivity. |
| Claiming "one-tailed" without directional theory | One-tailed only when theory predicts direction. Two-tailed by default. |
| Pairing reflexive TA with Cohen's κ | Incompatible frameworks. Pick Hsieh & Shannon content analysis for κ-compatible coding. |
| WAI-TECH / post-only measure as "mediator" of pre-post change | Temporally impossible. Reframe as a correlate. |
| Using α = .10 threshold for site × treatment interaction | Escape hatch. Use α = .05; always report stratified and pooled. |
| Adding unverified citations to justify choices | Every DOI must resolve. Verify before writing. |

## Effect Size Benchmarks

- **Therapist skill self-efficacy (training):**
  - Short interventions (1-2 sessions): d ≈ 0.35-0.50
  - Multi-week programs: d ≈ 0.50-0.80
  - Simulation-based: d ≈ 0.40-0.79
- **Psychotherapy outcomes (general):** d ≈ 0.50-0.80 (Wampold benchmark)
- **Brief educational interventions:** d ≈ 0.20-0.40

Use as priors for power analyses and for framing expected effect sizes.

## Anti-Fabrication Rule

Every citation in any file that references this skill must have a verified, resolving DOI. Earlier versions of this file contained fabricated references (Brown/Lilford/STEPS Trials Group; Flaat et al.; Portalupi et al.; and a Shen et al. paper misattributed to anthropomorphism) that were caught only by a dedicated verification audit. **Never add a citation without DOI verification. If you cannot verify, flag the reference as unverified and ask the user before proceeding.**
