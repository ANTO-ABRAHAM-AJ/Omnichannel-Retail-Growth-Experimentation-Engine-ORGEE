/*
    ============================================================
    ORGEE — Phase 4: Advanced SQL Analytics
    04_inventory_health.sql
    ============================================================

    BUSINESS QUESTION
    What does the overall inventory health picture look like, and
    which specific products are at the greatest stockout risk?

    NOTE ON DATA
    inventory_status in this dataset is heavily skewed toward
    in_stock (~99.4%), with low_stock (~0.64%) and genuine
    out_of_stock events being rare (~0.003%, roughly 28 of
    1,000,000 observations). Because true stockouts are so rare,
    this analysis treats low_stock as the primary leading indicator
    of risk rather than relying on out_of_stock alone, which is too
    sparse to rank meaningfully on its own.

    TECHNIQUES USED
    CTE, CASE, window functions (ranking), aggregation, subquery,
    date analysis (most recent observation per product).
    ============================================================
*/

-- ------------------------------------------------------------
-- Overall inventory status distribution
-- ------------------------------------------------------------

SELECT
    inventory_status,
    COUNT(*) AS observation_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 4) AS pct_of_observations
FROM dbo.Fact_Inventory_Snapshot
GROUP BY inventory_status
ORDER BY observation_count DESC;

-- ------------------------------------------------------------
-- Products with the highest count of low_stock / out_of_stock
-- observations (repeated risk signal, not a one-off blip)
-- ------------------------------------------------------------

WITH RiskEvents AS (
    SELECT
        fis.product_sk,
        dp.product_id,
        dp.product_category_name_english,
        SUM(CASE WHEN fis.inventory_status = 'low_stock' THEN 1 ELSE 0 END)     AS low_stock_events,
        SUM(CASE WHEN fis.inventory_status = 'out_of_stock' THEN 1 ELSE 0 END)  AS out_of_stock_events,
        COUNT(*) AS total_observations
    FROM dbo.Fact_Inventory_Snapshot fis
    JOIN dbo.Dim_Product dp ON fis.product_sk = dp.product_sk
    GROUP BY fis.product_sk, dp.product_id, dp.product_category_name_english
)
SELECT TOP 20
    product_id, product_category_name_english,
    low_stock_events, out_of_stock_events, total_observations,
    RANK() OVER (
        ORDER BY (low_stock_events + out_of_stock_events * 10) DESC
        -- out_of_stock weighted 10x heavier than low_stock — an
        -- actual stockout is a materially worse outcome than a
        -- low-stock warning
    ) AS risk_rank
FROM RiskEvents
WHERE low_stock_events > 0 OR out_of_stock_events > 0
ORDER BY risk_rank;

-- ------------------------------------------------------------
-- Current (most recent) status per product — a snapshot of
-- today's risk, not historical frequency
-- ------------------------------------------------------------

WITH LatestObservation AS (
    SELECT
        fis.product_sk,
        fis.inventory_status,
        fis.available_quantity,
        fis.observation_timestamp,
        ROW_NUMBER() OVER (
            PARTITION BY fis.product_sk
            ORDER BY fis.observation_timestamp DESC
        ) AS rn
    FROM dbo.Fact_Inventory_Snapshot fis
)
SELECT
    lo.inventory_status,
    COUNT(*) AS product_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_products
FROM LatestObservation lo
WHERE lo.rn = 1
GROUP BY lo.inventory_status
ORDER BY product_count DESC;

/*
    BUSINESS INTERPRETATION — fill in after running:
    - How healthy does inventory look overall, and is that
      consistent between the historical-frequency view and the
      current-snapshot view?
    - Which specific products/categories carry the most risk?

    BUSINESS IMPLICATION — fill in after running:
    - Reorder-point recommendations for the highest-risk products
    - Whether risk concentrates in specific categories worth a
      supplier-diversification conversation
*/
