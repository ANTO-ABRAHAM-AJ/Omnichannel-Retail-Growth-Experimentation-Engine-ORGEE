# ORGEE — Phase 4: Advanced SQL Analytics

**Business Question:**  
> **What happened?**

**Data Source:**  
Completed Phase 3 ORGEE enterprise SQL warehouse only.

**Raw CSV Usage:**  
None.

**Status:**  
**Completed, executed, documented, and validated.**

---

## 1. Overview

Phase 4 transforms the Phase 3 enterprise SQL warehouse into a set of business-facing analytical investigations using advanced SQL.

The objective is not simply to write SQL queries, but to answer practical business questions through:

**Business Question → SQL Analysis → Executed Result → Interpretation → Business Implication**

Phase 4 covers:

- Revenue
- Products
- Inventory
- Sellers
- Categories
- Customer purchasing behavior
- Customer revenue concentration
- Marketing performance
- Final analytical validation

The phase deliberately remains focused on:

> **What happened?**

More advanced behavioral, segmentation, predictive, recommendation, and experimentation analyses are intentionally deferred to later ORGEE phases.

---

# 2. Phase 4 Structure

| Script | Business Question | Key Techniques |
|---|---|---|
| `01_revenue_trends.sql` | How is revenue trending over time? | CTE, `LAG`, `CASE`, date dimension |
| `02_best_selling_products.sql` | Which products lead by volume versus revenue? | CTE, `RANK`, aggregation, subquery |
| `03_product_performance.sql` | Does price tier relate to review score? | `CASE`, aggregation, ranking |
| `04_inventory_health.sql` | Which products carry the greatest inventory risk? | CTE, `CASE`, `ROW_NUMBER`, aggregation |
| `05_seller_performance.sql` | Which sellers drive revenue and how concentrated is seller revenue? | `RANK`, `NTILE`, aggregation |
| `06_category_performance.sql` | Which categories drive revenue and which have high AOV? | `RANK`, window functions, aggregation |
| `07_customer_purchases.sql` | How often do customers repeat-purchase? | `CASE`, `ROW_NUMBER`, aggregation |
| `08_customer_revenue_contribution.sql` | How concentrated is revenue among high-value customers? | `NTILE`, `PERCENT_RANK`, window functions |
| `09_marketing_performance.sql` | Which channels and campaigns convert most efficiently? | `CASE`, `RANK`, aggregation |
| `10_phase4_validation.sql` | Are the Phase 4 assumptions and calculations valid? | Validation framework |

---

# 3. Analytical Coverage

## 01 — Revenue Trends

Measures:

- Monthly delivered revenue
- Gross revenue
- Order volume
- Month-over-month growth
- Revenue by order status

**Business Question:**

> How has revenue changed over time?

---

## 02 — Best-Selling Products

Compares products by:

- Units sold
- Total revenue
- Volume rank
- Revenue rank
- Rank divergence

**Business Question:**

> Are the products selling the most units also generating the most revenue?

---

## 03 — Product Performance

Evaluates:

- Price tiers
- Average review score
- Category-level review performance
- Category cancellation rates

**Business Question:**

> Does price level appear to relate to customer satisfaction?

---

## 04 — Inventory Health

Evaluates:

- Overall inventory status
- Low-stock events
- Out-of-stock events
- Product-level inventory risk
- Latest inventory status

**Business Question:**

> How healthy is inventory and where does inventory risk concentrate?

---

## 05 — Seller Performance

Evaluates:

- Top sellers by revenue
- Seller revenue quartiles
- Revenue concentration
- Revenue by seller state
- Average revenue per seller

**Business Question:**

> Which sellers drive revenue and how dependent is the marketplace on top sellers?

---

## 06 — Category Performance

Evaluates:

- Category revenue
- Revenue share
- Cumulative revenue concentration
- Average item price
- High-AOV categories outside the top revenue rankings

