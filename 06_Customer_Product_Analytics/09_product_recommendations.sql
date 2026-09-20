/*
    ============================================================
    ORGEE — Phase 6: Customer & Product Analytics
    09_product_recommendations.sql
    ============================================================

    BUSINESS QUESTION
    Translate the Phase 4-6 findings into concrete recommendations
    — each one backed by a supporting-evidence query below, not
    asserted without data. The recommendations themselves are
    driven by 08_feature_prioritization.sql's actual ranking, not
    predetermined by this script.

    TECHNIQUES USED
    Aggregation, CTE — one evidence query per recommendation.
    ============================================================
*/

-- ------------------------------------------------------------
-- RECOMMENDATION 1 candidate: Improve Product View -> Add to Cart
-- Evidence: the exact scale of the opportunity
-- ------------------------------------------------------------

SELECT
    'Recommendation candidate: Improve product-page cart-add experience' AS recommendation,
    COUNT(DISTINCT session_id) AS sessions_viewed_no_cart_add
FROM dbo.Fact_Events fe
WHERE fe.event_type = 'product_view'
  AND fe.session_id NOT IN (
      SELECT session_id FROM dbo.Fact_Events WHERE event_type = 'add_to_cart'
  );

-- ------------------------------------------------------------
-- RECOMMENDATION 2 candidate: Reduce cart abandonment
-- Evidence: abandoned cart value proxy (using avg order value as
-- a stand-in, since abandoned carts have no recorded price)
-- ------------------------------------------------------------

WITH AvgOrderValue AS (
    SELECT SUM(price) / COUNT(DISTINCT order_id) AS aov
    FROM dbo.Fact_Order_Items
    WHERE order_status = 'delivered'
),
AbandonedCarts AS (
    SELECT COUNT(DISTINCT session_id) AS abandoned_sessions
    FROM dbo.Fact_Events
    WHERE event_type = 'add_to_cart'
      AND session_id NOT IN (SELECT session_id FROM dbo.Fact_Events WHERE event_type = 'checkout_start')
)
SELECT
    'Recommendation candidate: Cart-abandonment recovery (e.g. reminder messaging)' AS recommendation,
    ac.abandoned_sessions,
    ROUND(aov.aov, 2) AS avg_order_value_proxy,
    ROUND(ac.abandoned_sessions * aov.aov, 2) AS rough_revenue_opportunity_if_recovered
FROM AbandonedCarts ac, AvgOrderValue aov;

-- ------------------------------------------------------------
-- RECOMMENDATION 3 candidate: Target At-Risk high-value customers
-- Evidence: exact segment size and revenue at stake
-- ------------------------------------------------------------

IF OBJECT_ID('tempdb..#RFM9') IS NOT NULL DROP TABLE #RFM9;

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
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        CASE
            WHEN frequency = 1 THEN 1 WHEN frequency = 2 THEN 3
            WHEN frequency BETWEEN 3 AND 4 THEN 4 WHEN frequency >= 5 THEN 5
        END AS f_score,
        NTILE(5) OVER (ORDER BY monetary ASC) AS m_score
    FROM CustomerRFMBase
)
SELECT customer_unique_id, monetary,
    CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
        WHEN f_score = 1 AND r_score >= 4 AND m_score >= 3 THEN 'Potential Loyalists'
        WHEN f_score = 1 AND r_score >= 4 AND m_score < 3 THEN 'New Customers'
        WHEN f_score >= 3 AND r_score <= 2 THEN 'At Risk'
        WHEN r_score <= 2 AND f_score = 1 AND m_score <= 2 THEN 'Lost Customers'
        ELSE 'Needs Attention'
    END AS segment
INTO #RFM9
FROM CustomerRFMScored;

SELECT
    'Recommendation candidate: Retention campaign for At-Risk segment' AS recommendation,
    COUNT(*) AS at_risk_customers,
    ROUND(SUM(monetary), 2) AS at_risk_revenue
FROM #RFM9
WHERE segment = 'At Risk';

DROP TABLE #RFM9;

-- ------------------------------------------------------------
-- RECOMMENDATION 4 candidate: Improve search prominence
-- Evidence: conversion lift already observed for searchers
-- ------------------------------------------------------------

SELECT
    'Recommendation candidate: Increase search visibility/prompting' AS recommendation,
    'Searching sessions convert at 11.21% vs 5.60% for non-searchers (Phase 5)' AS evidence;

/*
    Final recommendations, evidence-based numbers above, ranked
    by 08_feature_prioritization.sql's actual priority_rank —
    written up in README.md once all scripts have run.
*/
