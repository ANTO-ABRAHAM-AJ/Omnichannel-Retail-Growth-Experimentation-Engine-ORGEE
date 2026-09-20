# Phase 10 — Decision Scenarios & What-If Analysis
## 03. Scenario Validation

**Location:** Power BI Desktop, ORGEE.pbix, "Decision Scenarios" page
**Method:** Manual verification against live model output (screenshots captured during build), cross-checked by hand against each DAX formula

---

## 1. Objective

Confirm that the What-If parameter model behaves correctly before treating it as a finished deliverable:

- The model reproduces the real baseline exactly when all parameters are at 0%
- Each parameter genuinely changes its corresponding scenario measure
- No negative values are ever produced
- Percentages and currency values calculate correctly, by hand-checked arithmetic
- Baseline figures match the verified Phase 6/9 actuals
- The scenario measures never modify source data — they are read-only calculations layered on top of the existing model

---

## 2. Check: 0% assumption = baseline

**Method:** All three sliders (Conversion Improvement %, Repeat Purchase Improvement %, AOV Improvement %) set to 0.00.

| Measure | Result at 0% | Verified against |
|---|---|---|
| Scenario Revenue | 13.22M | Matches `Total Revenue` (Phase 9 dashboard) exactly |
| Current Revenue | 13.22M | Same measure, same value |
| Incremental Revenue | 0.00 | Correct — no uplift with no assumption |
| Current Customers | 93K | Matches Phase 6/9 (93,358) |
| Scenario Customers | 93.36K | Matches — 93,358 rounds to 93.36K at 2-decimal display; formula adds 0 additional customers at 0% retention lift |
| Current Revenue per Customer | 141.62 | Matches Phase 9 dashboard exactly |
| Scenario Revenue per Customer | 141.62 | Identical to Current at baseline — correct |
| Retention Revenue Contribution | 0.00 | Correct — isolated lever also at 0 |

**Result: PASS.** Every scenario measure reproduces its real baseline exactly when parameters are at 0%. No drift, no offset error.

---

## 3. Check: parameter changes actually affect scenario measures

**Method:** Moved each slider independently and in combination; captured before/after screenshots at each step.

| Test | Slider(s) moved | Before | After | Changed correctly? |
|---|---|---|---|---|
| Conversion only | Conversion → 0.19 | 13.22M | 15.73M | Yes |
| All three together | All → ~0.19 each | 13.22M | 18.32M | Yes — combined effect exceeds single-lever effect, as expected |
| Retention isolation | Repeat Purchase → 0.19 (others 0) | Incremental Revenue 0.00 | Incremental Revenue 72.93K | Yes — small but real and independently verified against its own isolated measure |
| Preset buttons | Conservative / Moderate / Aggressive / Reset | — | Each correctly snapped all 3 sliders and every downstream card/chart to its saved state | Yes |

**Result: PASS.** Every parameter demonstrably drives its intended measures. The retention lever's effect is real but proportionally small — documented as an intentional finding in Section 6, not a defect.

---

## 4. Check: no negative values

**Method:** Tested at 0% (minimum) and 20% (maximum, the parameter's own upper bound) on all three sliders, individually and combined. Also reviewed each measure's formula for any subtraction that could theoretically go negative.

- All three Improvement % parameters are bounded 0–0.20 by the parameter definition itself — a negative "improvement" is not selectable in the UI at all.
- `Scenario Revenue`, `Scenario Customers`, `Scenario AOV`, `Scenario Conversion Rate`, `Scenario Repeat Purchase Rate` are all baseline **plus** a non-negative contribution — structurally incapable of going below baseline.
- `Incremental Revenue` = Scenario Revenue − Total Revenue is the only subtraction in the model, and since Scenario Revenue ≥ Total Revenue by construction, this can never be negative. Confirmed 0.00 (not negative) at the 0% baseline, the one case where it comes closest to zero.

**Result: PASS.** No negative value is reachable within the model's own parameter bounds.

---

## 5. Check: percentages and currency values calculate correctly

**Method:** Hand-recomputed the model's output at a captured slider position (all three ≈ 0.19) against the underlying formulas.

```
Baseline Revenue:              13.22M
Conversion contribution:       13.22M × 0.19  ≈ 2.51M
AOV contribution:              13.22M × 0.19  ≈ 2.51M
Retention contribution:        2,801 × 0.19 × 137.04 ≈ 0.07M
Expected Scenario Revenue:     13.22M + 2.51M + 2.51M + 0.07M ≈ 18.31M
Actual Scenario Revenue shown: 18.32M
```

Difference (≈0.01M) is fully explained by the slider not landing on exactly 0.19000 — confirmed by re-deriving from the isolated Retention Revenue Contribution card, which independently read 72.93K at the same slider position, matching `2,801 × 0.19 × 137.04 ≈ 72.9K` precisely.

**Result: PASS.** No calculation error found; the only variance is slider-precision rounding, not a formula defect.

---

## 6. Check: baseline revenue = Phase 6/9 actual revenue

| Figure | Phase 10 baseline (0%) | Phase 6/9 verified value |
|---|---|---|
| Revenue | 13.22M | 13.22M |
| Active Customers | 93K (93,358) | 93,358 |
| AOV | 141.62 (Revenue per Customer) | 141.62 |
| Repeat customers (used in Retention formula) | 2,801 | 2,801 — Phase 4/5/6 verified repeat-purchase count |

**Result: PASS.** Every baseline figure traces directly back to the same verified numbers used throughout Phases 6–9, not a separately-sourced or re-derived figure.

---

## 7. Check: scenario calculations don't modify source data

**Method:** Design review of the model, not a runtime test (this is a structural guarantee, not something that can drift at runtime).

- All 8 scenario measures are DAX `measures` — computed at query time from existing tables (`Total Revenue`, `AOV`, `Purchase Conversion Rate %`, `Repeat Purchase Rate %`, `Active Customers`) and the 3 What-If parameter tables. Measures read data; they cannot write to it.
- No `New table`, `New column`, or data-load step was used anywhere in the Phase 10 build — confirmed by the build process itself (every step was Modeling → New measure or New parameter, never New table/New column).
- Moving a slider or clicking a preset button only changes filter context for the report visuals on this one page; it cannot alter `Fact_Order_Items`, `Dim_Customer`, or any other underlying table.

**Result: PASS.** The scenario layer is structurally read-only by construction.

---

## 8. Known, intentional finding (not a defect)

The Repeat Purchase Improvement lever produces a much smaller revenue effect than the Conversion or AOV levers at the same slider position (e.g. ~73K vs. ~2.5M each at 0.19). This is correctly explained by the real, verified repeat-customer base being small (2,801) relative to the total customer base (93,358) — it is not visible on the main "Scenario Revenue Impact" chart at its $14–20M scale, which is why a dedicated **Retention Revenue Contribution** card was added specifically to make this lever's effect demonstrable on its own.

---

## 9. Summary

| # | Check | Result |
|---|---|---|
| 1 | 0% assumption = baseline | PASS |
| 2 | Parameter changes affect scenario measures | PASS |
| 3 | No negative values | PASS |
| 4 | Percentages/currency calculate correctly | PASS |
| 5 | Baseline revenue = Phase 6/9 actual | PASS |
| 6 | Scenario calculations don't modify source data | PASS |

**6 / 6 checks passed.** No defects found; one intentional, documented finding regarding the relative size of the retention lever's effect.
