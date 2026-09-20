/*
    ============================================================
    ORGEE — Phase 6: Customer & Product Analytics
    03_historical_clv.sql
    ============================================================

    BUSINESS QUESTION
    What is each customer actually worth, based on realized
    (historical) purchase value — and how is that value distributed
    and concentrated across segments?

    LOCKED METHODOLOGY
    Historical CLV = Total Completed Purchase Value per Customer
    during the observation period. This is realized historical
    value, NOT a predictive model — same SUM(price)-per-customer
    definition already used as "Monetary" in 01/02, now presented
    as the dedicated CLV analysis the plan calls for (distribution,
    percentiles, and segment cut — not a repeat of Phase 4's
    customer-revenue-contribution deciles, which used the same
    underlying number for a different purpose: overall concentration
    vs here, per-customer value distribution AND segment linkage).

    TECHNIQUES USED
    CTE, aggregation, PERCENTILE_CONT, NTILE, CASE.
    ============================================================
*/

IF OBJECT_ID('tempdb..#CLV') IS NOT NULL DROP TABLE #CLV;

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
        SUM(foi.price) AS historical_clv,
        DATEDIFF(DAY, MAX(d.full_date), (SELECT snapshot_date FROM SnapshotDate)) AS recency_days
    FROM dbo.Fact_Order_Items foi
    JOIN dbo.Dim_Customer dc ON foi.customer_sk = dc.customer_sk
    JOIN dbo.Dim_Date d ON foi.order_purchase_date_sk = d.date_sk
    WHERE foi.order_status = 'delivered'
    GROUP BY dc.customer_unique_id
),
CustomerRFMScored AS (
    SELECT
        customer_unique_id, recency_days, frequency, historical_clv,
        NTILE(5) OVER (ORDER BY recency_days DESC, customer_unique_id ASC) AS r_score,
        CASE
            WHEN frequency = 1 THEN 1
            WHEN frequency = 2 THEN 3
            WHEN frequency BETWEEN 3 AND 4 THEN 4
            WHEN frequency >= 5 THEN 5
        END AS f_score,
        NTILE(5) OVER (ORDER BY historical_clv ASC, customer_unique_id ASC) AS m_score
    FROM CustomerRFMBase
)
SELECT
    customer_unique_id, historical_clv, frequency, recency_days,
    CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
        WHEN f_score = 1 AND r_score >= 4 AND m_score >= 3 THEN 'Potential Loyalists'
        WHEN f_score = 1 AND r_score >= 4 AND m_score < 3 THEN 'New Customers'
        WHEN f_score >= 3 AND r_score <= 2 THEN 'At Risk'
        WHEN r_score <= 2 AND f_score = 1 AND m_score <= 2 THEN 'Lost Customers'
        ELSE 'Needs Attention'
    END AS segment
INTO #CLV
FROM CustomerRFMScored;

-- ------------------------------------------------------------
-- Overall CLV summary statistics
-- ------------------------------------------------------------

SELECT
    COUNT(*) AS total_customers,
    ROUND(SUM(historical_clv), 2) AS total_historical_value,
    ROUND(AVG(historical_clv), 2) AS avg_clv,
    (SELECT DISTINCT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY historical_clv) OVER () FROM #CLV) AS median_clv,
    ROUND(MIN(historical_clv), 2) AS min_clv,
    ROUND(MAX(historical_clv), 2) AS max_clv
FROM #CLV;

-- ------------------------------------------------------------
-- CLV distribution by decile (shape of the value distribution)
-- ------------------------------------------------------------

WITH Deciled AS (
    SELECT customer_unique_id, historical_clv,
        NTILE(10) OVER (ORDER BY historical_clv DESC, customer_unique_id ASC) AS clv_decile
    FROM #CLV
)
SELECT
    clv_decile,
    COUNT(*) AS customer_count,
    ROUND(SUM(historical_clv), 2) AS decile_total_value,
    ROUND(100.0 * SUM(historical_clv) / SUM(SUM(historical_clv)) OVER (), 2) AS pct_of_total_value,
    ROUND(MIN(historical_clv), 2) AS min_value_in_decile,
    ROUND(MAX(historical_clv), 2) AS max_value_in_decile
FROM Deciled
GROUP BY clv_decile
ORDER BY clv_decile;

-- ------------------------------------------------------------
-- *** CLV by RFM segment *** — the genuinely new Phase 6 cut
-- ------------------------------------------------------------

SELECT
    segment,
    COUNT(*) AS customer_count,
    ROUND(SUM(historical_clv), 2) AS segment_total_value,
    ROUND(AVG(historical_clv), 2) AS avg_clv,
    (SELECT DISTINCT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY historical_clv) OVER ()
     FROM #CLV c2 WHERE c2.segment = c1.segment) AS median_clv
FROM #CLV c1
GROUP BY segment
ORDER BY avg_clv DESC;

-- ------------------------------------------------------------
-- *** SIGNATURE-STYLE RATIO *** — Champions vs At-Risk avg CLV
-- ------------------------------------------------------------

SELECT
    (SELECT AVG(historical_clv) FROM #CLV WHERE segment = 'Champions') AS champions_avg_clv,
    (SELECT AVG(historical_clv) FROM #CLV WHERE segment = 'At Risk') AS at_risk_avg_clv,
    ROUND(
        (SELECT AVG(historical_clv) FROM #CLV WHERE segment = 'Champions')
        / NULLIF((SELECT AVG(historical_clv) FROM #CLV WHERE segment = 'At Risk'), 0), 2
    ) AS champions_to_at_risk_ratio;

DROP TABLE #CLV;

/*
    BUSINESS INTERPRETATION — fill in after running:
    - How skewed is customer value (compare mean vs median)?
    - The actual Champions-to-At-Risk value ratio, computed from
      real data (not assumed)

    BUSINESS IMPLICATION — fill in after running:
    - What the value concentration implies for where retention
      investment should concentrate
*/
