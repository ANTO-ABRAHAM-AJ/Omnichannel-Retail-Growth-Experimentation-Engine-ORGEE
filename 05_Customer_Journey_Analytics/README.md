# ORGEE — Phase 5: Customer Journey Analytics

**Core business question:** How do customers move through the digital shopping journey, and where are the biggest drop-offs preventing conversion?

**Data source:** The completed Phase 3 warehouse only.

**Status:** Completed and validated against the live ORGEE warehouse.

---

## Structure

| Script | Business Question | Key Techniques |
|---|---|---|
| `01_journey_mapping.sql` | What's the actual stage-by-stage sequence, and how many sessions reach each stage? | CTE, CASE, aggregation |
| `02_session_analysis.sql` | How do sessions behave — volume, engagement, converting vs not? | CTE, `PERCENTILE_CONT`, subquery |
| `03_event_behavioral_analysis.sql` | Which behaviors distinguish successful from unsuccessful journeys? | CTE, CASE, subquery |
| `04_funnel_analysis.sql` **(signature)** | Visit → Product View → Add to Cart → Checkout → Purchase — stage and overall conversion | CTE, `LAG`, `FIRST_VALUE` |
| `05_funnel_conversion_by_dimension.sql` | Does the funnel convert differently by device/platform/category? | CTE, `RANK`, aggregation |
| `06_dropoff_analysis.sql` **(signature)** | Where, precisely, is the single biggest drop-off? | `LAG`, `RANK` |
| `07_device_segment_comparison.sql` | Session-type and identified-vs-anonymous comparisons | CTE, CASE |
| `08_cohort_analysis.sql` | Month-of-first-purchase cohorts, tracked over time | CTE, `DATEDIFF`, `DATEFROMPARTS` |
| `09_retention_curves.sql` | The actual shape of retention, blended across cohorts | CTE, `LAG`, window functions |
| `10_phase5_validation.sql` | Grain, referential integrity, funnel logic, cohort logic, null handling | — |

---

## Two Deliberate Data-Source Decisions

### 1. Funnel and behavioral analysis

The funnel (scripts `01`, `03`, `04`, `05`, `06`, `07`) is built entirely from `Fact_Events` / `Fact_Sessions`.

These are the Python-generated synthetic behavioral tables. They were never cross-referenced against `Fact_Order_Items` (the real Olist order data) during generation — a session's `purchase_interaction` event has no guaranteed matching row in the real orders table.

Treating them as reconciled would be a false data-integrity assumption, so the funnel stays entirely self-contained within the behavioral dataset.

### 2. Cohort and retention analysis

Cohort analysis and retention curves (scripts `08`, `09`) are built entirely from `Fact_Order_Items`.

Only ~18% of sessions ever resolve to a known customer (the anonymous-until-login identity model from Phase 2/3) — building cohorts from identified sessions would produce thin, noisy groups with almost no members past month 0.

`Fact_Order_Items` has clean order dates spanning ~2 years with every row resolved to a customer, making it the right foundation.

The analysis also carries forward the Phase 4 grouping fix: `customer_unique_id`, not `customer_id`.

### Known context

Phase 4 already established that only 3.00% of customers repeat-purchase at all. Expect a steep cliff after month 0 in the retention curve — that's a real, expected pattern given that context, not a query defect.

---

## Grain Discipline

Every funnel count is **distinct `session_id`**, never raw event rows.

A session with five `product_view` events counts once, not five times.

This was explicitly verified in `10_phase5_validation.sql`.

---

## Scope Boundaries

The following were deliberately excluded from Phase 5 because they belong to later phases:

- RFM
- CLV
- Customer value modeling
- Recommendation engines
- Machine learning
- A/B testing
- Statistical experimentation
- Power BI
- What-If analysis

---

## How to Run

1. Run scripts `01` through `09` in any order.
   - There are no dependencies between them.
   - Each script is self-contained.
   - Scripts `08` and `09` independently re-derive the cohort base.

2. Run `10_phase5_validation.sql` last.

3. As with Phase 4, the `BUSINESS INTERPRETATION` and `BUSINESS IMPLICATION` blocks were deliberately left blank until real numbers existed.

4. All final findings documented below are based on actual execution against the live ORGEE warehouse.

---

# Phase 5 Status

## Completed

