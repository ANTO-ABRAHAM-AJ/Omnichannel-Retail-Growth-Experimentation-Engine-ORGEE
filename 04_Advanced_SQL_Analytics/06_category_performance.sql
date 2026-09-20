/*
    ============================================================
    ORGEE — Phase 4: Advanced SQL Analytics
    06_category_performance.sql
    ============================================================

    BUSINESS QUESTION
    Which product categories generate the most revenue, and which
    have the best economics (highest average order value)? Are the
    "biggest" categories (by revenue) the same as the "best"
    categories (by AOV)?

    TECHNIQUES USED
    CTE, window functions (RANK), aggregation, CASE.
    ============================================================
*/

-- ------------------------------------------------------------
-- Category revenue ranking
-- ------------------------------------------------------------

WITH CategoryRevenue AS (
    SELECT
        dp.product_category_name_english,
        COUNT(*) AS items_sold,
        SUM(foi.price) AS total_revenue,
        AVG(foi.price) AS avg_item_price
    FROM dbo.Fact_Order_Items foi
    JOIN dbo.Dim_Product dp ON foi.product_sk = dp.product_sk
    WHERE foi.order_status = 'delivered'
      AND dp.product_category_name_english IS NOT NULL
    GROUP BY dp.product_category_name_english
)
SELECT TOP 15
    product_category_name_english, items_sold, total_revenue,
    ROUND(avg_item_price, 2) AS avg_item_price,
    RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank
FROM CategoryRevenue
ORDER BY revenue_rank;

-- ------------------------------------------------------------
-- Category revenue share and cumulative concentration
-- (what % of categories account for 80% of revenue?)
-- ------------------------------------------------------------

WITH CategoryRevenue AS (
    SELECT
        dp.product_category_name_english,
        SUM(foi.price) AS total_revenue
    FROM dbo.Fact_Order_Items foi
    JOIN dbo.Dim_Product dp ON foi.product_sk = dp.product_sk
    WHERE foi.order_status = 'delivered'
      AND dp.product_category_name_english IS NOT NULL
    GROUP BY dp.product_category_name_english
),
Ranked AS (
    SELECT
        product_category_name_english,
        total_revenue,
        RANK() OVER (ORDER BY total_revenue DESC) AS category_rank,
        SUM(total_revenue) OVER (ORDER BY total_revenue DESC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_revenue,
        SUM(total_revenue) OVER () AS grand_total_revenue
    FROM CategoryRevenue
)
SELECT
    category_rank,
    product_category_name_english,
    total_revenue,
    ROUND(100.0 * total_revenue / grand_total_revenue, 2) AS pct_of_total,
    ROUND(100.0 * running_revenue / grand_total_revenue, 2) AS cumulative_pct
FROM Ranked
ORDER BY category_rank;

-- ------------------------------------------------------------
-- High-AOV categories that AREN'T in the top-10 by total revenue
-- (small but valuable categories worth more marketing attention)
-- ------------------------------------------------------------

WITH CategoryStats AS (
    SELECT
        dp.product_category_name_english,
        COUNT(*) AS items_sold,
        SUM(foi.price) AS total_revenue,
        AVG(foi.price) AS avg_item_price,
        RANK() OVER (ORDER BY SUM(foi.price) DESC) AS revenue_rank,
        RANK() OVER (ORDER BY AVG(foi.price) DESC) AS aov_rank
    FROM dbo.Fact_Order_Items foi
    JOIN dbo.Dim_Product dp ON foi.product_sk = dp.product_sk
    WHERE foi.order_status = 'delivered'
      AND dp.product_category_name_english IS NOT NULL
    GROUP BY dp.product_category_name_english
    HAVING COUNT(*) >= 20
)
SELECT
    product_category_name_english, items_sold, total_revenue,
    ROUND(avg_item_price, 2) AS avg_item_price, revenue_rank, aov_rank
FROM CategoryStats
WHERE aov_rank <= 10 AND revenue_rank > 10
ORDER BY aov_rank;

/*
    BUSINESS INTERPRETATION — fill in after running:
    - How many categories drive 80% of revenue (Pareto check)?
    - Which high-value-but-low-volume categories are underexposed?

    BUSINESS IMPLICATION — fill in after running:
    - Category-level marketing/inventory investment priorities
*/
