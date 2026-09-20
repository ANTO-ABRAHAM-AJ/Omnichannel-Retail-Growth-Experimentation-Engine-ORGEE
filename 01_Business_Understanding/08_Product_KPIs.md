# Phase 1 — Business Understanding
## 08. Product KPIs

---

## 1. Funnel KPIs

| KPI | Value | Interpretation |
|---|---|---|
| Total Visits (sessions) | 500,000 | The full top-of-funnel population this project's product analysis is built on |
| Product View Rate | 81.14% of visits | The large majority of sessions do engage with at least one product |
| Add-to-Cart Rate | 30.22% of visits | Where the funnel's steepest single loss occurs, relative to Product View |
| Checkout Rate | 16.35% of visits | |
| Purchase Conversion Rate | 9.50% of visits | The final efficiency figure of the entire funnel |
| **Largest single drop-off point** | **Product View → Add to Cart (62.76%)** | **The clearest, most directly actionable product opportunity identified in this project** |

## 2. Recommendation Engine KPIs

| KPI | Value | Interpretation |
|---|---|---|
| Recommendation Coverage | 99.53% of customers | The engine successfully generates a recommendation for nearly every customer — coverage is not the problem |
| Content-Based Engine Hit Rate@5 | 0.07% | Offline evaluation of how often the engine's top-5 recommendations matched what a customer actually purchased next |
| Naive Popularity Baseline Hit Rate@5 | 1.07% | A simple "recommend the current best-sellers" baseline, used specifically as the comparison point |
| **Result** | **Engine underperformed the baseline by ~15.3×** | **The current recommendation logic does not currently outperform a naive alternative, despite near-complete coverage** |

## 3. Experimentation KPIs (A/B Test)

| KPI | Value |
|---|---|
| Experiment | exp_001 — Top Sellers (control) vs. Personalized Recommendations (treatment) |
| Control Conversion Rate | 2.16% |
| Treatment Conversion Rate | 2.06% |
| Absolute Effect | -0.10 percentage points |
| 95% Confidence Interval | [-0.95pp, +0.75pp] |
| Statistical Significance | Not significant (p = 0.8126) |
| Sample Ratio Mismatch (SRM) Check | Passed — traffic split confirmed valid before analyzing the result |
| **Decision** | **DO NOT SHIP** |

## 4. Why Coverage Was High But Performance Was Poor

It's worth being specific about what the 99.53% coverage figure does and doesn't tell us: it confirms the recommendation *system* is functioning correctly end-to-end — it reliably produces a recommendation for nearly every customer, with no meaningful gap in serving. What it does not confirm is that those recommendations are any *good*. This distinction — a system working correctly vs. a system producing valuable output — is exactly why the offline Hit Rate@5 comparison against a baseline, and the follow-up controlled A/B test, were both necessary rather than treating high coverage alone as evidence of success.

## 5. What This Means for Product Strategy

The product data points clearly toward **cart conversion, not recommendation personalization, as the current highest-leverage product opportunity.** The recommendation engine has been built, evaluated offline, and tested in a live controlled experiment — and has not yet demonstrated it improves outcomes at any of those three checkpoints. Meanwhile, the Product View → Add to Cart drop-off is both the single largest friction point in the funnel and one of the most directly addressable, through improvements to product discoverability, on-page content, and cart-prompt design — none of which require the kind of further, unproven investment the recommendation engine would need before it could plausibly justify deployment. This conclusion is stated plainly here specifically because the recommendation and experimentation data support it — not despite what that data shows.