- All 10 SQL scripts written and executed against the live ORGEE warehouse.
- Both source-table decisions — funnel/behavior on `Fact_Events`, cohorts on `Fact_Order_Items` — held up correctly under real execution.
- Signature insight computed directly from `06_dropoff_analysis.sql`'s ranked output.
- Individual analytical outputs were captured and documented.
- Consolidated validation was executed through `10_phase5_validation.sql`.

---

## Validated

`10_phase5_validation.sql` returned:

**12 PASS, 1 INFO, 0 FAIL**

The validation confirmed:

- Funnel stage counts are monotonically non-increasing.
- Funnel grain uses distinct sessions rather than raw event rows.
- `Fact_Sessions.session_id` is unique.
- Every `Fact_Events.session_id` exists in `Fact_Sessions`.
- No orphan events exist.
- All relevant event dates resolve to `Dim_Date`.
- All order purchase dates resolve to `Dim_Date`.
- Funnel stage chronology is valid.
- Overall funnel conversion percentage is within the valid 0–100% range.
- Cohort assignment is one cohort per delivered-order customer with no fan-out.
- No retention percentage exceeds 100%.
- `Fact_Events.event_type` contains no NULL values.
- Session identification rate is 18.06%, matching the Phase 3 baseline.
- The single INFO result documents the expected NULL `customer_sk` values for anonymous sessions; this is part of the anonymous-until-login model and is not a defect.

---

## Post-Execution Fix

One real bug was identified during execution and corrected.

The category-level cart-to-purchase query in:

`05_funnel_conversion_by_dimension.sql`

was initially scoped incorrectly and produced mathematically impossible rates above 100%.

The query was corrected and reissued.

The corrected analysis explicitly treats the category-level rate as a **session-level association** because the synthetic `purchase_interaction` event is not tied to a specific `product_sk`.

---

# Key Findings

## 1. Signature Insight — Largest Funnel Drop-Off

**The largest customer drop-off occurs between Product View → Add to Cart.**

- Product View sessions: **405,699**
- Add to Cart sessions: **151,078**
- Sessions lost: **254,621**
- Drop-off: **62.76%**

This is the largest stage-to-stage drop-off in the funnel.

For comparison:

| Funnel Transition | Drop-Off |
|---|---:|
| Product View → Add to Cart | **62.76%** |
| Add to Cart → Checkout | **45.90%** |
| Checkout → Purchase | **41.99%** |
| Visit → Product View | **18.86%** |

The primary customer-journey friction point is therefore the transition from **product interest to cart engagement**.

---

## 2. Overall Funnel Conversion

The overall **Visit → Purchase conversion rate is 9.48%**.

| Stage | Sessions | Overall Conversion |
|---|---:|---:|
| Visit | 500,000 | 100.00% |
| Product View | 405,699 | 81.14% |
| Add to Cart | 151,078 | 30.22% |
| Checkout | 81,736 | 16.35% |
| Purchase | 47,418 | **9.48%** |

The funnel shows substantial loss at multiple stages, with the largest absolute and relative stage-to-stage friction occurring at **Product View → Add to Cart**.

---

## 3. Converting Sessions Show Higher Engagement

Converting sessions demonstrate substantially higher engagement than non-converting sessions.

- Average duration:
  - Converting: **2,607 seconds**
  - Non-converting: **1,249 seconds**

- Average events:
  - Converting: **12.1**
  - Non-converting: **5.4**

Converting sessions are therefore more than twice as long and contain more than twice the event activity of non-converting sessions.

---

## 4. Search Behavior Is Associated With Higher Conversion

Sessions that included a search converted at:

**11.21%**

Sessions that did not search converted at:

**5.60%**

Therefore, sessions containing search activity show roughly **2× the conversion rate** of sessions without search activity.

This is an observed association in the behavioral dataset, not a causal claim.

---

## 5. Cart Abandonment

Among sessions that added something to the cart:

- Sessions that added to cart: **151,078**
- Abandoned before checkout: **69,342**
- Cart abandonment rate: **45.90%**

This identifies a second major friction point after the Product View → Add to Cart transition.

---

## 6. Session Length Shows the Largest Segment Difference

Conversion varies dramatically by session type:

| Session Type | Sessions | Converting Sessions | Conversion Rate |
|---|---:|---:|---:|
| Long | 100,294 | 28,101 | **28.02%** |
| Medium | 224,875 | 18,593 | **8.27%** |
| Short | 174,831 | 724 | **0.41%** |

Long sessions therefore show approximately a **68× spread** in conversion compared with short sessions.

By comparison, device and platform conversion rates remain relatively close, with less than a 1 percentage-point difference across the major device/platform groups.

