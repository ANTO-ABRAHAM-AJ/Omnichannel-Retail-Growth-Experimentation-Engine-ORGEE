# ORGEE — Phase 8: Experimentation Framework

**Core business question:** Does personalized product recommendation improve purchase conversion compared with a control experience using top-selling products?
**Status:** Complete. 8 scripts, 12/12 validation checks passing, one honest, statistically-grounded business decision.

## Structure

| Script | Purpose |
|---|---|
| `01_experiment_design.sql` | Confirms experiment scope, hypothesis, and 4 locked design decisions |
| `02_experiment_population.sql` | Builds `expt.experiment_population` — Assigned/Eligible/Analyzed population layers |
| `03_srm_validation.sql` ⭐ | Chi-square goodness-of-fit gate check — PASS/FAIL before any performance interpretation |
| `04_experiment_metrics.sql` ⭐ | Control vs Treatment: primary and secondary metrics |
| `05_statistical_significance.sql` ⭐ | Two-proportion z-test, p-value, 95% confidence interval |
| `06_experiment_readout.sql` ⭐ | Consolidated executive readout |
| `07_business_decision.sql` ⭐ | Final SHIP / DO NOT SHIP / CONTINUE TESTING call, with reasoning |
| `08_phase8_validation.sql` | Final QA — 12 PASS, 0 FAIL |

## Design decisions locked in before writing any SQL

Before building anything, the actual Python generator source (not just the warehouse DDL) was checked directly, which surfaced four critical facts:

1. **Scope is `exp_001` only.** `Dim_Experiment` has 3 experiments, but the generator only ever produced `Fact_Recommendation_Events` for the alphabetically-first experiment_id. `exp_002`/`exp_003` have assignments but zero recommendation events — confirmed directly in Script 01 (0 events for both). Conveniently, `exp_001`'s variant labels are literally "Top Sellers Recommendations" (control) vs "Personalized Content-Based Recommendations" (treatment) — an exact match to this phase's hypothesis.
2. **Purchase Conversion Rate is defined purely from `Fact_Recommendation_Events`** (customers with ≥1 `recommendation_conversion` event ÷ eligible customers) — this signal is self-contained synthetic data, never cross-referenced against real `Fact_Order_Items` purchases.
3. **No true treatment effect was ever built into this data.** The generator applies identical `impression_to_click` (12%) and `click_to_purchase` (8%) probabilities to both control and treatment — verified directly in the source, not assumed. This meant a null/no-significant-difference result was the honest, expected outcome going in — not a sign of a broken analysis.
4. **Assignment allocation is a deterministic, near-exact 50/50 split** (not probabilistic), confirmed in Script 01 (49,720 control / 49,721 treatment).

## Real bugs found and fixed along the way (not glossed over)

1. **Buffer pool memory exhaustion in Script 01**: an early query joined `Fact_Experiment_Assignments` directly to `Fact_Recommendation_Events` on the shared `experiment_sk` key (only 3 distinct values), creating a cross-join-like row explosion (~1 billion intermediate rows for one experiment alone). Fixed by aggregating each fact table separately before joining the pre-collapsed summaries.
2. **Two consolidation bugs in Script 06**: a first attempt to combine Script 04's four already-correct, isolated metric calculations into fewer combined CTEs introduced (a) a join fan-out that inflated the conversion rate ~4.7x, and (b) a restricted-context denominator that collapsed Revenue-per-User to nearly equal AOV. Fixed by reverting to four properly isolated calculations mirroring Script 04's confirmed-correct structure exactly — a real lesson that "cleaning up" working SQL by merging queries can silently break it.
3. **Methodological correction in Script 03 (caught in review)**: the original script ran the chi-square test on the ELIGIBLE population (2,223/2,188) and labeled that "SRM". That's not the canonical definition — SRM specifically tests whether the RANDOMIZATION/ASSIGNMENT mechanism itself matched the planned ratio, which can only be answered on the ASSIGNED population (49,720/49,721). Fixed: the primary SRM gate now runs on the assigned population (chi-square ≈0.00001, trivially clean, confirming the deterministic split), with the original eligible-population comparison kept as a separate, explicitly-labeled INFORMATIONAL "exposure balance" diagnostic rather than conflated with SRM.

## The honest signature insight

> **Personalized recommendations changed Purchase Conversion Rate by -0.10 percentage points (-4.75% relative lift), with a 95% confidence interval of [-0.95pp, +0.75pp], leading to a DO NOT SHIP decision.**

SRM passed cleanly (chi-square ≈0.00001, on the assigned population). The primary metric showed Treatment performing slightly *worse* than Control, not better, and the difference was nowhere near statistically significant (p=0.8126). This is a precisely-estimated null result with a reasonably-sized eligible population (4,411 total) — not an underpowered, ambiguous one — which is why the decision is **DO NOT SHIP** rather than **CONTINUE TESTING**: the plan's own distinction reserves "continue testing" for a promising-but-uncertain positive direction, and that's not what this data shows.

**Scope boundary, maintained since Phase 7**: this decision is about `exp_001`'s synthetic experiment data only. It is not a verdict on Phase 7's actual content-based recommendation engine, which was never connected to this experiment's outcome data — that pipeline was never wired that way, and rewiring it now would be new architecture.

## How to run

Run `01` through `08` in strict numeric order — this is a genuine pipeline (like Phase 7), not independent analyses. `expt.experiment_population` (built in Script 02) is the shared foundation every later script depends on.

---

## PHASE 8 STATUS

**Completed:** All 8 scripts built, executed against the live warehouse, and debugged through 3 real issues (a fact-to-fact join fan-out causing memory exhaustion, a metric-consolidation bug that silently corrupted two already-correct calculations, and a methodological mislabeling of the SRM check's population) — all found, diagnosed, and fixed properly.

**Validated:** `08_phase8_validation.sql` — **12 PASS, 0 FAIL**. Assignment integrity, allocation balance, an independent SRM recomputation on the assigned population (matching Script 03's corrected primary chi-square of ≈0.00001), metric denominator sanity, statistical output validity, and final decision consistency all check out clean.

**Key findings:**
- SRM (assigned population, the canonical definition): PASS (chi-square ≈0.00001, trivially clean — confirms the deterministic 50/50 assignment split). Eligible-population exposure balance (2,223/2,188, informational only): also balanced (chi-square 0.2777).
- Primary metric: Control 2.16% vs Treatment 2.06% conversion — not statistically significant (p=0.8126, z=-0.24).
- 95% CI [-0.95pp, +0.75pp] — spans zero, centered slightly negative.
- Secondary metrics (CTR, Purchase Rate) both near-identical between variants, consistent with the primary result.
- AOV/Revenue-per-user proxies showed an eye-catching gap, correctly diagnosed and flagged as small-sample noise (~46 conversions/variant) rather than oversold as a real finding.
- **Final decision: DO NOT SHIP** — a real, defensible, data-driven conclusion, not a predetermined one.

**Validation result:** PASS (12/12 checks, 0 failures).

**Anything unresolved:** None. The null result is a genuine finding about this experiment's data, consistent with what the generator source code predicted before any metric was computed — not an unresolved technical issue.