**Business Question:**

> Which categories drive revenue and which categories have high average item value?

---

## 07 — Customer Purchases

Evaluates:

- One-time buyers
- Two-order customers
- Three-to-five-order customers
- Six-or-more-order customers
- Repeat-purchase rate
- Time to second order

**Business Question:**

> Is the business predominantly driven by one-time buyers?

---

## 08 — Customer Revenue Contribution

Evaluates:

- Customer-level revenue
- Revenue ranking
- Revenue deciles
- Top 10% revenue contribution
- Top 20% revenue contribution

**Business Question:**

> How concentrated is revenue among the highest-value customers?

This is the **Phase 4 signature insight**.

---

## 09 — Marketing Performance

Evaluates:

- Impressions
- Clicks
- Conversions
- CTR
- Conversion rate
- Campaign-level performance
- Campaign-type performance

**Business Question:**

> Which marketing channels and campaigns convert most efficiently?

The analysis intentionally remains at the campaign/channel aggregate level.

---

## 10 — Phase 4 Validation

Performs final validation checks covering:

- Date integrity
- Analytical grain
- Customer grouping logic
- NULL handling
- Revenue percentage integrity
- Revenue decile integrity
- Ranking sanity

**Final result:**

> **8 PASS · 1 INFO · 0 FAIL**

---

# 4. Critical Data-Modeling Fix

One of the most important findings during Phase 4 was a customer-grain issue inherited from the Olist source structure.

`Dim_Customer.customer_id` is effectively an order-level identifier in this dataset.

Therefore, using `customer_id` for customer-level repeat-purchase analysis would incorrectly treat individual orders as separate customers.

The correct person-level identifier is:

`customer_unique_id`

The Phase 4 customer analyses therefore use `customer_unique_id` for:

- Repeat-purchase analysis
- Purchase-frequency analysis
- Time-to-second-order analysis
- Customer revenue concentration
- Revenue deciles
- Customer-level ranking

The correction was identified and applied before the customer-level results were finalized.

The final validation confirmed that the corrected grouping identifies genuine repeat purchasers.

---

# 5. Key Phase 4 Findings

## 5.1 Revenue Concentration — Signature Insight

The strongest Phase 4 finding is:

> **The top 10% of customers generate 41.14% of total revenue.**

The top 20% generate:

> **56.78% of total revenue.**

This demonstrates significant customer-level revenue concentration.

### Business Implication

A relatively small group of high-value customers contributes a disproportionately large share of revenue.

Therefore, future retention and customer-value analysis should consider customer economic contribution rather than treating all customers as equally valuable.

---

# 6. Revenue Trends

The highest completed-revenue month identified in the analysis is:

> **November 2017 — $987,765.37**

The revenue-by-order-status analysis shows:

> **97.28% of gross revenue comes from delivered orders.**

Canceled orders account for approximately:

> **0.70% of gross revenue.**

### Important Data-Boundary Note

September 2018 appears as the lowest month because it represents only a partial final-period observation.

It should therefore **not** be interpreted as evidence of a genuine business downturn.

---

# 7. Product Volume vs Revenue

The products leading by units sold are not identical to the products leading by total revenue.

This demonstrates:

> **Volume leadership and revenue leadership are different dimensions of product performance.**

A high-volume product can generate less revenue than a lower-volume product with a higher selling price.

### Business Implication

Product strategy should not rely on unit volume alone.

Relevant dimensions include:

- Units sold
- Revenue
- Average selling price
- Product ranking
- Rank divergence

---

# 8. Price Tier vs Customer Satisfaction

Average review scores remain relatively stable across the four price tiers.

| Price Tier | Average Review Score |
|---|---:|
| Under R$50 | 4.0769 |
| R$50–150 | 4.0752 |
| R$150–300 | 4.0974 |
| R$300+ | 4.1145 |

The difference between the tiers is relatively small.

### Key Takeaway

