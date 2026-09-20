/*
    ============================================================
    ORGEE — Phase 4: Advanced SQL Analytics
    08_customer_revenue_contribution.sql
    ============================================================

    BUSINESS QUESTION
    How concentrated is revenue among top customers? What share of
    total revenue comes from the top 10% / 20% of customers?

    This is the primary candidate for Phase 4's required Signature
    Insight — the actual percentages below are computed directly
    from the warehouse, not assumed or predetermined.

    CRITICAL DATA NOTE
    Same fix as 07_customer_purchases.sql — grouped by
    customer_unique_id (the real person-level identifier), never by
    customer_id (which is one-per-order in this dataset and would
    make every "customer" contribute identically, hiding any real
    concentration pattern).

    TECHNIQUES USED
    CTE, window functions (NTILE, cumulative SUM), aggregation,
    ranking.
    ============================================================
*/

-- ------------------------------------------------------------
-- Revenue per unique customer, ranked
-- ------------------------------------------------------------

WITH CustomerRevenue AS (
    SELECT
        dc.customer_unique_id,
        SUM(foi.price) AS total_revenue,
        COUNT(DISTINCT foi.order_id) AS order_count
    FROM dbo.Fact_Order_Items foi
    JOIN dbo.Dim_Customer dc ON foi.customer_sk = dc.customer_sk
    WHERE foi.order_status = 'delivered'
    GROUP BY dc.customer_unique_id
)
SELECT TOP 20
    customer_unique_id, total_revenue, order_count,
    RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank
FROM CustomerRevenue
ORDER BY revenue_rank;

-- ------------------------------------------------------------
-- *** SIGNATURE INSIGHT QUERY ***
-- Revenue decile breakdown: what % of total revenue does each
-- 10%-of-customers decile contribute? (NTILE 10 = deciles)
-- ------------------------------------------------------------

WITH CustomerRevenue AS (
    SELECT
        dc.customer_unique_id,
        SUM(foi.price) AS total_revenue
    FROM dbo.Fact_Order_Items foi
    JOIN dbo.Dim_Customer dc ON foi.customer_sk = dc.customer_sk
    WHERE foi.order_status = 'delivered'
    GROUP BY dc.customer_unique_id
),
Deciled AS (
    SELECT
        customer_unique_id,
        total_revenue,
        NTILE(10) OVER (ORDER BY total_revenue DESC) AS revenue_decile
    FROM CustomerRevenue
)
SELECT
    revenue_decile,
    COUNT(*) AS customer_count,
    SUM(total_revenue) AS decile_revenue,
    ROUND(100.0 * SUM(total_revenue) / SUM(SUM(total_revenue)) OVER (), 2) AS pct_of_total_revenue,
    ROUND(
        100.0 * SUM(SUM(total_revenue)) OVER (ORDER BY revenue_decile
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
        / SUM(SUM(total_revenue)) OVER (), 2
    ) AS cumulative_pct_of_revenue
FROM Deciled
GROUP BY revenue_decile
ORDER BY revenue_decile;

-- ------------------------------------------------------------
-- Precise top-10% / top-20% headline figures
-- (the exact numbers the signature insight will quote)
-- ------------------------------------------------------------

WITH CustomerRevenue AS (
    SELECT
        dc.customer_unique_id,
        SUM(foi.price) AS total_revenue
    FROM dbo.Fact_Order_Items foi
    JOIN dbo.Dim_Customer dc ON foi.customer_sk = dc.customer_sk
    WHERE foi.order_status = 'delivered'
    GROUP BY dc.customer_unique_id
),
Ranked AS (
    SELECT
        customer_unique_id,
        total_revenue,
        PERCENT_RANK() OVER (ORDER BY total_revenue DESC) AS pct_rank,
        SUM(total_revenue) OVER () AS grand_total
    FROM CustomerRevenue
)
SELECT
    'Top 10% of customers' AS segment,
    COUNT(*) AS customer_count,
    SUM(total_revenue) AS segment_revenue,
    ROUND(100.0 * SUM(total_revenue) / MAX(grand_total), 2) AS pct_of_total_revenue
FROM Ranked WHERE pct_rank <= 0.10
UNION ALL
SELECT
    'Top 20% of customers',
    COUNT(*),
    SUM(total_revenue),
    ROUND(100.0 * SUM(total_revenue) / MAX(grand_total), 2)
FROM Ranked WHERE pct_rank <= 0.20;

/*
    SIGNATURE INSIGHT — fill in with the ACTUAL numbers returned
    above once run against the live warehouse. Format only
    (per Phase 4 requirements, do not predetermine or fabricate):

        "The top X% of customers generate Y% of total revenue."

    BUSINESS IMPLICATION — fill in after running:
    - What this concentration level implies for retention priority
      vs broad acquisition spend
*/
