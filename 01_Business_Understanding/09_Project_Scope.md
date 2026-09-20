# Phase 1 — Business Understanding
## 09. Project Scope

---

## 1. In Scope — The 10-Phase Architecture

```
PHASE 1   Business Understanding
PHASE 2   Hybrid Data Engineering            (real Olist data + synthetic behavioral layer)
PHASE 3   Enterprise SQL Data Warehouse       (Kimball star schema)
PHASE 4   Advanced SQL Analytics
PHASE 5   Customer Journey Analytics          (funnel, sessions, cohort retention)
PHASE 6   Customer & Product Analytics        (RFM, CLV, North Star metric)
PHASE 7   Recommendation Intelligence         (content-based engine)
PHASE 8   Experimentation Framework           (A/B test, SRM, significance testing)
PHASE 9   Power BI Executive Decision Platform (5 dashboard pages)
PHASE 10  Decision Scenarios & What-If Analysis
```

## 2. In Scope — Deliverables, by Phase

- **Phase 2:** A hybrid data foundation combining real Olist marketplace data (orders, products, customers, sellers, payments, reviews) with a purpose-built Python-generated behavioral layer (sessions, events, marketing campaigns, inventory, identity resolution, and experiment assignment).
- **Phase 3:** A Kimball-modeled enterprise SQL data warehouse, with documented star schema, ER diagram, data dictionary, and referential integrity constraints.
- **Phase 4:** Advanced SQL analytics covering revenue trends, product/seller/category performance, inventory health, and customer purchasing patterns.
- **Phase 5:** Full customer journey analytics — funnel analysis, session-type breakdowns, drop-off analysis, and cohort retention curves.
- **Phase 6:** RFM segmentation, Historical CLV, the North Star metric, and a product-side KPI tree with a feature-prioritization framework.
- **Phase 7:** One content-based recommendation engine, evaluated offline against a naive popularity baseline.
- **Phase 8:** One formal, controlled A/B experiment, with a predetermined SRM check, significance test, confidence interval, and a stated business decision (SHIP / DO NOT SHIP / CONTINUE TESTING).
- **Phase 9:** Five interactive Power BI dashboards (Executive, Sales, Customer, Product, Marketing), with synced category and date filters and cross-page drill-through.
- **Phase 10:** One interactive What-If scenario page, with three adjustable parameters, preset scenario buttons, and a stated executive decision framework distinguishing illustrative projection from forecast.
- **Throughout:** full documentation at every phase — SQL scripts, results write-ups, validation checklists, and phase-level READMEs, so every figure in every later phase is traceable back to the script that produced it.

## 3. Explicitly Out of Scope (Version 1)

The following were deliberately excluded, not overlooked — each would have added technological breadth without adding proportional business insight to the specific questions this project set out to answer:

- Kafka, Spark Streaming, or any real-time streaming infrastructure — this project's questions don't require real-time data, only accurate historical analysis.
- FastAPI, Docker, Kubernetes, or CI/CD pipelines — there is no production service being deployed; the deliverable is analysis and a reporting layer, not a running application.
- Cloud deployment — kept local/on-premise in scope to keep the project's cost and complexity proportional to a portfolio project.
- Multiple competing ML models or a model-comparison exercise — one recommendation approach, properly evaluated and tested, demonstrates the relevant skill more credibly than several shallow ones.
- SHAP or other model-explainability tooling — not necessary for a content-based recommender, where the "why" behind a recommendation is already transparent by construction.
- Deep learning of any kind — the scale and nature of this data does not justify it, and a simpler model that is properly tested is more defensible than a complex one that isn't.
- Time-series forecasting — this project answers "what is happening" and "what would happen under a given assumption" (Phase 10's What-If tool), not "what will happen," which is a different and separately scoped kind of claim.
- An AI decision assistant — decision support here is delivered through interpretable dashboards and a transparent scenario calculator, not a black-box recommendation layer on top of the analysis itself.

## 4. Why This Boundary Was Held

These exclusions remain candidate ideas for a potential Version 2, not gaps in what's delivered here. This project's guiding principle, stated and held to throughout all ten phases, is **business insight over technology quantity** — and that principle was tested most directly not in what was built, but in what wasn't: when the recommendation engine underperformed its baseline (Phase 7) and the marketing channels showed no significant difference (Phase 9), the response was to report both findings clearly, rather than to add scope in search of a more flattering result.
