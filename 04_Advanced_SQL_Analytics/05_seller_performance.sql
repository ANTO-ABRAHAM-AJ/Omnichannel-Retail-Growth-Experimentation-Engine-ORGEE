/*
    ============================================================
    ORGEE — Phase 4: Advanced SQL Analytics
    05_seller_performance.sql
    ============================================================

    BUSINESS QUESTION
    Which sellers drive the most revenue, and how concentrated is
    that revenue among a small group of top sellers? Does seller
    performance vary meaningfully by state?

    TECHNIQUES USED
    CTE, window functions (RANK, NTILE for seller tiers), aggregation,
    subquery.
    ============================================================
*/

-- ------------------------------------------------------------
-- Top 20 sellers by revenue
-- ------------------------------------------------------------

WITH SellerRevenue AS (
    SELECT
        ds.seller_id,
        ds.seller_state,
        COUNT(*) AS items_sold,
        SUM(foi.price) AS total_revenue,
        AVG(foi.price) AS avg_item_price
    FROM dbo.Fact_Order_Items foi
    JOIN dbo.Dim_Seller ds ON foi.seller_sk = ds.seller_sk
    WHERE foi.order_status = 'delivered'
    GROUP BY ds.seller_id, ds.seller_state
)
SELECT TOP 20
    seller_id, seller_state, items_sold, total_revenue, ROUND(avg_item_price, 2) AS avg_item_price,
    RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank
FROM SellerRevenue
ORDER BY revenue_rank;

-- ------------------------------------------------------------
-- Seller performance tiers (quartiles by revenue) and how much
-- of total revenue each tier controls
-- ------------------------------------------------------------

WITH SellerRevenue AS (
    SELECT
        ds.seller_id,
        SUM(foi.price) AS total_revenue
    FROM dbo.Fact_Order_Items foi
    JOIN dbo.Dim_Seller ds ON foi.seller_sk = ds.seller_sk
    WHERE foi.order_status = 'delivered'
    GROUP BY ds.seller_id
),
Tiered AS (
    SELECT
        seller_id,
        total_revenue,
        NTILE(4) OVER (ORDER BY total_revenue DESC) AS revenue_quartile
    FROM SellerRevenue
)
SELECT
    revenue_quartile,
    COUNT(*) AS seller_count,
    SUM(total_revenue) AS quartile_revenue,
    ROUND(100.0 * SUM(total_revenue) / SUM(SUM(total_revenue)) OVER (), 2) AS pct_of_total_revenue
FROM Tiered
GROUP BY revenue_quartile
ORDER BY revenue_quartile;

-- ------------------------------------------------------------
-- Revenue by seller state
-- ------------------------------------------------------------

SELECT
    ds.seller_state,
    COUNT(DISTINCT ds.seller_id) AS seller_count,
    SUM(foi.price) AS total_revenue,
    ROUND(SUM(foi.price) / COUNT(DISTINCT ds.seller_id), 2) AS avg_revenue_per_seller
FROM dbo.Fact_Order_Items foi
JOIN dbo.Dim_Seller ds ON foi.seller_sk = ds.seller_sk
WHERE foi.order_status = 'delivered'
GROUP BY ds.seller_state
ORDER BY total_revenue DESC;

/*
    BUSINESS INTERPRETATION — fill in after running:
    - How concentrated is revenue among top-quartile sellers?
    - Which states over/under-index on revenue per seller?

    BUSINESS IMPLICATION — fill in after running:
    - Retention priority for top-tier sellers
    - Whether geographic seller recruitment should target
      underrepresented, high-performing states
*/
