# Phase 1 — Business Understanding
## 04. Stakeholders

---

Each stakeholder group below maps to a dedicated Power BI page (Phase 9), built specifically around the questions that stakeholder actually asks — rather than one generic dashboard everyone is expected to adapt to their own needs.

## Executive Leadership

**What they need:** A single, trustworthy view of overall business health, and a way to sanity-check growth decisions before committing budget.
**How they use it:** Opens the **Executive** page for a top-line read on revenue, delivered orders, active customers, conversion, and repeat-purchase rate, using the metric-selector control to switch the trend chart between Revenue/Orders/Customers depending on what's being discussed that week. For anything requiring a "what if we improved X" conversation, moves to the **Decision Scenarios** page and tests a lever directly, using the Conservative/Moderate/Aggressive presets to frame a range rather than a single guess.

## Sales / Category Leads

**What they need:** Which product categories and sellers actually drive revenue, and where revenue concentration creates dependency risk.
**How they use it:** The **Sales** page's category and seller breakdowns identify health_beauty, watches_gifts, and bed_bath_table as the top three revenue-generating categories, and surface that the top 25% of sellers generate 86.78% of total seller revenue — a concentration figure directly relevant to seller-relationship and diversification strategy.

## Customer / CRM Leads

**What they need:** Which customer segments are most valuable, what the real retention curve looks like, and where a retention intervention would have the most leverage.
**How they use it:** The **Customer** page's RFM segmentation and cohort retention curve identify Potential Loyalists (21,655 customers, $207.83 average CLV) as the segment combining the most scalable value, and the retention curve makes the urgency of the Month 0→Month 1 drop-off (100% → 0.48%) immediately visible rather than buried in a table.

## Product Leads

**What they need:** Where the product funnel breaks down, and whether the recommendation engine is actually earning its place in the product before further investment is made in it.
**How they use it:** The **Product** page shows the funnel's largest drop-off (Product View → Add to Cart, 62.76%) alongside the recommendation engine's evaluation metrics and the A/B experiment's DO NOT SHIP decision side by side — so a product lead sees both "where the opportunity is" and "what's already been tried and didn't work" on one page, rather than discovering the recommendation engine's real performance separately or after further investment.

## Marketing Leads

**What they need:** Whether current channels and campaigns are meaningfully different in performance, to avoid reallocating budget based on differences that are just noise.
**How they use it:** The **Marketing** page's channel comparison makes the "no statistically meaningful difference across 5 channels" finding directly visible, with the underlying reasoning (expected variance given ~18,000 impressions per campaign) stated in plain language rather than left as a number a marketing lead would have to interpret themselves.

## Data / Analytics Function (this project's author)

**What they need:** A credible, technically sound, end-to-end demonstration of the analytics stack — from data engineering through experimentation through executive reporting — built to the standard a real retail analytics team would hold itself to, including reporting negative results honestly.
**How they use it:** The complete ten-phase build itself, documented at every stage with SQL scripts, validation checks, and phase-by-phase READMEs, is the deliverable — a portfolio artifact demonstrating not just individual technical skills, but the judgment to scope a project correctly and report what the data actually shows.
