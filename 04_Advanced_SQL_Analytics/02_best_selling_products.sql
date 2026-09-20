/*
    ============================================================
    ORGEE — Phase 4: Advanced SQL Analytics
    02_best_selling_products.sql
    ============================================================

    BUSINESS QUESTION
    Which products sell the most by volume, and which generate the
    most revenue? Do the two rankings agree, or are there high-volume
    / low-revenue products (and vice versa) worth knowing about?

    TECHNIQUES USED
    CTE, window functions (RANK, ROW_NUMBER), aggregation, subquery.
    ============================================================
*/

-- ------------------------------------------------------------
-- Top 10 products by units sold
-- ------------------------------------------------------------

WITH ProductVolume AS (
    SELECT
        dp.product_id,
        dp.product_category_name_english,
        COUNT(*) AS units_sold,
        SUM(foi.price) AS total_revenue,
        RANK() OVER (ORDER BY COUNT(*) DESC) AS volume_rank
    FROM dbo.Fact_Order_Items foi
    JOIN dbo.Dim_Product dp ON foi.product_sk = dp.product_sk
    WHERE foi.order_status = 'delivered'
    GROUP BY dp.product_id, dp.product_category_name_english
)
SELECT TOP 10 *
FROM ProductVolume
ORDER BY volume_rank;

-- ------------------------------------------------------------
-- Top 10 products by revenue
-- ------------------------------------------------------------

WITH ProductRevenue AS (
    SELECT
        dp.product_id,
        dp.product_category_name_english,
        COUNT(*) AS units_sold,
        SUM(foi.price) AS total_revenue,
        RANK() OVER (ORDER BY SUM(foi.price) DESC) AS revenue_rank
    FROM dbo.Fact_Order_Items foi
    JOIN dbo.Dim_Product dp ON foi.product_sk = dp.product_sk
    WHERE foi.order_status = 'delivered'
    GROUP BY dp.product_id, dp.product_category_name_english
)
SELECT TOP 10 *
FROM ProductRevenue
ORDER BY revenue_rank;

-- ------------------------------------------------------------
-- Products that rank very differently on volume vs revenue
-- (e.g. top-20 by units but NOT top-100 by revenue — cheap,
-- high-frequency items — or the reverse: low volume, high revenue,
-- premium/niche items)
-- ------------------------------------------------------------

WITH ProductStats AS (
    SELECT
        dp.product_id,
        dp.product_category_name_english,
        COUNT(*) AS units_sold,
        SUM(foi.price) AS total_revenue,
        AVG(foi.price) AS avg_unit_price,
        RANK() OVER (ORDER BY COUNT(*) DESC) AS volume_rank,
        RANK() OVER (ORDER BY SUM(foi.price) DESC) AS revenue_rank
    FROM dbo.Fact_Order_Items foi
    JOIN dbo.Dim_Product dp ON foi.product_sk = dp.product_sk
    WHERE foi.order_status = 'delivered'
    GROUP BY dp.product_id, dp.product_category_name_english
)
SELECT TOP 20
    product_id, product_category_name_english,
    units_sold, total_revenue, avg_unit_price,
    volume_rank, revenue_rank,
    ABS(volume_rank - revenue_rank) AS rank_divergence
FROM ProductStats
WHERE volume_rank <= 100
ORDER BY rank_divergence DESC;

/*
    BUSINESS INTERPRETATION — fill in after running:
    - Do volume leaders and revenue leaders overlap, or are they
      different products entirely?
    - Which categories dominate the top-10 lists?

    BUSINESS IMPLICATION — fill in after running:
    - Pricing/bundling opportunities for high-volume/low-price items
    - Which products merit premium placement or marketing spend
*/
