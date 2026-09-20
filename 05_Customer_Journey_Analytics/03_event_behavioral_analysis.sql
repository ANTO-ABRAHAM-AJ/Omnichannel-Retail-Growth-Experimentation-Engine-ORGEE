/*
    ============================================================
    ORGEE — Phase 5: Customer Journey Analytics
    03_event_behavioral_analysis.sql
    ============================================================

    BUSINESS QUESTION
    Which behaviors within a session are associated with a
    successful (converting) journey versus an unsuccessful one?

    TECHNIQUES USED
    CTE, CASE, aggregation, subquery.
    ============================================================
*/

-- ------------------------------------------------------------
-- Overall event type distribution
-- ------------------------------------------------------------

SELECT
    event_type,
    COUNT(*) AS event_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_events
FROM dbo.Fact_Events
GROUP BY event_type
ORDER BY event_count DESC;

-- ------------------------------------------------------------
-- Behavior comparison: converting vs non-converting sessions
-- (average count of each event type per session, by outcome)
-- ------------------------------------------------------------

WITH SessionOutcome AS (
    SELECT
        fs.session_id,
        CASE WHEN EXISTS (
            SELECT 1 FROM dbo.Fact_Events fe
            WHERE fe.session_id = fs.session_id AND fe.event_type = 'purchase_interaction'
        ) THEN 'Converting' ELSE 'Non-converting' END AS session_outcome
    FROM dbo.Fact_Sessions fs
),
EventCounts AS (
    SELECT
        so.session_outcome,
        fe.event_type,
        COUNT(*) AS event_count
    FROM dbo.Fact_Events fe
    JOIN SessionOutcome so ON fe.session_id = so.session_id
    GROUP BY so.session_outcome, fe.event_type
),
SessionCounts AS (
    SELECT session_outcome, COUNT(*) AS session_count
    FROM SessionOutcome
    GROUP BY session_outcome
)
SELECT
    ec.session_outcome,
    ec.event_type,
    ec.event_count,
    sc.session_count,
    ROUND(1.0 * ec.event_count / sc.session_count, 3) AS avg_events_of_this_type_per_session
FROM EventCounts ec
JOIN SessionCounts sc ON ec.session_outcome = sc.session_outcome
ORDER BY ec.session_outcome, ec.event_type;

-- ------------------------------------------------------------
-- Search behavior: does searching correlate with conversion?
-- ------------------------------------------------------------

WITH SessionSearch AS (
    SELECT
        fs.session_id,
        CASE WHEN EXISTS (
            SELECT 1 FROM dbo.Fact_Events fe
            WHERE fe.session_id = fs.session_id AND fe.event_type = 'search'
        ) THEN 1 ELSE 0 END AS did_search,
        CASE WHEN EXISTS (
            SELECT 1 FROM dbo.Fact_Events fe
            WHERE fe.session_id = fs.session_id AND fe.event_type = 'purchase_interaction'
        ) THEN 1 ELSE 0 END AS converted
    FROM dbo.Fact_Sessions fs
)
SELECT
    CASE WHEN did_search = 1 THEN 'Searched' ELSE 'Did not search' END AS search_behavior,
    COUNT(*) AS session_count,
    SUM(converted) AS converting_sessions,
    ROUND(100.0 * SUM(converted) / COUNT(*), 2) AS conversion_rate_pct
FROM SessionSearch
GROUP BY CASE WHEN did_search = 1 THEN 'Searched' ELSE 'Did not search' END;

-- ------------------------------------------------------------
-- Cart abandonment signal: sessions with add_to_cart but no
-- checkout_start
-- ------------------------------------------------------------

WITH CartBehavior AS (
    SELECT
        session_id,
        MAX(CASE WHEN event_type = 'add_to_cart' THEN 1 ELSE 0 END) AS added_to_cart,
        MAX(CASE WHEN event_type = 'checkout_start' THEN 1 ELSE 0 END) AS started_checkout,
        MAX(CASE WHEN event_type = 'remove_from_cart' THEN 1 ELSE 0 END) AS removed_from_cart
    FROM dbo.Fact_Events
    GROUP BY session_id
)
SELECT
    SUM(added_to_cart) AS sessions_added_to_cart,
    SUM(CASE WHEN added_to_cart = 1 AND started_checkout = 0 THEN 1 ELSE 0 END) AS abandoned_before_checkout,
    ROUND(
        100.0 * SUM(CASE WHEN added_to_cart = 1 AND started_checkout = 0 THEN 1 ELSE 0 END)
        / NULLIF(SUM(added_to_cart), 0), 2
    ) AS cart_abandonment_rate_pct,
    SUM(removed_from_cart) AS sessions_with_cart_removal
FROM CartBehavior;

/*
    BUSINESS INTERPRETATION — fill in after running:
    - Which specific behaviors most strongly distinguish converting
      from non-converting sessions?
    - How large is the cart-abandonment problem specifically?

    BUSINESS IMPLICATION — fill in after running:
    - Concrete UX interventions suggested by the behavior gap
      (e.g. cart-recovery messaging, search prominence)
*/
