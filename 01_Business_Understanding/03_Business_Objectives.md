# Phase 1 — Business Understanding
## 03. Business Objectives

---

Each objective below states not just *what* was built, but *why* it was necessary given the business problem in `02_Business_Problem.md`, and which phase of the project delivers it.

## 1. Establish a single source of truth for retail performance

**Why:** Without a properly modeled, reconciled data foundation, every downstream metric is only as trustworthy as the query that happened to produce it — two analysts could report two different "total revenue" figures from the same raw data. **Delivered by:** Phase 2 (hybrid data engineering) and Phase 3 (Kimball star schema warehouse), which together ensure every KPI in every later phase and every Power BI page traces back to the same reconciled fact and dimension tables.

## 2. Understand where customers drop off in the journey

**Why:** "Improve conversion" is not an actionable goal on its own — it only becomes actionable once you know *which specific stage* of the journey is losing the most customers. **Delivered by:** Phase 5, which quantified the funnel precisely enough to identify Product View → Add to Cart as the single largest drop-off point (62.76%), rather than leaving the team to guess.

## 3. Identify which customers are worth the most, and why

**Why:** Treating all customers as equally worth retaining wastes retention budget on low-value customers and under-invests in the customers who actually drive the business. **Delivered by:** Phase 6's RFM segmentation and Historical CLV analysis, which quantified a 10.07× value gap between the Champions and At-Risk segments — a number precise enough to justify differentiated retention spend.

## 4. Test whether personalization actually improves outcomes, rather than assuming it does

**Why:** Personalized recommendations are treated as a default best practice across the retail industry, which makes it easy to build one and assume it's working without ever checking. **Delivered by:** Phase 7 (building and offline-evaluating a content-based recommendation engine against a naive baseline) and Phase 8 (a formal, controlled A/B experiment with a predetermined statistical framework — SRM check, significance test, confidence interval — defined *before* the result was known, specifically to prevent the outcome from being reinterpreted after the fact).

## 5. Determine whether marketing channels differ meaningfully

**Why:** Marketing budget reallocation decisions are often made from raw channel comparisons that don't account for expected statistical noise — a channel that looks 0.5 percentage points better might simply be within the range chance alone would produce. **Delivered by:** Phase 9's Marketing dashboard, which found all 5 tested channels statistically indistinguishable, meaning no channel currently has a defensible claim to more budget.

## 6. Put the findings in front of decision-makers, not just analysts

**Why:** Analysis that lives only in SQL scripts and notebooks doesn't get used by the people who make budget and roadmap decisions. **Delivered by:** Phase 9's five Power BI dashboards (Executive, Sales, Customer, Product, Marketing), built with synced filters and drill-through so a non-technical stakeholder can explore the data themselves rather than requesting a new report for every question.

## 7. Let decision-makers test hypothetical changes before committing to them

**Why:** Knowing the current state of the business is necessary but not sufficient — leadership also needs to reason about *what would happen if* a specific lever (conversion, retention, order value) improved, before deciding where to invest. **Delivered by:** Phase 10's interactive What-If scenario page, with adjustable parameters, preset scenarios, and a clear, honest labeling of every projection as illustrative rather than a forecast.

## 8. Report what the data shows, including when it's a negative result

**Why:** A project's negative findings are often the most valuable ones, because they prevent wasted future investment — but only if they're reported with the same confidence as positive findings, rather than hidden or reframed. **Delivered by:** the explicit DO NOT SHIP decision in Phase 8, and the "no meaningful channel difference" finding in Phase 9's Marketing dashboard, both stated as clearly and prominently as any positive result in this project.
