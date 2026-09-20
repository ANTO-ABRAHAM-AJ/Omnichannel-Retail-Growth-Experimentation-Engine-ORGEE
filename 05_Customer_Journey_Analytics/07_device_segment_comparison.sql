/*
    ============================================================
    ORGEE — Phase 5: Customer Journey Analytics
    07_device_segment_comparison.sql
    ============================================================

    BUSINESS QUESTION
    Beyond device/platform (already covered in
    05_funnel_conversion_by_dimension.sql), are there other
    meaningful segment differences in journey behavior — session
    length category, and identified vs anonymous traffic?

    DATA NOTE
    Only ~18% of sessions ever resolve to a known customer (the
    anonymous-until-login identity model from Phase 2/3). This
    script deliberately compares "identified" vs "anonymous"
    session behavior as a real, data-supported segment — not a
    fabricated one.

    TECHNIQUES USED
    CTE, CASE, aggregation.
    ============================================================
*/

-- ------------------------------------------------------------
-- Conversion by session_type (short / medium / long)
-- ------------------------------------------------------------

WITH SessionConversion AS (
    SELECT
        fs.session_id,
        fs.session_type,
        CASE WHEN EXISTS (
            SELECT 1 FROM dbo.Fact_Events fe
            WHERE fe.session_id = fs.session_id AND fe.event_type = 'purchase_interaction'
        ) THEN 1 ELSE 0 END AS converted
    FROM dbo.Fact_Sessions fs
)
SELECT
    session_type,
    COUNT(*) AS session_count,
    SUM(converted) AS converting_sessions,
    ROUND(100.0 * SUM(converted) / COUNT(*), 2) AS conversion_rate_pct
FROM SessionConversion
GROUP BY session_type
ORDER BY conversion_rate_pct DESC;

-- ------------------------------------------------------------
-- Identified vs anonymous sessions — engagement and conversion
-- ------------------------------------------------------------

WITH SessionSegment AS (
    SELECT
        fs.session_id,
        CASE WHEN fs.customer_sk IS NOT NULL THEN 'Identified' ELSE 'Anonymous' END AS identity_segment,
        fs.session_duration_seconds,
        (SELECT COUNT(*) FROM dbo.Fact_Events fe WHERE fe.session_id = fs.session_id) AS event_count,
        CASE WHEN EXISTS (
            SELECT 1 FROM dbo.Fact_Events fe
            WHERE fe.session_id = fs.session_id AND fe.event_type = 'purchase_interaction'
        ) THEN 1 ELSE 0 END AS converted
    FROM dbo.Fact_Sessions fs
)
SELECT
    identity_segment,
    COUNT(*) AS session_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_sessions,
    AVG(CAST(session_duration_seconds AS FLOAT)) AS avg_duration_seconds,
    AVG(CAST(event_count AS FLOAT)) AS avg_events_per_session,
    SUM(converted) AS converting_sessions,
    ROUND(100.0 * SUM(converted) / COUNT(*), 2) AS conversion_rate_pct
FROM SessionSegment
GROUP BY identity_segment;

-- ------------------------------------------------------------
-- Geographic segment — conversion by customer state
-- (identified sessions only, since state requires a resolved
-- customer)
-- ------------------------------------------------------------

WITH SessionState AS (
    SELECT
        fs.session_id,
        dc.customer_state,
        CASE WHEN EXISTS (
            SELECT 1 FROM dbo.Fact_Events fe
            WHERE fe.session_id = fs.session_id AND fe.event_type = 'purchase_interaction'
        ) THEN 1 ELSE 0 END AS converted
    FROM dbo.Fact_Sessions fs
    JOIN dbo.Dim_Customer dc ON fs.customer_sk = dc.customer_sk
)
SELECT TOP 10
    customer_state,
    COUNT(*) AS session_count,
    SUM(converted) AS converting_sessions,
    ROUND(100.0 * SUM(converted) / COUNT(*), 2) AS conversion_rate_pct
FROM SessionState
GROUP BY customer_state
HAVING COUNT(*) >= 30
ORDER BY conversion_rate_pct DESC;

/*
    BUSINESS INTERPRETATION — fill in after running:
    - Does identified traffic convert meaningfully better than
      anonymous traffic (as you'd expect for logged-in, higher-
      intent users), or is the gap small?
    - Any state-level pattern worth noting

    BUSINESS IMPLICATION — fill in after running:
    - Whether encouraging login earlier in the journey is worth
      pursuing based on the actual identified-vs-anonymous gap
*/