> **Higher price does not correspond to a large improvement in average review score in this dataset.**

Price tier alone therefore does not appear to strongly differentiate customer satisfaction.

---

# 9. Inventory Health

Historical inventory observations show:

| Inventory Status | Share |
|---|---:|
| In stock | 99.3584% |
| Low stock | 0.6388% |
| Out of stock | 0.0028% |

The latest product-level inventory snapshot shows approximately:

> **99.33% of products in stock**

and:

> **0.67% in low-stock status**

with no products appearing in the captured current out-of-stock result.

### Key Takeaway

Inventory health is strong overall.

Because genuine out-of-stock observations are extremely rare, low-stock frequency provides a more useful leading indicator of potential inventory pressure.

---

# 10. Seller Revenue Concentration

The seller analysis shows substantial revenue concentration.

The top seller revenue quartile contributes approximately:

> **86.78% of total seller revenue.**

### Key Takeaway

> **A relatively small group of top sellers drives the majority of seller revenue.**

### Business Implications

This supports future analysis of:

- Top-seller retention
- Seller relationship management
- Seller dependency
- Seller performance monitoring
- Geographic seller productivity

---

# 11. Customer Repeat Purchase

Using the corrected person-level identifier `customer_unique_id`, the analysis identifies:

- **93,358** unique customers
- **2,801** repeat customers
- **3.00%** repeat-purchase rate

The first-to-second-order analysis shows:

> **Average time to second order: approximately 114 days**

### Key Takeaway

The observed customer base is strongly dominated by one-time purchasing behavior.

This establishes an important baseline for the later customer-retention and customer-value phases.

---

# 12. Marketing Performance

Channel-level conversion rates are:

| Channel | Conversion Rate |
|---|---:|
| Display | **0.83%** |
| Search | 0.81% |
| Social | 0.80% |
| Email | 0.80% |
| Push | 0.78% |

Display has the highest conversion rate.

However, email generates the highest conversion volume:

> **2,549 conversions**

because it has substantially greater exposure volume.

### Key Takeaway

> **Highest conversion efficiency is not the same as highest conversion volume.**

Marketing decisions should therefore consider both:

**Scale + Efficiency**

rather than relying on a single metric.

---

# 13. Category Performance

The leading revenue categories include:

1. `health_beauty`
2. `watches_gifts`
3. `bed_bath_table`
4. `sports_leisure`
5. `computers_accessories`

The category concentration analysis shows that the first 17 ranked categories account for approximately:

> **80.76% of total category revenue.**

At the same time, the high-AOV analysis shows that some categories have much higher average item prices while ranking substantially lower by total revenue.

### Key Takeaway

> **Revenue scale and transaction value are different dimensions of category performance.**

A category can generate high revenue through volume without having the highest average item price.

---

# 14. Customer-Level Grain Correction

The customer identifier correction is a major data-modeling insight from Phase 4.

### Incorrect approach

`GROUP BY customer_id`

This would treat order-linked customer records as separate customers.

### Correct approach

`GROUP BY customer_unique_id`

This groups multiple orders belonging to the same real customer.

The corrected approach enables valid measurement of:

- Repeat-purchase rate
- Purchase frequency
- Time to second order
- Customer revenue concentration
- Revenue deciles

This is a **data-modeling correction**, not merely a SQL syntax correction.

---

# 15. Phase 4 Validation

The final validation script is:

`10_phase4_validation.sql`

The validation framework produced:

| Status | Checks |
|---|---:|
| PASS | 8 |
| INFO | 1 |
| FAIL | 0 |

## Final Validation Result

> **PHASE 4 VALIDATION: PASS**

---

## 15.1 Date Integrity

All populated `Fact_Order_Items.order_purchase_date_sk` values successfully resolve to `Dim_Date`.

Result:

`unresolved = 0`

**Status: PASS**

---

## 15.2 Product Grain

