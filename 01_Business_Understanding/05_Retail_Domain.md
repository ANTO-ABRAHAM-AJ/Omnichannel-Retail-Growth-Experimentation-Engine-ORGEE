# Phase 1 — Business Understanding
## 05. Retail Domain Research

---

## 1. The E-Commerce Marketplace Domain

ORGEE is grounded in the real-world dynamics of online marketplace retail, using the public **Olist** dataset — a genuine Brazilian e-commerce marketplace spanning 2016–2018 — as its factual foundation, layered with a purpose-built synthetic behavioral dataset to reconstruct the omnichannel signals (sessions, browsing events, marketing exposure, cross-device identity) that a real retailer has, but that a public order-level dataset doesn't include on its own.

A marketplace differs from a single-brand retailer in ways that directly shaped this project's findings and are worth understanding explicitly:

- **Many independent sellers, not one inventory owner.** Olist's real data includes 3,095 distinct sellers. This makes seller concentration a genuine strategic risk — the Phase 4 finding that the top 25% of sellers generate 86.78% of total seller revenue is a real marketplace dynamic, not an artifact of how the data was generated.
- **A broad, long-tail category structure.** 71 real product categories are present, from health_beauty and watches_gifts (the top revenue drivers) down to niche categories contributing comparatively little. This "long tail" pattern — a small number of categories carrying most of the revenue — is typical of marketplace retail specifically, as opposed to a curated single-brand catalog.
- **Lower organic repeat-purchase rates than other retail sub-domains.** Marketplace and general e-commerce retail typically see lower repeat-purchase rates than subscription retail (where repeat purchase is structurally built in) or grocery retail (where purchase frequency is naturally high due to consumable goods). ORGEE's real, measured 3.00% repeat-purchase rate is consistent with this domain pattern — it reflects a genuine characteristic of marketplace retail rather than an unusually poor outcome specific to this dataset.
- **Fragmented, multi-method payment behavior.** The real data includes multiple payment types and installment plans, reflecting actual purchasing behavior in this market rather than a simplified single-payment-method assumption.

## 2. Why This Domain Was Chosen Over a Fully Synthetic Dataset

A fully synthetic dataset can be shaped to produce whatever pattern is convenient for a project's narrative. Building on real transactional data instead means the core business facts — revenue concentration, category performance, seller dependency, and repeat-purchase behavior — reflect patterns that genuinely occurred in a real marketplace. The synthetic layer added on top was scoped narrowly and specifically: it exists only to supply the omnichannel behavioral dimension (session-level browsing, cart activity, marketing exposure, and a controlled experiment) that the real Olist dataset structurally cannot provide, since it is an order-level, not session-level, dataset. Every core business finding in this project — the funnel drop-off point, the retention curve, the category concentration, the seller dependency — is grounded in this real-world domain context, not invented to fit a narrative.

## 3. Domain Implications for This Project's Findings

Understanding this domain context changes how several of ORGEE's findings should be read:

- The **3.00% repeat-purchase rate** is not evidence of a failing business — it is a typical marketplace pattern, which is exactly why it represents a genuine growth opportunity rather than a symptom to be alarmed by.
- The **62.76% Product View → Add to Cart drop-off** is consistent with marketplace retail's typically higher browsing-to-cart friction compared to curated single-brand retail, where product discovery is a smaller part of the journey.
- The **recommendation engine underperforming a popularity baseline** is a plausible, real outcome in a marketplace with 71 categories and a long-tail catalog — content-based similarity can struggle precisely where category and product diversity is high, which is a genuine domain-level explanation worth investigating further before assuming the engine's architecture itself is simply broken.
