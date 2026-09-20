/*
    ============================================================
    ORGEE — Phase 5: Customer Journey Analytics
    02_session_analysis.sql
    ============================================================

    BUSINESS QUESTION
    How do sessions behave — how much activity, how much time spent,
    and how does that differ between sessions that convert and
    sessions that don't?

    TECHNIQUES USED
    CTE, CASE, aggregation, window functions, subquery.
    ============================================================
*/

-- ------------------------------------------------------------
-- Overall session volume by month
-- ------------------------------------------------------------

SELECT
    d.year_number,
    d.month_number,
    d.month_name,
    COUNT(*) AS session_count
FROM dbo.Fact_Sessions fs
JOIN dbo.Dim_Date d ON fs.session_start_date_sk = d.date_sk
GROUP BY d.year_number, d.month_number, d.month_name
ORDER BY d.year_number, d.month_number;

-- ------------------------------------------------------------
-- Events per session — overall distribution
-- ------------------------------------------------------------

WITH EventsPerSession AS (
    SELECT session_id, COUNT(*) AS event_count
    FROM dbo.Fact_Events
    GROUP BY session_id
)
SELECT
    COUNT(*) AS total_sessions_with_events,
    AVG(CAST(event_count AS FLOAT)) AS avg_events_per_session,
    MIN(event_count) AS min_events,
    MAX(event_count) AS max_events,
    (
        SELECT DISTINCT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY event_count) OVER ()
        FROM EventsPerSession
    ) AS median_events_per_session
FROM EventsPerSession;

-- ------------------------------------------------------------
-- Converting vs non-converting sessions — engagement comparison
-- (a "converting" session is one that produced a
-- purchase_interaction event)
-- ------------------------------------------------------------

WITH SessionOutcome AS (
    SELECT
        fs.session_id,
        fs.session_duration_seconds,
        fs.session_type,
        (SELECT COUNT(*) FROM dbo.Fact_Events fe WHERE fe.session_id = fs.session_id) AS event_count,
        CASE WHEN EXISTS (
            SELECT 1 FROM dbo.Fact_Events fe
            WHERE fe.session_id = fs.session_id AND fe.event_type = 'purchase_interaction'
        ) THEN 'Converting' ELSE 'Non-converting' END AS session_outcome
    FROM dbo.Fact_Sessions fs
)
SELECT
    session_outcome,
    COUNT(*) AS session_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_sessions,
    AVG(CAST(session_duration_seconds AS FLOAT)) AS avg_duration_seconds,
    AVG(CAST(event_count AS FLOAT)) AS avg_events_per_session
FROM SessionOutcome
GROUP BY session_outcome;

-- ------------------------------------------------------------
-- Device-level session behavior: volume and conversion rate
-- ------------------------------------------------------------

WITH SessionConversion AS (
    SELECT
        fs.session_id,
        dd.device_type,
        dd.platform,
        CASE WHEN EXISTS (
            SELECT 1 FROM dbo.Fact_Events fe
            WHERE fe.session_id = fs.session_id AND fe.event_type = 'purchase_interaction'
        ) THEN 1 ELSE 0 END AS converted
    FROM dbo.Fact_Sessions fs
    LEFT JOIN dbo.Dim_Device dd ON fs.device_sk = dd.device_sk
)
SELECT
    device_type,
    platform,
    COUNT(*) AS session_count,
    SUM(converted) AS converting_sessions,
    ROUND(100.0 * SUM(converted) / COUNT(*), 2) AS conversion_rate_pct
FROM SessionConversion
GROUP BY device_type, platform
ORDER BY conversion_rate_pct DESC;

/*
    BUSINESS INTERPRETATION — fill in after running:
    - Do converting sessions show materially more engagement
      (longer, more events) than non-converting ones, or is the
      difference small?
    - Any device/platform combination that stands out on conversion

    BUSINESS IMPLICATION — fill in after running:
    - Where UX/engagement investment might move conversion
*/
