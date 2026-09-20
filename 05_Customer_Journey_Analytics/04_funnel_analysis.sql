/*
    ============================================================
    ORGEE — Phase 5: Customer Journey Analytics
    04_funnel_analysis.sql ⭐ SIGNATURE SCRIPT
    ============================================================

    BUSINESS QUESTION
    What does the core customer funnel look like — Visit → Product
    View → Add to Cart → Checkout → Purchase — and what is the
    conversion rate at each stage?

    GRAIN NOTE
    Every count is DISTINCT session_id, not raw event rows.

    TECHNIQUES USED
    CTE, CASE, LAG (stage-over-stage comparison), window functions,
    aggregation.
    ============================================================
*/

-- ------------------------------------------------------------
-- Core funnel: stage counts, stage conversion rate (vs prior
-- stage), and overall conversion rate (vs Visit)
-- ------------------------------------------------------------

WITH StageSessions AS (
    SELECT
        session_id,
        MAX(CASE WHEN event_type = 'session_start'          THEN 1 ELSE 0 END) AS visit,
        MAX(CASE WHEN event_type = 'product_view'            THEN 1 ELSE 0 END) AS product_view,
        MAX(CASE WHEN event_type = 'add_to_cart'               THEN 1 ELSE 0 END) AS add_to_cart,
        MAX(CASE WHEN event_type = 'checkout_start'              THEN 1 ELSE 0 END) AS checkout,
        MAX(CASE WHEN event_type = 'purchase_interaction'           THEN 1 ELSE 0 END) AS purchase
    FROM dbo.Fact_Events
    GROUP BY session_id
),
FunnelCounts AS (
    SELECT 1 AS stage_order, 'Visit'         AS stage_name, SUM(visit)         AS session_count FROM StageSessions
    UNION ALL
    SELECT 2, 'Product View', SUM(product_view) FROM StageSessions
    UNION ALL
    SELECT 3, 'Add to Cart',  SUM(add_to_cart)  FROM StageSessions
    UNION ALL
    SELECT 4, 'Checkout',     SUM(checkout)     FROM StageSessions
    UNION ALL
    SELECT 5, 'Purchase',     SUM(purchase)     FROM StageSessions
)
SELECT
    stage_order,
    stage_name,
    session_count,
    LAG(session_count) OVER (ORDER BY stage_order) AS prior_stage_count,
    CASE
        WHEN LAG(session_count) OVER (ORDER BY stage_order) IS NULL THEN NULL
        ELSE ROUND(100.0 * session_count / LAG(session_count) OVER (ORDER BY stage_order), 2)
    END AS stage_conversion_rate_pct,
    ROUND(
        100.0 * session_count / FIRST_VALUE(session_count) OVER (ORDER BY stage_order),
        2
    ) AS overall_conversion_rate_pct
FROM FunnelCounts
ORDER BY stage_order;

-- ------------------------------------------------------------
-- Relative loss at each stage — how much of the ORIGINAL visit
-- population is lost at each specific step (not just vs prior
-- stage — this shows where the biggest absolute bleed is)
-- ------------------------------------------------------------

WITH StageSessions AS (
    SELECT
        session_id,
        MAX(CASE WHEN event_type = 'session_start'          THEN 1 ELSE 0 END) AS visit,
        MAX(CASE WHEN event_type = 'product_view'            THEN 1 ELSE 0 END) AS product_view,
        MAX(CASE WHEN event_type = 'add_to_cart'               THEN 1 ELSE 0 END) AS add_to_cart,
        MAX(CASE WHEN event_type = 'checkout_start'              THEN 1 ELSE 0 END) AS checkout,
        MAX(CASE WHEN event_type = 'purchase_interaction'           THEN 1 ELSE 0 END) AS purchase
    FROM dbo.Fact_Events
    GROUP BY session_id
),
FunnelCounts AS (
    SELECT 1 AS stage_order, 'Visit'         AS stage_name, SUM(visit)         AS session_count FROM StageSessions
    UNION ALL
    SELECT 2, 'Product View', SUM(product_view) FROM StageSessions
    UNION ALL
    SELECT 3, 'Add to Cart',  SUM(add_to_cart)  FROM StageSessions
    UNION ALL
    SELECT 4, 'Checkout',     SUM(checkout)     FROM StageSessions
    UNION ALL
    SELECT 5, 'Purchase',     SUM(purchase)     FROM StageSessions
)
SELECT
    stage_order,
    stage_name,
    session_count,
    FIRST_VALUE(session_count) OVER (ORDER BY stage_order) - session_count AS lost_vs_original_visits,
    ROUND(
        100.0 * (FIRST_VALUE(session_count) OVER (ORDER BY stage_order) - session_count)
        / FIRST_VALUE(session_count) OVER (ORDER BY stage_order), 2
    ) AS pct_of_original_visits_lost
FROM FunnelCounts
ORDER BY stage_order;

/*
    BUSINESS INTERPRETATION — fill in after running:
    - The shape of the funnel — is loss gradual and even, or
      concentrated at one specific step?
    - The overall Visit-to-Purchase conversion rate

    BUSINESS IMPLICATION — fill in after running:
    - Where funnel-optimization effort would have the highest
      leverage (quantified precisely in 06_dropoff_analysis.sql)
*/
