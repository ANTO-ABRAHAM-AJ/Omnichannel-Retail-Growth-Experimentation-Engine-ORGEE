/*
    ============================================================
    ORGEE — Phase 6: Customer & Product Analytics
    01_rfm_analysis.sql
    ============================================================

    BUSINESS QUESTION
    Who are our most valuable and most engaged customers, based on
    how recently, how often, and how much they've purchased?

    GRAIN
    One row per customer_unique_id (person-level), not customer_id
    (which is one-per-order in this dataset — see Phase 4/5).

    METHODOLOGY CORRECTIONS — decided BEFORE writing this query,
    verified against the actual data:

    1. SNAPSHOT DATE: Recency is measured against the last order
       date actually present in the data (2018-08-29), computed
       dynamically below — NOT GETDATE(). This is 2016-2018
       historical data; scoring recency against today's real-world
       date would make every customer look maximally inactive.

    2. FREQUENCY SCORING: standard NTILE(5) quintile scoring is
       NOT used for Frequency. Verified: 97.00% of customers
       (90,557 of 93,358) placed exactly one delivered order —
       only 2,801 customers (3.00%) ever repeat-purchased at all,
       and it drops off fast after that (2,573 at 2 orders, down
       to single digits by 6+ orders). A quintile split on a
       variable this skewed would just arbitrarily tie-break
       identical values across buckets, not measure anything real.
       Instead, Frequency is scored on business-meaningful buckets
       grounded in the actual distribution: 1 order, 2 orders,
       3-4 orders, 5+ orders.

    Recency and Monetary both have enough continuous spread
    (Monetary: 8,455 distinct values across 93,358 customers) for
    standard NTILE(5) quintile scoring — verified before use.

    SCORING CONVENTION: 5 = best, 1 = worst, for all three of R/F/M.

    TECHNIQUES USED
    CTE, window functions (NTILE), CASE, aggregation, DATEDIFF.
    ============================================================
*/

IF OBJECT_ID('tempdb..#RFM') IS NOT NULL DROP TABLE #RFM;

WITH SnapshotDate AS (
    SELECT MAX(d.full_date) AS snapshot_date
    FROM dbo.Fact_Order_Items foi
    JOIN dbo.Dim_Date d ON foi.order_purchase_date_sk = d.date_sk
    WHERE foi.order_status = 'delivered'
),
CustomerRFMBase AS (
    SELECT
        dc.customer_unique_id,
        MAX(d.full_date) AS last_order_date,
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
        customer_unique_id,
        recency_days,
        frequency,
        monetary,
        -- Recency: 5 = most recent (smallest recency_days)
        NTILE(5) OVER (ORDER BY recency_days DESC, customer_unique_id ASC) AS r_score,
        -- Frequency: business-meaningful buckets, NOT a quintile
        -- (see methodology note above)
        CASE
            WHEN frequency = 1 THEN 1
            WHEN frequency = 2 THEN 3
            WHEN frequency BETWEEN 3 AND 4 THEN 4
            WHEN frequency >= 5 THEN 5
        END AS f_score,
        -- Monetary: 5 = highest total spend
        NTILE(5) OVER (ORDER BY monetary ASC, customer_unique_id ASC) AS m_score
    FROM CustomerRFMBase
)
SELECT
    customer_unique_id,
    recency_days,
    frequency,
    monetary,
    r_score,
    f_score,
    m_score,
    CONCAT(r_score, f_score, m_score) AS rfm_score,
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
INTO #RFM
FROM CustomerRFMScored;

-- ------------------------------------------------------------
-- Output 1: full customer-level RFM table (top 50 by rfm_sum,
-- for inspection — the full #RFM table feeds 02-04)
-- ------------------------------------------------------------

SELECT TOP 50
    customer_unique_id, recency_days, frequency, monetary,
    r_score, f_score, m_score, rfm_score, rfm_sum, segment
FROM #RFM
ORDER BY rfm_sum DESC, monetary DESC;

-- ------------------------------------------------------------
-- Output 2: score distribution sanity check — confirms R and M
-- are roughly evenly split into 5 groups (true quintiles) while
-- F is concentrated as expected given the real distribution
-- ------------------------------------------------------------

SELECT 'r_score' AS score_type, r_score AS score_value, COUNT(*) AS customer_count
FROM #RFM GROUP BY r_score
UNION ALL
SELECT 'f_score', f_score, COUNT(*) FROM #RFM GROUP BY f_score
UNION ALL
SELECT 'm_score', m_score, COUNT(*) FROM #RFM GROUP BY m_score
ORDER BY score_type, score_value;

-- ------------------------------------------------------------
-- Output 3: segment sizes (full detail in 02_customer_segmentation.sql)
-- ------------------------------------------------------------

SELECT
    segment,
    COUNT(*) AS customer_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_customers
FROM #RFM
GROUP BY segment
ORDER BY customer_count DESC;

DROP TABLE #RFM;

/*
    BUSINESS INTERPRETATION — fill in after running:
    - How many customers land in each segment, and does the size
      distribution make sense given 97% one-time-buyer reality?
    - Where the bulk of the customer base actually sits

    BUSINESS IMPLICATION — fill in after running:
    - Which segments are large enough to be worth a targeted
      campaign vs which are too small to prioritize
*/
