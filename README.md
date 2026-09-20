<div align="center">

# 🛒 ORGEE — Omnichannel Retail & Growth Experimentation Engine
**End-to-End Retail Analytics, Customer Growth, Product Analytics & Experimentation Platform**

![Domain](https://img.shields.io/badge/Domain-Retail%20%26%20E--Commerce-blue?style=for-the-badge)
![Tech Stack](https://img.shields.io/badge/Tech-SQL%20%7C%20Python%20%7C%20Power%20BI-orange?style=for-the-badge)
![Focus](https://img.shields.io/badge/Focus-Growth%20%26%20Experimentation-success?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen?style=for-the-badge)

</div>

<br>

# 📌 Project Overview

**ORGEE (Omnichannel Retail & Growth Experimentation Engine)** is an end-to-end retail analytics platform designed to demonstrate how modern retail organizations transform customer and product data into decisions that improve conversion, retention, and revenue.

The platform combines:

- **Hybrid Data Engineering** (real transaction data + purpose-built synthetic behavioral data)
- **Enterprise SQL Data Warehousing**
- **Advanced SQL Analytics**
- **Customer Journey & Product Analytics**
- **Recommendation Intelligence**
- **Controlled Experimentation (A/B Testing)**
- **Business Intelligence (Power BI)**
- **Interactive Decision Scenarios & What-If Analysis**

The project uses the **public Olist Brazilian e-commerce marketplace dataset** — real orders, products, customers, sellers, payments, and reviews — combined with a Python-generated synthetic behavioral layer (sessions, browsing events, marketing campaigns, and a controlled experiment), to reconstruct the omnichannel signals a real retailer has that a public order-level dataset alone doesn't provide.

The overall objective is to demonstrate how technical analytics connects directly to **business decision-making, customer growth strategy, product prioritization, and executive reporting.**

---

# ⚠️ Business Problem

Modern retailers operate across mobile apps, websites, and third-party marketplaces, generating data at every step of the customer journey — browsing, cart activity, purchases, reviews, and marketing exposure. As retail organizations scale, they face challenges such as:

- Fragmented data across disconnected systems
- Uncertainty about where customers abandon their journey
- Difficulty identifying which customers are actually worth retaining
- Assumptions about personalization and marketing effectiveness that are rarely tested
- Difficulty prioritizing which growth lever to invest in first

Traditional dashboards can show *what* happened but rarely provide a complete framework for deciding *what to do next*.

This project addresses that gap through an integrated enterprise analytics workflow:

> **Understanding the business ➔ Building the data foundation ➔ Analyzing behavior ➔ Testing growth hypotheses ➔ Communicating insights ➔ Modeling decisions**

---

# 🎯 Project Objectives

The primary objectives of the platform are to:

- Build an enterprise analytical foundation for omnichannel retail data.
- Map and quantify the full customer journey, from first visit to repeat purchase.
- Segment customers by value using RFM and Customer Lifetime Value.
- Build and rigorously evaluate a product recommendation engine.
- Test whether personalization actually improves outcomes using a controlled A/B experiment.
- Determine whether marketing channels perform meaningfully differently.
- Build interactive Power BI dashboards with reusable DAX measures.
- Provide an interactive What-If tool letting management test hypothetical business levers before committing to them.
- Report findings honestly — including when a hypothesis doesn't hold up.

---

# 🌟 North Star Metric — Monthly Delivered Revenue per Active Customer

The project uses **Monthly Delivered Revenue per Active Customer** as its strategic North Star Metric — established in Phase 6.

It ties revenue growth directly to customer value rather than treating them as separate stories, and is the metric every Phase 10 What-If scenario is ultimately measured against.

### Supporting Metrics

- Total Revenue
- Delivered Orders
- Active Customers
- Average Order Value (AOV)
- Purchase Conversion Rate
- Repeat Purchase Rate
- Customer Segment Value (RFM / CLV)
- Recommendation Engine Hit Rate
- Campaign CTR & Conversion Rate

---

# 🔄 End-to-End Project Architecture

```text
                  BUSINESS UNDERSTANDING
                            │
                            ▼
                HYBRID DATA ENGINEERING
        (real Olist data + Python-generated behavioral layer)
                            │
                            ▼
              ENTERPRISE SQL DATA WAREHOUSE
                  (Kimball Star Schema)
                            │
                            ▼
                 ADVANCED SQL ANALYTICS
                            │
                            ▼
              CUSTOMER JOURNEY ANALYTICS
              (funnel, cohorts, retention)
                            │
                            ▼
           CUSTOMER & PRODUCT ANALYTICS
          (RFM, CLV, North Star Metric)
                            │
                            ▼
              RECOMMENDATION INTELLIGENCE
                            │
                            ▼
                    EXPERIMENTATION
                (A/B Testing, SRM, Significance)
                            │
                            ▼
               POWER BI EXECUTIVE PLATFORM
                    (5 Dashboards)
                            │
                            ▼
         DECISION SCENARIOS & WHAT-IF ANALYSIS
                            │
                            ▼
                  MANAGEMENT DECISIONS
```

---

# 🏗️ Project Phases

## 01 — Business Understanding

Defines the business problem, objectives, stakeholders, retail domain research, customer journey mapping, business and product KPIs, and project scope. Finalized **last**, after all other phases, so it accurately reflects what the project actually found — including its negative results.

## 02 — Hybrid Data Engineering

Builds the enterprise data foundation, combining real Olist marketplace data with a Python-generated synthetic behavioral layer.

### Key Activities
- Real public data ingestion & cleaning (orders, products, customers, sellers, payments, reviews)
- Python-generated synthetic data (sessions, events, marketing campaigns, inventory, identity resolution, experiment assignment)
- Login-event-based cross-device identity stitching
- Data validation, quality gates, and duplicate handling (e.g. the geolocation table's 261,831 duplicate rows, identified and resolved)

### Outcome
A structured, hybrid data layer capable of supporting a realistic omnichannel analysis, without misrepresenting synthetic data as real.

## 03 — Enterprise SQL Data Warehouse

Applies Kimball dimensional modeling to build a proper analytical foundation.

### Key Components
- Fact and Dimension tables (16 total)
- Star schema design, ER diagram, data dictionary
- Primary/foreign keys, referential integrity
- Appropriate indexing

### Outcome
28 / 28 validation checks passing — row-count reconciliation, grain checks, referential integrity, and business-logic checks, all independently verified.

## 04 — Advanced SQL Analytics

Uses SQL to analyze:
- Revenue trends over time
- Best-selling products and category performance
- Seller performance and revenue concentration
- Customer purchase behavior and revenue contribution

### Key Techniques
CTEs, window functions, ranking, aggregation, CASE logic, date analysis, subqueries.

### Outcome
The **top 10% of customers generate 41.14%** of total revenue — the first clear signal of the concentration risk that recurs throughout the rest of the project.

## 05 — Customer Journey Analytics

Maps and quantifies the full customer journey.

### Key Components
- Funnel analysis (Visit → Product View → Add to Cart → Checkout → Purchase)
- Session-type behavior analysis
- Cohort retention curve construction

### Outcome
The largest funnel drop-off is **Product View → Add to Cart (62.76%)**, and blended retention falls from 100% to **0.48% within one month** of first purchase — the two clearest, most actionable findings in the customer journey.

## 06 — Customer & Product Analytics

Converts customer and product behavior into quantified business value.

### Key Components
- RFM segmentation (Champions, Loyal Customers, Potential Loyalists, Needs Attention, At Risk, Lost Customers, New Customers)
- Historical Customer Lifetime Value
- North Star Metric definition
- Product KPI tree and feature prioritization framework

### Outcome
Champions carry a **10.07× higher average CLV** than At-Risk customers — a number precise enough to justify differentiated retention investment by segment.

## 07 — Recommendation Intelligence

Builds and rigorously offline-evaluates a content-based recommendation engine.

### Approach
Customer purchase history + product attributes (category, price, characteristics) → similarity scoring → personalized recommendations.

### Outcome
99.53% customer coverage, but a **0.07% Hit Rate@5 against a 1.07% naive popularity baseline** — the engine did not outperform simply recommending best-sellers, a result carried forward honestly into Phase 8 rather than treated as a finished success.

## 08 — Experimentation

Runs a controlled, statistically rigorous A/B test to confirm or refute Phase 7's finding in a live setting.

### Statistical Framework
- Hypothesis, control/treatment definition, sample size
- **Sample Ratio Mismatch (SRM) check** via chi-square goodness-of-fit — validated *before* analyzing results
- Significance testing (pooled SE for the hypothesis test, unpooled SE for the confidence interval)
- Effect size and 95% confidence interval

### Outcome
Treatment conversion (2.06%) vs. control (2.16%) — **not statistically significant (p = 0.8126)**. Formal decision: **DO NOT SHIP.**

## 09 — Power BI Executive Platform

Transforms every prior phase's findings into five interactive, cross-filterable dashboards.

### Dashboards
- **Executive** — revenue, orders, customers, conversion, retention, with a metric-switcher control
- **Sales** — category and seller performance, revenue concentration
- **Customer** — RFM segmentation, CLV, retention curve
- **Product** — funnel, recommendation engine evaluation, experiment results
- **Marketing** — campaign and channel performance

### Interactivity
- Synced category and date-range slicers across pages
- Cross-page drill-through (Sales → Product, filtered to the clicked category)
- A verified, root-caused fix to a retention-calculation methodology bug found during QA (see phase README for full details)

## 10 — Decision Scenarios & What-If Analysis

Turns the platform into an executive decision-support tool.

### Key Components
- Three adjustable What-If parameters: Conversion, Repeat Purchase, and AOV Improvement %
- Real-time scenario KPI cards (Current vs. Scenario)
- Three comparison visuals (Revenue Impact, Conversion Scenario, Customer Value Impact)
- Preset scenario buttons (Conservative / Moderate / Aggressive) via bookmarks, plus a Reset control
- An Executive Decision Framework explicitly distinguishing illustrative projection from forecast

---

# 💡 Key Business Recommendations

Based on the analytical findings, the platform recommends:

### 1. 🎯 Prioritize First-Month Retention

Given retention falls to 0.48% within one month, the highest-leverage retention window is immediate post-purchase — second-purchase incentives and win-back campaigns should be concentrated here, not spread evenly across a 12-month horizon.

### 2. 🛒 Fix Product View → Add to Cart Before Investing Further in Personalization

The largest funnel drop-off (62.76%) is a product-discoverability and cart-conversion problem — a more directly addressable opportunity than continuing to invest in an unproven recommendation engine.

### 3. 🚫 Do Not Deploy the Current Recommendation Engine

Backed by both an offline baseline comparison and a live controlled experiment — treat it as an exploratory capability requiring further development, not a ready product feature.

### 4. 📊 Prioritize Controlled Testing Over Channel Reallocation

With no statistically meaningful difference across 5 marketing channels, budget should not be shifted based on the small observed differences alone — structured experimentation is needed before making that call.

### 5. 💎 Differentiate Retention Investment by Segment

With a 10.07× CLV gap between Champions and At-Risk customers, retention spend should be targeted by segment value, not applied uniformly.

---

# 🚀 Feature Prioritization

The project uses an Impact vs. Effort framework.

| Initiative | Impact | Effort | Priority |
|---|---|---|---|
| First-Month Retention Campaign | High | Low | High |
| Cart-Conversion / Product-Discoverability Improvements | High | Medium | High |
| Segment-Based Retention Targeting (RFM/CLV) | High | Low | High |
| Executive Power BI Dashboard Suite | High | Medium | High |
| What-If Decision Scenario Tool | Medium | Medium | Medium |
| Recommendation Engine Redevelopment | Medium | High | Medium |
| Marketing Channel Experimentation Framework | Medium | Medium | Medium |
| Cross-Device Identity Resolution Expansion | Low | High | Low |

---

# 🧪 Experimentation

A fully executed **Recommendation Engine A/B Test** (`exp_001`) was run to validate whether personalized recommendations outperform a top-sellers control.

**Control Group:** Top Sellers recommendation strategy
**Treatment Group:** Content-based personalized recommendations

### Primary Metric
Purchase Conversion Rate

### Secondary Metrics
Recommendation CTR, Average Order Value, Revenue per User, Purchase Rate

### Result
Not statistically significant (p = 0.8126) — **DO NOT SHIP**, with the full statistical framework (SRM validation, significance test, confidence interval) documented in Phase 8.

---

# 💎 Business Value

The platform demonstrates how enterprise retail analytics can support:

### 📈 Revenue Growth
- Identify the highest-leverage funnel and retention opportunities.
- Quantify customer value to prioritize investment.

### ⚙️ Operational Efficiency
- Replace assumption-driven personalization and marketing decisions with tested evidence.
- Centralize reporting across five stakeholder-specific dashboards.

### 👔 Executive Decision Support
- Monitor business KPIs against one verified source of truth.
- Model hypothetical business-lever changes before committing budget.

### 💡 Product Decision Support
- Convert funnel and experimentation data into a clear product roadmap.
- Avoid investing further in an unproven recommendation engine.

### 🔬 Experimentation Discipline
- Demonstrate a real, predetermined statistical framework rather than post-hoc result interpretation.

---

# 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Database & Data Engineering | Microsoft SQL Server, SSMS, T-SQL |
| Data Modeling | Kimball Star Schema |
| Analytics | SQL, Advanced SQL |
| Synthetic Data Generation | Python |
| Statistics & Experimentation | T-SQL (chi-square SRM, z-test via Abramowitz-Stegun normal CDF approximation, pooled/unpooled SE) — independently cross-validated in Python (`scipy.stats`) |
| Business Intelligence | Microsoft Power BI, DAX |
| Documentation | Markdown |
| Version Control | Git, GitHub |

*A note on tooling:* Phase 8's statistical testing was deliberately implemented directly in T-SQL rather than delegated to a Python library, to demonstrate the underlying statistics were genuinely understood, and to keep the toolchain focused rather than broad for its own sake.

---

# 📂 Repository Structure

```text
ORGEE/
│
├── README.md
│
├── 01_Business_Understanding/
│
├── 02_Hybrid_Data_Engineering/
│
├── 03_Enterprise_SQL_Warehouse/
│
├── 04_Advanced_SQL_Analytics/
│
├── 05_Customer_Journey_Analytics/
│
├── 06_Customer_Product_Analytics/
│
├── 07_Recommendation_Intelligence/
│
├── 08_Experimentation/
│   └── python_validation/
│       ├── phase8_python_validation.py
│       └── python_validation_results.md
│
├── 09_PowerBI_Executive_Platform/
│   ├── ORGEE.pbix
│   ├── images/
│   ├── README.md
│   ├── data_model_reference.md
│   └── dax_reference.md
│
└── 10_Decision_Scenarios/
    ├── images/
    ├── 03_scenario_validation.md
    └── 04_phase10_readme.md
```

---

# 📊 Dataset

The project uses the **Olist Brazilian E-Commerce Public Dataset** as its real-data foundation, combined with a Python-generated synthetic behavioral layer.

### Real Data (Olist)
- ~99,441 orders, ~112,650 order items, ~32,951 products, ~3,095 sellers
- 71 product categories
- Real payments, reviews, and geolocation data (with 261,831 duplicate geolocation rows identified and handled during cleaning)

### Synthetic Data (Python-generated)
- 500,000 customer sessions, ~3,000,000 browsing events
- 50 marketing campaigns across 5 channels
- One fully executed A/B experiment (`exp_001`)
- Cross-device identity resolution via login-event stitching

> **Note on large data files:** five generated/raw files were excluded from this repository, either because they exceed GitHub's 100MB hard limit or its 50MB recommended limit, and are hosted externally instead:
> - [`events.csv`](https://drive.google.com/file/d/11hVTD_9GRkK-DlvMsBFr45i0A-7pvh8I/view?usp=drive_link) (~362MB)
> - [`campaign_exposures.csv`](https://drive.google.com/file/d/1BkWYIp0p2nzSJ43dNpke1v3w3qTXUdUv/view?usp=drive_link) (~108MB)
> - [`inventory_observations.csv`](https://drive.google.com/file/d/1HtT-xueyAtUMmAS3pPgEw_R8w4EPv4yr/view?usp=drive_link) (~89MB)
> - [`olist_geolocation_dataset.csv`](https://drive.google.com/file/d/1tj4grRnNVFQX57K0eE_0NWPXS2ml_zqD/view?usp=drive_link) (~58MB, raw)
> - [`sessions.csv`](https://drive.google.com/file/d/1jDxmWkbzxn0y6FPJURXuVxLQpzm5D3wh/view?usp=drive_link) (~52MB)
>
> All five are fully reproducible by running the documented Phase 2 Python pipeline (`python/generators/`) and public-data cleaning scripts (`python/phase_02_public_data_cleaning.py`) against the same seed data — the generation logic, not the output file, is what's meant to be reviewed here.

### Primary Business Outcome Field

`order_status = 'delivered'` — the qualifying condition for revenue, customer, and retention calculations throughout the project.

---

# ⚠️ Dataset & Project Limitations

This project combines real historical marketplace data with a synthetic behavioral layer. It does not represent a live, production retail platform. It does not contain:

- Real customer session or clickstream data (session-level behavior is synthetic)
- Real marketing spend or attribution data
- Real-time inventory or fulfillment data
- Customer service, returns, or refund records
- True causal outcomes for the untested growth levers modeled in Phase 10

Therefore, figures such as the Phase 10 What-If scenario projections are explicitly labeled **illustrative**, not forecasts — they show what a lever *would* produce *if* the assumed improvement were achieved, with no claim about the likelihood or cost of achieving it.

The project also identified and transparently corrected a real methodology issue during development: Phase 5's original SQL-derived customer retention curve used an unweighted average across cohorts, which was found during Phase 9 QA to disagree with the (statistically sounder) size-weighted Power BI calculation by more than 10× at the one-month mark. The root cause was identified, the SQL was corrected, and the fix was independently verified against Phase 4's separately-derived repeat-purchase rate. See Phase 9's README for the full writeup.

The project intentionally maintains transparency about these limitations, including its two negative findings (the recommendation engine's underperformance, and the marketing channels' lack of statistically meaningful difference).

---

# 🔮 Future Enhancements

Future versions of the platform could extend the solution with:

### ⚡ Real-Time & Production Infrastructure
- Kafka / Spark Streaming for real-time event processing
- FastAPI, Docker, Kubernetes, CI/CD, cloud deployment

### 🧠 Advanced Modeling
- Multiple competing recommendation approaches, formally compared
- SHAP or other explainability tooling, if a more complex model is introduced
- Deep learning, if justified by data scale
- Time-series forecasting, extending "what is happening" into "what will happen"

### 🤖 Decision Support
- An AI-assisted decision layer on top of the existing interpretable dashboards

### 🔬 Further Validation
- ✅ ~~A Python (`scipy.stats`) cross-check of the Phase 8 A/B test's SQL-derived statistics~~ — **completed**, exact match confirmed (see `08_Experimentation/python_validation/`)
- Re-testing the recommendation engine with an alternative modeling approach, now that content-based similarity has been shown not to outperform a naive baseline

These are intentionally scoped as future work, not gaps in Version 1 — this project's guiding principle throughout was **business insight over technology quantity**.

---

# 🏁 Final Outcome

ORGEE demonstrates a complete end-to-end enterprise retail analytics workflow.

The project connects:

```text
Business Understanding
        ↓
Data Engineering
        ↓
SQL Analytics
        ↓
Customer Journey Analytics
        ↓
Customer & Product Analytics
        ↓
Recommendation Intelligence
        ↓
Experimentation
        ↓
Business Intelligence
        ↓
Decision Scenarios
        ↓
Management Decision-Making
```

The final solution demonstrates how technical capabilities — SQL, data warehousing, statistical experimentation, and Power BI — can be integrated with business and product analytics to address practical retail growth challenges, including the discipline to report a negative result as clearly as a positive one.

It provides a structured foundation for:

- Customer Journey Optimization
- Customer Segmentation & Retention Strategy
- Product & Recommendation Evaluation
- Controlled Experimentation
- Executive Reporting
- Scenario-Based Decision Support

---

# 📌 Project Status

**Status: ✅ Completed**

### Completed Phases
- ✅ 01 — Business Understanding
- ✅ 02 — Hybrid Data Engineering
- ✅ 03 — Enterprise SQL Data Warehouse *(28/28 validation checks passing)*
- ✅ 04 — Advanced SQL Analytics
- ✅ 05 — Customer Journey Analytics *(retention methodology bug found and corrected)*
- ✅ 06 — Customer & Product Analytics
- ✅ 07 — Recommendation Intelligence
- ✅ 08 — Experimentation *(DO NOT SHIP decision, statistically validated)*
- ✅ 09 — Power BI Executive Platform *(fully interactive, design-consistency verified)*
- ✅ 10 — Decision Scenarios & What-If Analysis
- ✅ Python (`scipy.stats`) cross-validation of Phase 8's A/B test statistics *(exact match — p = 0.8126, CI confirmed to the decimal)*

### Planned Later
*(none — all planned work is complete)*

---

<div align="center">

## 🚀 ORGEE — Omnichannel Retail & Growth Experimentation Engine

**From Transaction Data → Customer Growth Intelligence → Executive Decisions**

<br>

*Business Analysis • Growth Analytics • Product Analytics • SQL • Experimentation • Power BI • Retail Analytics*

</div>
