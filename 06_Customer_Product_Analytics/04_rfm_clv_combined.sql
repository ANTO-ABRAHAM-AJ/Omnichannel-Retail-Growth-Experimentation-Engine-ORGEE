/*
    ============================================================
    ORGEE — Phase 6: Customer & Product Analytics
    04_rfm_clv_combined.sql ⭐ SIGNATURE SCRIPT
    ============================================================

    BUSINESS QUESTION
    Bringing RFM behavior and historical value together — which
    segments should the business retain, grow, win back, or
    deprioritize?

    Self-contained (recomputes the same RFM/CLV base as 01-03).

    TECHNIQUES USED
    CTE, CASE, aggregation, ranking.
    ============================================================
*/

IF OBJECT_ID('tempdb..#RFMCLV') IS NOT NULL DROP TABLE #RFMCLV;

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
INTO #RFMCLV
FROM CustomerRFMScored;

-- ------------------------------------------------------------
-- *** THE COMBINED TABLE *** — segment, customers, revenue,
-- avg CLV, avg frequency, avg recency, ranked by value
-- ------------------------------------------------------------

SELECT
    segment,
    COUNT(*) AS customers,
    ROUND(SUM(monetary), 2) AS revenue,
    ROUND(100.0 * SUM(monetary) / SUM(SUM(monetary)) OVER (), 2) AS pct_of_revenue,
    ROUND(AVG(monetary), 2) AS avg_clv,
    ROUND(AVG(frequency * 1.0), 2) AS avg_frequency,
    ROUND(AVG(recency_days * 1.0), 1) AS avg_recency_days,
    RANK() OVER (ORDER BY AVG(monetary) DESC) AS value_rank
FROM #RFMCLV
GROUP BY segment
ORDER BY value_rank;

-- ------------------------------------------------------------
-- Retention-priority view: segments with meaningful historical
-- value that are showing recency decay (candidates for
-- win-back / retention action, sized by revenue at stake)
-- ------------------------------------------------------------

SELECT
    segment,
    COUNT(*) AS customers,
    ROUND(SUM(monetary), 2) AS revenue_at_stake,
    ROUND(AVG(recency_days * 1.0), 1) AS avg_recency_days
FROM #RFMCLV
WHERE segment IN ('At Risk', 'Lost Customers')
GROUP BY segment
ORDER BY revenue_at_stake DESC;

DROP TABLE #RFMCLV;

/*
    BUSINESS INTERPRETATION — fill in after running:
    - Which segment ranks highest on value, and by how much does
      it outpace the rest?
    - How much revenue currently sits in "At Risk" — i.e. how much
      is genuinely at stake if nothing changes

    BUSINESS IMPLICATION — fill in after running:
    - This table is the direct input to 08_feature_prioritization.sql
      and 10_business_impact_analysis.sql — flag here which segment(s)
      warrant the first recommendation
*/
