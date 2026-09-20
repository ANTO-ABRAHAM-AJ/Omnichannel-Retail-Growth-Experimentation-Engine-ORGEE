# ORGEE — Phase 7: Recommendation Intelligence

**Core business question:** What product should we recommend to this customer?

**Locked approach:** One content-based recommendation engine, built entirely in T-SQL against the Phase 3 warehouse — no Python, no collaborative filtering, no deep learning (per the locked scope).

**Status:** Complete. 7 scripts, **16 PASS, 2 INFO, 0 FAIL**, one honest (negative) signature insight.

## Structure

| Script | Purpose |
|---|---|
| `01_recommendation_data_preparation.sql` | Builds `reco.interactions` — the customer-product interaction dataset |
| `02_product_feature_engineering.sql` | Builds `reco.product_features` — 5 features per product |
| `03_customer_preference_profiles.sql` | Builds `reco.customer_preferences` — weighted-sum behavioral profiles |
| `04_content_based_recommendation_engine.sql` ⭐ | Builds `reco.recommendations` — the actual Top-5 engine, cosine similarity |
| `05_recommendation_evaluation.sql` ⭐ | Leakage-safe historical holdout evaluation — the critical script |
| `06_recommendation_business_impact.sql` | Honest business framing given what was actually measured |
| `07_phase7_validation.sql` | Final validation — 16 PASS, 2 INFO, 0 FAIL |

## Design decisions locked in before writing any SQL

- **Primary signal = purchases** (`Fact_Order_Items`, always identified). **Secondary signal = views/cart-adds** (`Fact_Events`, only the ~18% of sessions that resolve to a known customer — the anonymous-until-login design from Phase 2/3).

- **Interaction weighting**: view = 1.0, cart = 2.0, purchase = 3.0 — stated explicitly, not hidden. Repeated engagement with the same product sums (a view + cart + purchase = 6.0), treated as stronger signal than a single interaction.

- **5 product features**: category (one-hot), average price, weight, volume (`length × height × width` combined into one feature), photo count. No brand/subcategory — genuinely don't exist in this data.

- **Long/tall feature tables** (`product_sk` / `customer_unique_id`, `feature_name`, `feature_value`), not wide columns — the standard pattern that makes cosine similarity computable in plain T-SQL.

- **Candidate generation**: each customer's single top-preference category, capped to that category's 100 most-popular products — a deliberate, documented tradeoff for computational tractability (see bugs below).

## Real bugs found and fixed along the way (not glossed over)

1. **Phase 3 warehouse defect, only surfaced now**: `Dim_Product.product_photos_qty` was `NULL` for all 32,951 products — traced back to the original Phase 3 load using `TRY_CONVERT(INT, ...)` directly on decimal-formatted source text (`"1.0"`, not `"1"`), which silently fails for INT (but not DECIMAL) conversions. Also affected `product_name_length` and `product_description_length`. Fixed at the source with a targeted patch, converting to `DECIMAL` first, then rounding to `INT`.

2. **Tempdb exhaustion**: the first version of Script 04's candidate generation joined every customer directly to every product in their top category, producing 159,461,416 rows before the actual similarity computation even began. Fixed with a two-stage shortlist (rank products by popularity within category, cap at 100, then join customers to the shortlist).

3. **Reproducibility bug**: `ROW_NUMBER()` / `RANK()` calls with no tiebreaker meant re-running the identical script could produce slightly different results (Hit Rate@5 shifted from 0.08% to 0.07% between two "identical" runs) whenever a customer had an exact tie in preference value or similarity score. Fixed with explicit tiebreakers, and confirmed stable across two subsequent runs.

4. **Baseline population mismatch (caught in review)**: the naive popularity baseline was being evaluated on all 25,015 customers with a holdout purchase, while the engine was evaluated only on the 14,490 who also had training-period activity — not apples-to-apples, since many of the extra ~10,525 customers could never have received an engine recommendation in the first place (no training data to build a profile from). Fixed by computing one shared eligible population and using it for both metrics.

5. **Product feature leakage (caught in review)**: `price_norm` (unlike category/weight/volume/photos, which are static catalog attributes) is derived from transactional data and was computed across the entire observation period in Script 02 — meaning the training-only evaluation was unknowingly using future pricing information. Fixed by rebuilding a training-period-only `price_norm` for the evaluation pipeline specifically, replacing every use of `reco.product_features` inside Script 05 (including inside the customer preference profiles themselves, not just the final similarity step).

## The honest signature insight

> **The content-based recommendation engine achieved a 0.07% Hit Rate@5 across 14,490 evaluable customers (using a leakage-safe historical holdout, with a training-period-only product feature set and a baseline evaluated on the identical population), underperforming a naive popularity baseline (1.07%) by roughly 15.3×.** A wider candidate pool was tested and made results worse, indicating that simply increasing candidate coverage was not the solution to the observed performance limitation. The likely explanation: content-based similarity lacks the collaborative signal ("customers who buy X also buy Y") needed to predict genuinely new purchases — a real, structural limitation of the locked one-content-based-engine scope, not a bug.

This is not the success story the original plan hoped for, and it's reported as such — consistent with the plan's own rule: *"we will not predetermine X or Y. The data decides the result."*

**What the engine does demonstrably do well**: produce coherent, interpretable, same-category recommendations (every inspected example matched the customer's actual top preference, similarity scores in a tight 0.68–1.00 range). Its defensible use case, given the evidence, is same-session "similar item" cross-sell — not long-horizon future-purchase prediction.

## Relationship to Phase 8

Phase 8's existing experimentation data (`Fact_Recommendation_Events`, `Dim_Experiment`) was built independently in Phase 2 as a self-contained A/B-testing demonstration dataset — it does not literally test this specific engine's specific picks, and rewiring that pipeline now would be new architecture. Phase 8 remains valuable on its own terms for demonstrating rigorous experimentation methodology (SRM checks, significance testing).

## How to run

Run `01` through `07` in strict numeric order — unlike Phases 4-6, this is a genuine pipeline where each script builds permanent tables (`reco.*` schema) that the next script depends on, not independent self-contained analyses.

---

## PHASE 7 STATUS

**Completed:** All 7 scripts built, executed against the live warehouse, and debugged through 5 real issues (a Phase 3 warehouse defect, a computational scaling failure, a reproducibility bug, a baseline population mismatch, and a product-feature leakage issue) — all found, diagnosed, and fixed properly rather than worked around.

**Validated:** `07_phase7_validation.sql` — **16 PASS, 2 INFO, 0 FAIL**. Data quality, recommendation logic (Top-N respected, no duplicates, no already-purchased leakage, valid similarity bounds), coverage (99.53%), and evaluation validity (leakage-safe cutoff confirmed, not just assumed) all check out cleanly.

**Key findings:**

- 99.53% of profiled customers (94,691 of 95,137) receive Top-5 recommendations.
- Recommendations are internally coherent (same-category matches, sensible similarity scores).
- **The engine does not beat a naive popularity baseline at predicting future purchases** — the honest signature insight above.
- 14,490 customers were evaluable — a real, usable sample, not a "too little data" result.

**Validation result:** PASS (**16 PASS, 2 INFO, 0 FAIL**).

**Anything unresolved:** None from a correctness standpoint. The engine's predictive limitation is a genuine finding about this approach's fit for this business, not an unresolved technical issue — the evaluation itself is sound and reproducible.
