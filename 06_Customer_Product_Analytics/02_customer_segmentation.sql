/*
    ============================================================
    ORGEE — Phase 6: Customer & Product Analytics
    02_customer_segmentation.sql
    ============================================================

    BUSINESS QUESTION
    How big is each RFM segment, how much revenue does it drive,
    and what distinguishes its purchasing behavior?

    Self-contained (recomputes the same RFM base as
    01_rfm_analysis.sql — each Phase 6 script runs independently,
    same convention as Phase 5).

    TECHNIQUES USED
    CTE, CASE, window functions, aggregation.
    ============================================================
*/

IF OBJECT_ID('tempdb..#RFM2') IS NOT NULL DROP TABLE #RFM2;

WITH SnapshotDate AS (
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
            WHEN frequency = 1 THEN 1
            WHEN frequency = 2 THEN 3
            WHEN frequency BETWEEN 3 AND 4 THEN 4
            WHEN frequency >= 5 THEN 5
        END AS f_score,
        NTILE(5) OVER (ORDER BY monetary ASC, customer_unique_id ASC) AS m_score
    FROM CustomerRFMBase
)
SELECT
    customer_unique_id, recency_days, frequency, monetary,
    CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
        WHEN f_score = 1 AND r_score >= 4 AND m_score >= 3 THEN 'Potential Loyalists'
        WHEN f_score = 1 AND r_score >= 4 AND m_score < 3 THEN 'New Customers'
        WHEN f_score >= 3 AND r_score <= 2 THEN 'At Risk'
        WHEN r_score <= 2 AND f_score = 1 AND m_score <= 2 THEN 'Lost Customers'
        ELSE 'Needs Attention'
    END AS segment
INTO #RFM2
FROM CustomerRFMScored;

-- ------------------------------------------------------------
-- Segment profile: size, revenue, revenue share, AOV, frequency,
-- recency — the core Phase 6 segmentation table
-- ------------------------------------------------------------

SELECT
    segment,
    COUNT(*) AS customer_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_customers,
    SUM(monetary) AS segment_revenue,
    ROUND(100.0 * SUM(monetary) / SUM(SUM(monetary)) OVER (), 2) AS pct_revenue_contribution,
    ROUND(AVG(monetary), 2) AS avg_customer_value,
    ROUND(AVG(monetary * 1.0 / frequency), 2) AS avg_order_value,
    ROUND(AVG(frequency * 1.0), 2) AS avg_frequency,
    ROUND(AVG(recency_days * 1.0), 1) AS avg_recency_days
FROM #RFM2
GROUP BY segment
ORDER BY segment_revenue DESC;

-- ------------------------------------------------------------
-- Revenue efficiency: revenue per customer vs revenue per
-- 1-percentage-point of the customer base — which segments are
-- "punching above their weight"?
-- ------------------------------------------------------------

SELECT
    segment,
    COUNT(*) AS customer_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_customers,
    ROUND(100.0 * SUM(monetary) / SUM(SUM(monetary)) OVER (), 2) AS pct_of_revenue,
    ROUND(
        (100.0 * SUM(monetary) / SUM(SUM(monetary)) OVER ())
        / NULLIF(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 0), 2
    ) AS revenue_share_to_customer_share_ratio
FROM #RFM2
GROUP BY segment
ORDER BY revenue_share_to_customer_share_ratio DESC;

DROP TABLE #RFM2;

/*
    BUSINESS INTERPRETATION — fill in after running:
    - Which segments carry disproportionate revenue relative to
      their size (ratio > 1)?
    - How large is the "Needs Attention" catch-all — if it's large,
      the segment rules may need refinement (documented honestly
      either way)

    BUSINESS IMPLICATION — fill in after running:
    - Which segments justify dedicated marketing spend given their
      actual size and revenue contribution
*/
