# Phase 9/10 — Power BI Data Model Reference
## ORGEE — Omnichannel Retail & Growth Experimentation Engine

**Location:** ORGEE.pbix
**Purpose:** Documents every table, column, and measure in the Power BI data model — the companion reference to the Phase 3 SQL data dictionary, but for the reporting layer specifically.

---

## Dimension Tables

### Dim_Customer
customer_city, customer_id, customer_sk, customer_state, customer_unique_id, customer_zip_code_prefix, load_timestamp

### Dim_Date
date_sk, day_name, day_of_month, day_of_week, full_date, is_weekend, month_name, month_number, MonthYear *(calculated column)*, MonthYearSort *(calculated column)*, quarter_number, year_number

### Dim_Device
device_sk, device_type, platform

### Dim_Experiment
control_variant_label, end_timestamp, experiment_id, experiment_name, experiment_sk, load_timestamp, objective, primary_metric, start_timestamp, treatment_variant_label

### Dim_Product
load_timestamp, product_category_name, product_category_name_english, product_description_length, product_height_cm, product_id, product_length_cm, product_name_length, product_photos_qty, product_sk, product_weight_g, product_width_cm

### Dim_Seller
load_timestamp, seller_city, seller_id, seller_sk, seller_state, seller_zip_code_prefix

### Dim_Campaign
campaign_id, campaign_name, campaign_sk, campaign_type, channel, end_date, load_timestamp, objective, start_date

---

## Fact Tables

### Fact_Order_Items
customer_sk, freight_value, load_timestamp, order_id, order_item_id, order_item_sk, order_purchase_date_sk, order_status, payment_installments_max, payment_type_primary, payment_value_order_total, price, product_sk, seller_sk

### Fact_Recommendation_Events
anonymous_id, customer_sk, event_date_sk, event_timestamp, event_type, experiment_sk, load_timestamp, product_sk, recommendation_event_id, recommendation_event_sk, session_id, variant

### Fact_Reviews
customer_sk, load_timestamp, order_id, review_answer_date_sk, review_comment_message, review_comment_title, review_creation_date_sk, review_id, review_score, review_sk

---

## Analytical / Reporting Tables

### Customer_RFM_Segments
customer_unique_id, f_score, frequency, historical_clv, m_score, r_score, recency_days, rfm_sum, segment

### Customer_Cohort_Retention
cohort_month, cohort_size, months_since_cohort, retained_customers, retention_rate_pct
*(No relationship to Dim_Product — cannot be filtered by product category. See Phase 9 README, Section 7.)*

### Experiment_Results_Facts
Metric, Value

### expt experiment_population
assignment_timestamp, customer_sk, is_eligible, variant

### reco recommendations
customer_unique_id, rec_sk, recommendation_rank, recommended_product_id, similarity_score, top_category

### reco eval_recommendations
customer_unique_id, product_sk, recommendation_rank, similarity_score

### Recommendation_Evaluation_Facts
Metric, Value

### vw_Daily_Campaign_Performance
campaign_id, campaign_name, campaign_type, channel, clicks, conversions, full_date, impressions

### vw_Daily_Product_Funnel
add_to_cart, checkout, full_date, month_number, product_views, purchase, visits, year_number
*(No relationship to Dim_Product — cannot be filtered by product category. See Phase 9 README, Section 7.)*

---

## Phase 10 — What-If Parameters

### AOV Improvement %
AOV Improvement %, AOV Improvement % Value

### Conversion Improvement %
Conversion Improvement %, Conversion Improvement % Value

### Repeat Purchase Improvement %
Repeat Purchase Improvement %, Repeat Purchase Improvement % Value

---

## Core Measures (Phase 9 — `Table` / `_Measures`)

The following measures power the 5 Phase 9 dashboard pages. Formulas for each are documented in `dax_reference.md` (companion file).

- Active Customers
- AOV
- Average CLV
- Avg Recommendation Similarity
- Delivered Orders
- Overall Campaign Conversion Rate %
- Overall CTR %
- Purchase Conversion Rate %
- Recommendation Coverage %
- Repeat Purchase Rate %
- Revenue per Active Customer
- Total Campaign Impressions
- Total Historical CLV
- Total Revenue
- Weighted Retention Rate %

## Scenario Measures (Phase 10)

Built during this project's Phase 10 work — formulas documented in full in `04_phase10_readme.md`:

- Incremental Revenue
- Retention Revenue Contribution
- Revenue Uplift %
- Scenario AOV
- Scenario Conversion Rate
- Scenario Customers
- Scenario Repeat Purchase Rate
- Scenario Revenue
- Scenario Revenue per Customer

## Supporting Visual-Control Objects

- Executive Chart Title *(measure)*
- Executive Metric Selector *(field parameter, drives the Executive page's chart-swap control)*
