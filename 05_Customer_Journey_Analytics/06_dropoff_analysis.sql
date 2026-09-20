/*
    ============================================================
    ORGEE — Phase 5: Customer Journey Analytics
    06_dropoff_analysis.sql ⭐ SIGNATURE SCRIPT
    ============================================================

    BUSINESS QUESTION
    Where, specifically, are we losing the most customers in the
    journey? This script identifies the single largest drop-off
    point — the primary candidate for the Phase 5 signature insight.

    TECHNIQUES USED
    CTE, window functions (LAG, RANK), aggregation.
    ============================================================
*/

-- ------------------------------------------------------------
-- Stage-to-stage drop-off %, ranked to find the biggest single
-- friction point
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
),
StageTransitions AS (
    SELECT
        stage_order,
        stage_name,
        session_count AS stage_users,
        LAG(stage_name) OVER (ORDER BY stage_order) AS from_stage,
        LAG(session_count) OVER (ORDER BY stage_order) AS from_stage_users
    FROM FunnelCounts
)
SELECT
    from_stage,
    stage_name AS to_stage,
    from_stage_users,
    stage_users AS to_stage_users,
    from_stage_users - stage_users AS users_lost,
    ROUND(100.0 * (from_stage_users - stage_users) / NULLIF(from_stage_users, 0), 2) AS dropoff_pct,
    RANK() OVER (ORDER BY 100.0 * (from_stage_users - stage_users) / NULLIF(from_stage_users, 0) DESC) AS dropoff_severity_rank
FROM StageTransitions
WHERE from_stage IS NOT NULL
ORDER BY dropoff_severity_rank;

/*
    *** SIGNATURE INSIGHT ***
    Fill in with the actual transition and percentage returned
    above once run against the live warehouse. Format only
    (per Phase 5 requirements, do not predetermine or fabricate):

        "The largest customer drop-off occurs between X and Y,
         where Z% of users fail to progress."

    BUSINESS INTERPRETATION — fill in after running:
    - Is the biggest drop-off early (browsing → engagement) or
      late (checkout → purchase)? These imply very different fixes.

    BUSINESS IMPLICATION — fill in after running:
    - The specific intervention this points to (e.g. product page
      design if Visit→Product View is worst; checkout friction if
      Checkout→Purchase is worst)
*/
