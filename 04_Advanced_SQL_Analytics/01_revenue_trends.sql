/*
    ============================================================
    ORGEE — Phase 4: Advanced SQL Analytics
    01_revenue_trends.sql
    ============================================================

    BUSINESS QUESTION
    How has revenue trended month over month, and which periods
    were strongest / weakest? Is growth accelerating or slowing?

    NOTES ON DATA
    order_status distribution in this dataset: delivered (96,478),
    shipped (1,107), canceled (625), unavailable (609), invoiced (314),
    processing (301), created (5), approved (2). Revenue is reported
    two ways below: "gross" (all order items regardless of status)
    and "completed" (delivered only) — canceled/unavailable orders
    never generated real revenue and would inflate a naive total.

    TECHNIQUES USED
    CTE, window functions (LAG for month-over-month growth),
    aggregation, CASE, date dimension join.
    ============================================================
*/

-- ------------------------------------------------------------
-- Monthly revenue trend (completed orders only) with MoM growth %
-- ------------------------------------------------------------

WITH MonthlyRevenue AS (
    SELECT
        d.year_number,
        d.month_number,
        d.month_name,
        SUM(CASE WHEN foi.order_status = 'delivered' THEN foi.price ELSE 0 END) AS completed_revenue,
        SUM(foi.price) AS gross_revenue,
        COUNT(DISTINCT foi.order_id) AS order_count
    FROM dbo.Fact_Order_Items foi
    JOIN dbo.Dim_Date d ON foi.order_purchase_date_sk = d.date_sk
    GROUP BY d.year_number, d.month_number, d.month_name
)
SELECT
    year_number,
    month_number,
    month_name,
    completed_revenue,
    gross_revenue,
    order_count,
    LAG(completed_revenue) OVER (ORDER BY year_number, month_number) AS prior_month_revenue,
    CASE
        WHEN LAG(completed_revenue) OVER (ORDER BY year_number, month_number) IS NULL THEN NULL
        WHEN LAG(completed_revenue) OVER (ORDER BY year_number, month_number) = 0 THEN NULL
        ELSE ROUND(
            100.0 * (completed_revenue - LAG(completed_revenue) OVER (ORDER BY year_number, month_number))
            / LAG(completed_revenue) OVER (ORDER BY year_number, month_number), 1
        )
    END AS mom_growth_pct
FROM MonthlyRevenue
ORDER BY year_number, month_number;

-- ------------------------------------------------------------
-- Revenue by order status — quantifies how much gross revenue
-- is "at risk" (canceled/unavailable) vs realized
-- ------------------------------------------------------------

SELECT
    order_status,
    COUNT(DISTINCT order_id) AS order_count,
    SUM(price) AS total_price_value,
    ROUND(100.0 * SUM(price) / SUM(SUM(price)) OVER (), 2) AS pct_of_gross_revenue
FROM dbo.Fact_Order_Items
GROUP BY order_status
ORDER BY total_price_value DESC;

-- ------------------------------------------------------------
-- Best and worst single month by completed revenue
-- ------------------------------------------------------------

WITH MonthlyRevenue AS (
    SELECT
        d.year_number, d.month_number, d.month_name,
        SUM(CASE WHEN foi.order_status = 'delivered' THEN foi.price ELSE 0 END) AS completed_revenue
    FROM dbo.Fact_Order_Items foi
    JOIN dbo.Dim_Date d ON foi.order_purchase_date_sk = d.date_sk
    GROUP BY d.year_number, d.month_number, d.month_name
),
Ranked AS (
    SELECT *,
        RANK() OVER (ORDER BY completed_revenue DESC) AS rank_high,
        RANK() OVER (ORDER BY completed_revenue ASC)  AS rank_low
    FROM MonthlyRevenue
)
SELECT year_number, month_number, month_name, completed_revenue, 'Highest' AS label
FROM Ranked WHERE rank_high = 1
UNION ALL
SELECT year_number, month_number, month_name, completed_revenue, 'Lowest' AS label
FROM Ranked WHERE rank_low = 1;

/*
    BUSINESS INTERPRETATION — fill in after running against the
    live warehouse (do not fabricate before seeing real numbers):
    - Overall trend direction (growing/flat/declining) and by how much
    - Any single month that stands out and a plausible explanation
    - Size of the gap between gross and completed revenue (cancellation impact)

    BUSINESS IMPLICATION — fill in after running:
    - What this suggests for forecasting, staffing, or inventory planning
*/