**Interpretation:** session depth and engagement show a much stronger observed relationship with conversion than device or platform.

---

## 7. Identified vs Anonymous Sessions

The identity-segment analysis shows:

| Identity Segment | Sessions | Conversion Rate |
|---|---:|---:|
| Anonymous | 409,679 | **9.30%** |
| Identified | 90,321 | **10.32%** |

Identified sessions convert modestly better than anonymous sessions.

The difference is relatively small compared with the much larger conversion gap associated with session length.

---

## 8. Retention Curve

> **Correction, applied and verified:** this section originally used an
> unweighted `AVG()` of each cohort's retention percentage, which let
> tiny early cohorts (e.g. a single-customer December 2016 cohort that
> happened to score 100% at month 1) count exactly as much as cohorts
> of 1,600+ customers — inflating Month 1 in particular, and the likely
> source of the non-monotonic bumps noted earlier in this phase.
> `09_retention_curves.sql` was corrected to a size-weighted average
> (`SUM(active_customers) / SUM(cohort_size)` per month), matching the
> "Weighted Retention Rate %" measure in the Phase 9 Power BI model.
> The corrected script was re-run against the live warehouse; the
> table below is the real output. Month 1 now reads **0.48%**, matching
> the Power BI dashboard exactly.

The cohort analysis shows a very steep decline after the first purchase month.

Blended retention:

| Month Offset | Average Retention |
|---:|---:|
| 0 | **100.00%** |
| 1 | **0.48%** |
| 2 | **0.34%** |
| 3 | **0.26%** |
| 4 | **0.26%** |
| 5 | **0.23%** |
| 6 | **0.23%** |
| 7 | **0.21%** |
| 8 | **0.20%** |
| 9 | **0.17%** |
| 10 | **0.25%** |
| 11 | **0.22%** |
| 12 | **0.17%** |

Retention drops sharply after month 0: blended retention falls to **0.48% by month 1**, then drops further and remains around **0.17–0.34% through month 12**.

This reconciles with Phase 4's **3.00% overall repeat-purchase rate** more precisely than the original figures did: summing the corrected Month 1–12 percentages above (0.48 + 0.34 + 0.26 + 0.26 + 0.23 + 0.23 + 0.21 + 0.20 + 0.17 + 0.25 + 0.22 + 0.17) comes to **≈3.02%** — matching Phase 4's 3.00% repeat-purchase rate almost exactly, since each repeat customer's second (or later) order falls into exactly one month bucket. The original unweighted figures summed to **≈8.09%**, nearly 3× too high — a check worth remembering for future phases: a blended monthly-retention curve should roughly sum to the known overall repeat rate, and that arithmetic is a fast way to catch this class of error before it reaches a dashboard.

---

# Business Interpretation

The Phase 5 analysis indicates that the primary customer-journey problem is **not simply getting visitors onto the site**.

The largest friction occurs after customers have already demonstrated product interest:

**Product View → Add to Cart**

At this stage, **62.76% of product-viewing sessions do not progress to cart activity**.

A second major friction point occurs after cart engagement, where **45.90% of cart-adding sessions fail to reach checkout**.

The behavioral analysis also shows that deeper engagement is strongly associated with conversion. Converting sessions are longer and contain substantially more events, while search-enabled sessions have approximately twice the conversion rate of sessions without search.

Device and platform differences are comparatively small.

---

# Business Implications

The findings suggest that the highest-leverage customer-journey optimization opportunity is the **product discovery / product-detail → add-to-cart experience**, rather than a device-specific optimization alone.

Potential areas for subsequent business investigation include:

- Product-page clarity and information quality
- Add-to-cart visibility and usability
- Product value communication
- Search and product-discovery experience
- Cart-to-checkout friction
- Re-engagement during the early post-purchase period

These are **business implications derived from the observed patterns**, not causal conclusions. Controlled experimentation belongs to the later Experimentation phase.

---

# Phase 5 Validation Result

**PASS — 12/12 substantive checks passed, 1 informational note, 0 failures.**

Phase 5 is therefore complete and provides the analytical foundation for the next stage of ORGEE.

---

## Final Phase 5 Takeaway

> **The largest customer-journey friction occurs between Product View and Add to Cart, where 62.76% of sessions fail to progress. The funnel converts 9.48% of visits into purchases, while deeper session engagement is strongly associated with conversion and retention drops sharply after the first purchase month.**

**Phase 5 — Customer Journey Analytics: COMPLETE.**