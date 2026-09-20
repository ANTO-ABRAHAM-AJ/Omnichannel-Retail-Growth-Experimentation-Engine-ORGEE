/*
    ============================================================
    ORGEE — Phase 9: Power BI Executive Decision Platform
    00_prerequisite_checks.sql
    ============================================================

    BUSINESS QUESTION
    Before opening Power BI, does the warehouse actually have
    stable, permanent tables for Power BI to connect to — and is
    the marketing data usable at all?

    WHY THIS SCRIPT EXISTS:
    Phases 5 (cohorts/retention) and 6 (RFM/CLV) were built as
    self-contained SQL scripts using temp tables — every run
    recomputed everything from scratch, and the results vanished
    when the session ended. Power BI needs a permanent table to
    connect to; it cannot run those old temp-table scripts itself.
    This script persists that ALREADY-VALIDATED logic (identical
    to the confirmed-correct Phase 5/6 versions, not a new
    analysis) into two small permanent tables.

    It also runs a first, honest look at the marketing data
    (Fact_Campaign_Exposures / Dim_Campaign), which has never been
    touched by any analysis in Phases 4-8 — this is exploratory
    only, to inform whether Dashboard 5 is buildable at all, not
    a finished design.

    TECHNIQUES USED
    CTE, NTILE with deterministic tiebreakers (per the Phase 6 fix),
    cohort date-diff logic (per Phase 5's methodology), schema
    inspection.
    ============================================================
*/

-- ------------------------------------------------------------
-- PART 1: Persist RFM + CLV segmentation (identical logic to the
-- final, validated Phase 6 scripts — same snapshot date,
-- same frequency bucketing, same NTILE tiebreakers, same segment
-- CASE precedence)
-- ------------------------------------------------------------

IF OBJECT_ID('dbo.Customer_RFM_Segments', 'U') IS NOT NULL DROP TABLE dbo.Customer_RFM_Segments;

;WITH SnapshotDate AS (
    SELECT MAX(d.full_date) AS snapshot_date
    FROM dbo.Fact_Order_Items foi
    JOIN dbo.Dim_Date d ON foi.order_purchase_date_sk = d.date_sk
    WHERE foi.order_status = 'delivered'
),
CustomerRFMBase AS (
    SELECT
        dc.customer_unique_id,
        COUNT(DISTINCT foi.order_id) AS frequency,
        SUM(foi.price) AS monetary,
        DATEDIFF(DAY, MAX(d.full_date), (SELECT snapshot_date FROM SnapshotDate)) AS recency_days
    FROM dbo.Fact_Order_Items foi
    JOIN dbo.Dim_Customer dc ON foi.customer_sk = dc.customer_sk
    JOIN dbo.Dim_Date d ON foi.order_purchase_date_sk = d.date_sk
    WHERE foi.order_status = 'delivered'
    GROUP BY dc.customer_unique_id
),
CustomerRFMScored AS (
    SELECT
        customer_unique_id, recency_days, frequency, monetary,
        NTILE(5) OVER (ORDER BY recency_days DESC, customer_unique_id ASC) AS r_score,
        CASE
            WHEN frequency = 1 THEN 1 WHEN frequency = 2 THEN 3
            WHEN frequency BETWEEN 3 AND 4 THEN 4 WHEN frequency >= 5 THEN 5
        END AS f_score,
        NTILE(5) OVER (ORDER BY monetary ASC, customer_unique_id ASC) AS m_score
    FROM CustomerRFMBase
)
SELECT
    customer_unique_id,
    recency_days,
    frequency,
    monetary AS historical_clv,
    r_score, f_score, m_score,
    (r_score + f_score + m_score) AS rfm_sum,
    CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
        WHEN f_score = 1 AND r_score >= 4 AND m_score >= 3 THEN 'Potential Loyalists'
        WHEN f_score = 1 AND r_score >= 4 AND m_score < 3 THEN 'New Customers'
        WHEN f_score >= 3 AND r_score <= 2 THEN 'At Risk'
        WHEN r_score <= 2 AND f_score = 1 AND m_score <= 2 THEN 'Lost Customers'
        ELSE 'Needs Attention'
    END AS segment
INTO dbo.Customer_RFM_Segments
FROM CustomerRFMScored;

CREATE CLUSTERED INDEX IX_Customer_RFM_Segments_CustomerID
    ON dbo.Customer_RFM_Segments (customer_unique_id);

-- Verify: should exactly match Phase 6's confirmed segment counts
-- (Needs Attention 39,337 / Potential Loyalists 21,655 /
--  Lost Customers 15,238 / New Customers 14,486 /
--  Loyal Customers 2,413 / At Risk 116 / Champions 113)
SELECT segment, COUNT(*) AS customer_count, SUM(historical_clv) AS segment_revenue
FROM dbo.Customer_RFM_Segments
GROUP BY segment
ORDER BY customer_count DESC;

-- ------------------------------------------------------------
-- PART 2: Persist cohort/retention (identical methodology to
-- Phase 5 — Fact_Order_Items only, real order data, month-since-
-- first-purchase cohort logic)
-- ------------------------------------------------------------

