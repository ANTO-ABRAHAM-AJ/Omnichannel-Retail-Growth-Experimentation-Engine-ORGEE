# Phase 1 — Business Understanding
## 01. Executive Summary

**Project:** ORGEE — Omnichannel Retail & Growth Experimentation Engine
**Project 2** of a two-project portfolio (Project 1: Risk Intelligence & Fraud Analytics — a separate project, focused on fraud detection rather than growth analytics).
**Theme:** Customer Growth • Product Analytics • Experimentation • Executive Decision Support

---

## 1. What ORGEE Is

ORGEE is an end-to-end retail analytics platform built to answer one question for retail leadership: **where should the business focus to grow revenue, retain customers, and improve product experience?**

It is not a single dashboard or a single model. It is a full analytics pipeline — from raw data to an executive decision-support tool — built the way a real retail analytics function would build one: starting from a hybrid data foundation, moving through a properly modeled enterprise data warehouse, layering on progressively deeper analysis, testing a specific growth hypothesis with a controlled experiment, and finally putting the findings in front of decision-makers in an interactive form they can actually use.

## 2. Why It Was Built This Way

Most portfolio analytics projects either (a) work from a single flat CSV with no real data-engineering discipline, or (b) reach for the newest, most impressive-sounding tools regardless of whether the business question needs them. ORGEE was deliberately built against both patterns. It combines **real transaction data** (the public Olist Brazilian marketplace dataset — orders, products, customers, sellers, payments, reviews) with a **purpose-built synthetic layer** (customer sessions, browsing events, marketing campaigns, inventory, and a formal A/B experiment) specifically to reconstruct the omnichannel behavioral signals a real retailer has, but that a public order-level dataset doesn't include on its own. Every phase was scoped to answer a real question with the simplest adequate tool, not to demonstrate the widest possible toolkit — a principle stated explicitly in Phase 9's scope document as *"business insight over technology quantity."*

## 3. The Architecture

```
BUSINESS UNDERSTANDING
        ↓
HYBRID DATA ENGINEERING  (real Olist data + Python-generated behavioral layer)
        ↓
CUSTOMER EVENT LAYER  (sessions, funnel, cross-device identity)
        ↓
ENTERPRISE SQL DATA WAREHOUSE  (Kimball star schema)
        ↓
ADVANCED SQL ANALYTICS
        ↓
CUSTOMER JOURNEY ANALYTICS  (funnel, cohorts, retention curves)
        ↓
CUSTOMER & PRODUCT ANALYTICS  (RFM, CLV, North Star metric)
        ↓
RECOMMENDATION INTELLIGENCE  (content-based engine)
        ↓
EXPERIMENTATION  (A/B test, SRM, statistical significance)
        ↓
POWER BI EXECUTIVE PLATFORM  (5 dashboards)
        ↓
DECISION SCENARIOS & WHAT-IF ANALYSIS  (interactive scenario modeling)
        ↓
   MANAGEMENT DECISIONS
```

Ten phases, each producing one dedicated deliverable, each building on the verified output of the phase before it — not ten independent exercises loosely bundled together.

## 4. What the Data Actually Showed

- **$13.22M** in delivered revenue across **96,478 orders** and **93,358 active customers**, at a **$137.04** average order value.
- Revenue is heavily concentrated: the **top 10% of customers generate 41.14%** of total revenue, and the top 20% generate 56.78% — a real dependency risk, not a hypothetical one.
- **Retention is the single biggest opportunity in the business.** Only **3.00%** of customers ever place a second order, and blended retention falls from 100% at the point of purchase to just **0.48% within one month**.
- The largest single point of friction in the customer journey is **Product View → Add to Cart, a 62.76% drop-off** — larger than any other stage in the funnel, including the final purchase step itself.
- A content-based recommendation engine was built and evaluated — and **underperformed a simple popularity baseline** (0.07% vs. 1.07% Hit Rate@5). A follow-up, properly controlled A/B experiment confirmed this: personalized recommendations showed **no statistically significant improvement** over a top-sellers control (p = 0.81), leading to a formal **DO NOT SHIP** decision.
- Marketing campaign performance was **statistically indistinguishable across all 5 channels tested** — meaning there is currently no evidence-based case for shifting budget toward any one channel over another.

## 5. Why the Negative Results Matter

Two of ORGEE's central findings — the recommendation engine's underperformance and the marketing channels' lack of meaningful difference — are negative results. They are reported here with the same rigor and prominence as the positive findings, not softened or reframed, because a retail analytics function that only reports what looks good isn't one that can be trusted with the next decision. Both findings came from a predetermined statistical framework (a Sample Ratio Mismatch check, a significance test, and a confidence interval, all defined before the experiment was analyzed) specifically so the result couldn't be quietly reinterpreted after the fact.

## 6. What This Enables

The completed platform lets retail leadership move from *"what happened?"* (Phase 9's five executive dashboards) to *"what would happen if we changed something?"* (Phase 10's interactive What-If scenario tool) — testing hypothetical improvements to conversion, retention, and order value against the business's real, verified baseline before committing budget or roadmap time to any one lever.
