/*
    ============================================================
    ORGEE — Phase 5: Customer Journey Analytics
    09_retention_curves.sql ⭐
    ============================================================

    BUSINESS QUESTION
    Beyond a single cohort table, what does the overall shape of
    retention look like — how quickly do customers stop coming
    back, and does that pattern hold consistently across cohorts?

    Self-contained (recomputes the same cohort base as
    08_cohort_analysis.sql — each Phase 5 script runs independently).

    TECHNIQUES USED
    CTE, window functions, DATEDIFF-based cohort bucketing,
    aggregation, pivoted grid via conditional aggregation.
    ============================================================
*/

WITH CustomerFirstOrder AS (
    SELECT
        dc.customer_unique_id,
        MIN(d.full_date) AS first_order_date
    FROM dbo.Fact_Order_Items foi
    JOIN dbo.Dim_Customer dc ON foi.customer_sk = dc.customer_sk
    JOIN dbo.Dim_Date d ON foi.order_purchase_date_sk = d.date_sk
    WHERE foi.order_status = 'delivered'
    GROUP BY dc.customer_unique_id
),
CustomerOrderMonths AS (
    SELECT DISTINCT
        dc.customer_unique_id,
        DATEFROMPARTS(d.year_number, d.month_number, 1) AS order_month
    FROM dbo.Fact_Order_Items foi
    JOIN dbo.Dim_Customer dc ON foi.customer_sk = dc.customer_sk
    JOIN dbo.Dim_Date d ON foi.order_purchase_date_sk = d.date_sk
    WHERE foi.order_status = 'delivered'
),
CohortActivity AS (
    SELECT
        cfo.customer_unique_id,
        DATEFROMPARTS(YEAR(cfo.first_order_date), MONTH(cfo.first_order_date), 1) AS cohort_month,
        DATEDIFF(MONTH,
            DATEFROMPARTS(YEAR(cfo.first_order_date), MONTH(cfo.first_order_date), 1),
            com.order_month
        ) AS month_offset
    FROM CustomerFirstOrder cfo
    JOIN CustomerOrderMonths com ON cfo.customer_unique_id = com.customer_unique_id
)
SELECT
    cohort_month,
    month_offset,
    COUNT(DISTINCT customer_unique_id) AS active_customers
INTO #CohortActivity2
FROM CohortActivity
GROUP BY cohort_month, month_offset;

-- ------------------------------------------------------------
-- *** THE RETENTION CURVE *** — blended across all cohorts,
-- restricted to month_offset values where at least 3 cohorts
-- had enough elapsed time to be observed at that offset (avoids
-- a curve that's misleadingly thin/noisy at the far right edge)
--
-- CORRECTION (post-Phase 9): the blended figure below is now a
-- SIZE-WEIGHTED average (SUM(active_customers) / SUM(cohort_size)
-- per month_offset), not a plain AVG() of each cohort's percentage.
-- The original unweighted AVG() let tiny early cohorts (e.g. a
-- single-customer December 2016 cohort scoring a lucky 100% at
-- month 1) count exactly as much as cohorts of 1,600+ customers,
-- which inflated the blended number well above what the underlying
-- customer population actually showed. This also explains the
-- earlier non-monotonic bumps in the curve (small-cohort noise).
-- The weighted version below matches the "Weighted Retention Rate %"
-- DAX measure in the Phase 9 Power BI model exactly, so the two
-- now reconcile.
-- ------------------------------------------------------------

WITH CohortSize AS (
    SELECT cohort_month, active_customers AS cohort_size
    FROM #CohortActivity2
    WHERE month_offset = 0
),
RetentionByCohort AS (
    SELECT
        ca.cohort_month,
        ca.month_offset,
        ca.active_customers,
        cs.cohort_size,
        ROUND(100.0 * ca.active_customers / cs.cohort_size, 2) AS retention_pct
    FROM #CohortActivity2 ca
    JOIN CohortSize cs ON ca.cohort_month = cs.cohort_month
),
ObservableOffsets AS (
    SELECT
        month_offset,
        COUNT(DISTINCT cohort_month) AS cohorts_observed
    FROM RetentionByCohort
    GROUP BY month_offset
)
SELECT
    rbc.month_offset,
    oo.cohorts_observed,
    ROUND(100.0 * SUM(rbc.active_customers) / SUM(rbc.cohort_size), 2) AS avg_retention_pct,
    MIN(rbc.retention_pct) AS min_retention_pct,
    MAX(rbc.retention_pct) AS max_retention_pct
FROM RetentionByCohort rbc
JOIN ObservableOffsets oo ON rbc.month_offset = oo.month_offset
WHERE oo.cohorts_observed >= 3 AND rbc.month_offset BETWEEN 0 AND 12
GROUP BY rbc.month_offset, oo.cohorts_observed
ORDER BY rbc.month_offset;

-- ------------------------------------------------------------
-- Month-over-month retention decline rate — where does the
-- curve fall fastest?
--
-- CORRECTION (post-Phase 9): same weighted-average fix as above,
-- for consistency — this feeds the LAG() decline calculation, so
-- it needs to be blended the same way as the headline curve.
-- ------------------------------------------------------------

WITH CohortSize AS (
    SELECT cohort_month, active_customers AS cohort_size
    FROM #CohortActivity2
    WHERE month_offset = 0
),
RetentionByCohort AS (
    SELECT
        ca.cohort_month,
        ca.month_offset,
        ca.active_customers,
        cs.cohort_size
    FROM #CohortActivity2 ca
    JOIN CohortSize cs ON ca.cohort_month = cs.cohort_month
),
BlendedCurve AS (
    SELECT
        month_offset,
        100.0 * SUM(active_customers) / SUM(cohort_size) AS avg_retention_pct
    FROM RetentionByCohort
    WHERE month_offset BETWEEN 0 AND 12
    GROUP BY month_offset
)
SELECT
    month_offset,
    ROUND(avg_retention_pct, 2) AS avg_retention_pct,
    ROUND(
        avg_retention_pct - LAG(avg_retention_pct) OVER (ORDER BY month_offset), 2
    ) AS change_vs_prior_month_pts
FROM BlendedCurve
ORDER BY month_offset;

DROP TABLE #CohortActivity2;

/*
    BUSINESS INTERPRETATION — fill in after running:
    - Describe the actual shape: is it a steep early cliff that
      flattens out, a gradual decline, or something else?
    - Where (which month_offset) does the biggest single drop occur?

    BUSINESS IMPLICATION — fill in after running:
    - The window during which a retention intervention (e.g.
      re-engagement campaign) would have the most impact, based on
      where the curve actually falls fastest
*/