Product-level aggregation was checked for duplicate `product_id` rows.

Result:

> **PASS**

This confirms that the product-level analysis does not contain an unintended fan-out.

---

## 15.3 Customer Grouping

The corrected `customer_unique_id` grouping successfully identifies genuine repeat purchasers.

Result:

`repeat_customer_count = 2801`

**Status: PASS**

---

## 15.4 Foreign-Key NULL Checks

Customer foreign key:

`Fact_Order_Items.customer_sk`

**NULL values: 0**

Product foreign key:

`Fact_Order_Items.product_sk`

**NULL values: 0**

Both checks:

> **PASS**

---

## 15.5 Revenue Percentage Integrity

Revenue-by-order-status percentages sum to:

`100.000000%`

**Status: PASS**

---

## 15.6 Revenue Decile Integrity

Customer revenue deciles sum to:

`100.000000%`

**Status: PASS**

The top revenue decile also contributes more revenue than the bottom revenue decile.

**Status: PASS**

---

# 16. Informational Data Gap

The only non-PASS result is an informational observation:

> **623 of 32,951 products lack an English category name.**

This is a known source-data limitation.

It is classified as:

**INFO**

rather than a failure.

Where English category names are explicitly required, the relevant category analyses exclude NULL category names.

There are:

> **0 unresolved correctness issues from Phase 4 validation.**

---

# 17. Scope Boundaries

Phase 4 intentionally does **not** perform:

- Funnel analysis
- Session drop-off analysis
- Customer journey mapping
- Cohort retention curves
- RFM segmentation
- Customer Lifetime Value (CLV)
- Recommendation engines
- A/B testing
- Statistical experimentation
- Power BI dashboards
- What-If analysis

These capabilities belong to later ORGEE phases.

---

# 18. Marketing Scope Control

`09_marketing_performance.sql` operates at:

**Campaign → Channel → Campaign Type → Aggregate Performance**

It does not analyze:

**Session → Event → Journey → Funnel Drop-off**

This keeps Phase 4 focused on:

> **What happened?**

rather than:

> **How did the customer journey unfold?**

---

# 19. Reproducibility

All Phase 4 analysis is reproducible from the completed Phase 3 warehouse.

No raw CSV files are required.

The analytical flow is:

**Phase 3 Enterprise Warehouse**  
↓  
**Star Schema Facts**  
↓  
**Dimension Joins**  
↓  
**Advanced SQL**  
↓  
**Business-Facing Results**  
↓  
**Interpretation**  
↓  
**Business Implication**  
↓  
**Final Validation**

Each SQL script remains the authoritative source for its analytical logic.

The corresponding Results Markdown files provide:

- Executed outputs
- Screenshot evidence
- Row counts
- Business interpretation
- Business implications

---

# 20. Screenshot Evidence Convention

SQL result screenshots are stored under:

`images/`

Each result set follows the corresponding analysis number and letter.

Examples:

- `01A`
- `01B`
- `01C`
- `02A`
- `02B`
- `02C`
- `03A`
- `03B`
- `03C`

Example filenames:

- `03A_price_tier_review_score.png`
- `03B_category_review_performance.png`
- `03C_category_cancellation_rate.png`

For large result sets, a representative screenshot is used.

For small result sets, the complete output is captured.

Each Results Markdown file records:

- Total result rows
- Rows displayed
- Screenshot filename
- Screenshot path
- Output evidence
- Business interpretation
- Business implications

The SQL script remains the authoritative source for complete reproducibility.

---