IF OBJECT_ID('dbo.Customer_Cohort_Retention', 'U') IS NOT NULL DROP TABLE dbo.Customer_Cohort_Retention;

;WITH CustomerFirstOrder AS (
    SELECT
        dc.customer_unique_id,
        MIN(DATEFROMPARTS(d.year_number, d.month_number, 1)) AS cohort_month
    FROM dbo.Fact_Order_Items foi
    JOIN dbo.Dim_Customer dc ON foi.customer_sk = dc.customer_sk
    JOIN dbo.Dim_Date d ON foi.order_purchase_date_sk = d.date_sk
    WHERE foi.order_status = 'delivered'
    GROUP BY dc.customer_unique_id
),
CustomerOrderMonths AS (
    SELECT DISTINCT
        dc.customer_unique_id,
        DATEFROMPARTS(d.year_number, d.month_number, 1) AS order_month
    FROM dbo.Fact_Order_Items foi
    JOIN dbo.Dim_Customer dc ON foi.customer_sk = dc.customer_sk
    JOIN dbo.Dim_Date d ON foi.order_purchase_date_sk = d.date_sk
    WHERE foi.order_status = 'delivered'
),
CohortActivity AS (
    SELECT
        cfo.cohort_month,
        cfo.customer_unique_id,
        DATEDIFF(MONTH, cfo.cohort_month, com.order_month) AS months_since_cohort
    FROM CustomerFirstOrder cfo
    JOIN CustomerOrderMonths com ON com.customer_unique_id = cfo.customer_unique_id
    WHERE DATEDIFF(MONTH, cfo.cohort_month, com.order_month) BETWEEN 0 AND 12
),
CohortSizes AS (
    SELECT cohort_month, COUNT(DISTINCT customer_unique_id) AS cohort_size
    FROM CustomerFirstOrder
    GROUP BY cohort_month
)
SELECT
    ca.cohort_month,
    ca.months_since_cohort,
    cs.cohort_size,
    COUNT(DISTINCT ca.customer_unique_id) AS retained_customers,
    ROUND(100.0 * COUNT(DISTINCT ca.customer_unique_id) / cs.cohort_size, 4) AS retention_rate_pct
INTO dbo.Customer_Cohort_Retention
FROM CohortActivity ca
JOIN CohortSizes cs ON cs.cohort_month = ca.cohort_month
GROUP BY ca.cohort_month, ca.months_since_cohort, cs.cohort_size;

CREATE CLUSTERED INDEX IX_Customer_Cohort_Retention_Cohort
    ON dbo.Customer_Cohort_Retention (cohort_month, months_since_cohort);

-- Verify: overall retention curve should match Phase 5's finding
-- (collapses to ~0.4-0.5% by month 1, stays flat ~0.2% through
-- month 12 — a genuinely low-retention business, not an error)
SELECT
    months_since_cohort,
    SUM(cohort_size) AS total_cohort_customers,
    SUM(retained_customers) AS total_retained,
    ROUND(100.0 * SUM(retained_customers) / SUM(cohort_size), 4) AS blended_retention_pct
FROM dbo.Customer_Cohort_Retention
GROUP BY months_since_cohort
ORDER BY months_since_cohort;

-- ------------------------------------------------------------
-- PART 3: Marketing data — exploratory only, NOT a final design.
-- First confirm the actual schema before assuming any column
-- names, since this table has never been touched by any prior
-- phase's analysis.
-- ------------------------------------------------------------

SELECT
    c.name AS column_name,
    t.name AS data_type,
    c.max_length,
    c.is_nullable
FROM sys.columns c
JOIN sys.types t ON c.user_type_id = t.user_type_id
WHERE c.object_id = OBJECT_ID('dbo.Fact_Campaign_Exposures')
ORDER BY c.column_id;

SELECT * FROM dbo.Dim_Campaign;

SELECT TOP 20 * FROM dbo.Fact_Campaign_Exposures;

SELECT
    COUNT(*) AS total_exposures,
    COUNT(DISTINCT campaign_sk) AS distinct_campaigns_referenced,
    (SELECT COUNT(*) FROM dbo.Dim_Campaign) AS total_campaigns_in_dim
FROM dbo.Fact_Campaign_Exposures;

/*
    BUSINESS INTERPRETATION — fill in after running:
    - Does Part 1's segment breakdown exactly match Phase 6's
      confirmed numbers? (It should — this is the same logic,
      just persisted.)
    - Does Part 2's blended retention curve match Phase 5's
      finding (collapsing to ~0.2-0.5% and staying flat)?
    - Part 3: what does Fact_Campaign_Exposures actually contain —
      does it have a clear exposure->conversion signal, or is it
      too sparse/undifferentiated to support a real dashboard?

    BUSINESS IMPLICATION — fill in after running:
    - Confirms Dashboard 3 (Customer) has real, permanent data to
      connect to
    - Determines whether Dashboard 5 (Marketing) is buildable, or
      should be honestly omitted per the plan's own principle
*/
