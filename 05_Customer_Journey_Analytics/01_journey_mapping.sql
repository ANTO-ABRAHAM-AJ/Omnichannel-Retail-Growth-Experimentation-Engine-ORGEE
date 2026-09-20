/*
    ============================================================
    ORGEE — Phase 5: Customer Journey Analytics
    01_journey_mapping.sql
    ============================================================

    BUSINESS QUESTION
    What does the actual sequence of customer interactions look
    like, and how many sessions reach each stage of the journey?

    DATA SOURCE
    Fact_Events / Fact_Sessions only (the synthetic behavioral
    dataset). Deliberately NOT cross-referenced against
    Fact_Order_Items — session-level "purchase_interaction" events
    were never reconciled against real Olist order rows, so mixing
    the two would be a false data-integrity assumption. The funnel
    is self-contained within the behavioral data.

    GRAIN NOTE
    A session can contain multiple events of the same type (e.g.
    several product_view events). Every count below is DISTINCT
    session_id, not raw event rows — otherwise sessions with more
    activity would be over-counted.

    TECHNIQUES USED
    CTE, CASE, aggregation, scalar subqueries, percentage calculations.
    ============================================================
*/

-- ------------------------------------------------------------
-- Journey stage reach: how many distinct sessions ever produced
-- each stage's qualifying event
-- ------------------------------------------------------------

WITH StageSessions AS (
    SELECT
        session_id,
        MAX(CASE WHEN event_type = 'session_start'        THEN 1 ELSE 0 END) AS reached_visit,
        MAX(CASE WHEN event_type = 'product_view'          THEN 1 ELSE 0 END) AS reached_product_view,
        MAX(CASE WHEN event_type = 'add_to_cart'             THEN 1 ELSE 0 END) AS reached_add_to_cart,
        MAX(CASE WHEN event_type = 'checkout_start'            THEN 1 ELSE 0 END) AS reached_checkout,
        MAX(CASE WHEN event_type = 'purchase_interaction'         THEN 1 ELSE 0 END) AS reached_purchase
    FROM dbo.Fact_Events
    GROUP BY session_id
)
SELECT
    'Visit'         AS journey_stage, SUM(reached_visit)         AS session_count, 1 AS stage_order
FROM StageSessions
UNION ALL
SELECT 'Product View', SUM(reached_product_view), 2 FROM StageSessions
UNION ALL
SELECT 'Add to Cart',  SUM(reached_add_to_cart), 3 FROM StageSessions
UNION ALL
SELECT 'Checkout',     SUM(reached_checkout), 4 FROM StageSessions
UNION ALL
SELECT 'Purchase',     SUM(reached_purchase), 5 FROM StageSessions
ORDER BY stage_order;

-- ------------------------------------------------------------
-- Stage reach as % of total sessions (not % of prior stage —
-- that's drop-off analysis, handled in 06_dropoff_analysis.sql)
-- ------------------------------------------------------------

WITH StageSessions AS (
    SELECT
        session_id,
        MAX(CASE WHEN event_type = 'product_view'          THEN 1 ELSE 0 END) AS reached_product_view,
        MAX(CASE WHEN event_type = 'add_to_cart'             THEN 1 ELSE 0 END) AS reached_add_to_cart,
        MAX(CASE WHEN event_type = 'checkout_start'            THEN 1 ELSE 0 END) AS reached_checkout,
        MAX(CASE WHEN event_type = 'purchase_interaction'         THEN 1 ELSE 0 END) AS reached_purchase
    FROM dbo.Fact_Events
    GROUP BY session_id
),
TotalSessions AS (
    SELECT COUNT(*) AS total FROM dbo.Fact_Sessions
)
SELECT
    (SELECT total FROM TotalSessions) AS total_sessions,
    SUM(reached_product_view) AS product_view_sessions,
    ROUND(100.0 * SUM(reached_product_view) / (SELECT total FROM TotalSessions), 2) AS product_view_pct,
    SUM(reached_add_to_cart) AS add_to_cart_sessions,
    ROUND(100.0 * SUM(reached_add_to_cart) / (SELECT total FROM TotalSessions), 2) AS add_to_cart_pct,
    SUM(reached_checkout) AS checkout_sessions,
    ROUND(100.0 * SUM(reached_checkout) / (SELECT total FROM TotalSessions), 2) AS checkout_pct,
    SUM(reached_purchase) AS purchase_sessions,
    ROUND(100.0 * SUM(reached_purchase) / (SELECT total FROM TotalSessions), 2) AS purchase_pct
FROM StageSessions;

/*
    BUSINESS INTERPRETATION — fill in after running:
    - What fraction of all sessions ever engage past a simple visit?
    - How steep is the overall shape of the journey?

    BUSINESS IMPLICATION — fill in after running:
    - Where the biggest opportunity for journey-level intervention sits
      (detailed drop-off quantification comes in 06_dropoff_analysis.sql)
*/