# 21. Repository Structure

    04_Advanced_SQL_Analytics/
    │
    ├── 01_revenue_trends.sql
    ├── 01_Revenue_Trends_Results.md
    │
    ├── 02_best_selling_products.sql
    ├── 02_Best_Selling_Products_Results.md
    │
    ├── 03_product_performance.sql
    ├── 03_Product_Performance_Results.md
    │
    ├── 04_inventory_health.sql
    ├── 04_Inventory_Health_Results.md
    │
    ├── 05_seller_performance.sql
    ├── 05_Seller_Performance_Results.md
    │
    ├── 06_category_performance.sql
    ├── 06_Category_Performance_Results.md
    │
    ├── 07_customer_purchases.sql
    ├── 07_Customer_Purchases_Results.md
    │
    ├── 08_customer_revenue_contribution.sql
    ├── 08_Customer_Revenue_Contribution_Results.md
    │
    ├── 09_marketing_performance.sql
    ├── 09_Marketing_Performance_Results.md
    │
    ├── 10_phase4_validation.sql
    ├── 10_Phase4_Validation_Results.md
    │
    ├── README.md
    │
    └── images/
        ├── 01A_...
        ├── 01B_...
        ├── 01C_...
        ├── 02A_...
        ├── 02B_...
        ├── 02C_...
        ├── 03A_...
        ├── 03B_...
        ├── 03C_...
        ├── 04A_...
        ├── 04B_...
        ├── 04C_...
        ├── 05A_...
        ├── 05B_...
        ├── 05C_...
        ├── 06A_...
        ├── 06B_...
        ├── 06C_...
        ├── 07A_...
        ├── 07B_...
        ├── 07C_...
        ├── 08A_...
        ├── 08B_...
        ├── 08C_...
        ├── 09A_...
        ├── 09B_...
        ├── 09C_...
        ├── 10A_phase4_validation_results.png
        └── 10B_phase4_validation_summary.png

---

# 22. Phase 4 Completion Checklist

- [x] 01 — Revenue Trends
- [x] 02 — Best-Selling Products
- [x] 03 — Product Performance
- [x] 04 — Inventory Health
- [x] 05 — Seller Performance
- [x] 06 — Category Performance
- [x] 07 — Customer Purchases
- [x] 08 — Customer Revenue Contribution
- [x] 09 — Marketing Performance
- [x] 10 — Phase 4 Validation
- [x] All SQL scripts executed against the ORGEE warehouse
- [x] Actual outputs captured
- [x] Business interpretations documented
- [x] Business implications documented
- [x] Screenshot evidence documented
- [x] Large result sets documented using representative excerpts
- [x] Customer grain issue identified and corrected
- [x] Signature insight independently confirmed
- [x] Final validation completed
- [x] 0 validation failures

---

# 23. Phase 4 Connection to Later Phases

The ORGEE analytical progression is:

**PHASE 4 — Advanced SQL Analytics**  
↓  
**What happened?**  
↓  
Revenue → Products → Inventory → Sellers → Categories → Customers → Marketing  
↓  
**PHASE 5 — Customer Journey Analytics**  
↓  
**Where do customers drop off?**  
↓  
**PHASE 6 — Customer & Product Analytics**  
↓  
**Which customers and products are most valuable?**  
↓  
**PHASE 7 — Recommendation Intelligence**  
↓  
**What should we recommend?**  
↓  
**PHASE 8 — Experimentation**  
↓  
**Does personalization improve conversion?**

Phase 4 therefore establishes the descriptive analytical foundation required by the subsequent phases.

---

# 24. Final Phase 4 Status

## ✅ COMPLETE — VALIDATED

Phase 4 Advanced SQL Analytics successfully transforms the Phase 3 enterprise warehouse into a validated analytical layer covering:

**Revenue → Products → Inventory → Sellers → Categories → Customers → Revenue Concentration → Marketing**

The phase produces both:

- Technical SQL evidence
- Business-facing analytical insights

### Final Validation

**8 PASS · 1 INFO · 0 FAIL**

### Signature Insight

> **The top 10% of customers generate 41.14% of total revenue, while the top 20% generate 56.78%.**

### Final Assessment

> **Phase 4 is complete, executed, documented, and validated against the ORGEE enterprise warehouse.**