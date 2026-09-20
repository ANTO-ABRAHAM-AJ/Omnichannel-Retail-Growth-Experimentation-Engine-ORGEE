/*
    ============================================================
    ORGEE — Phase 6: Customer & Product Analytics
    05_north_star_metric.sql
    ============================================================

    NORTH STAR METRIC DEFINITION

    Metric: Monthly Delivered Revenue per Active Customer

    Definition: Total delivered order revenue in a given month,
    divided by the count of distinct customers (customer_unique_id)
    who placed at least one delivered order that month.

    Calculation: SUM(price) for delivered orders in month M,
    divided by COUNT(DISTINCT customer_unique_id) with a delivered
    order in month M.

    Grain: One row per calendar month.

    WHY THIS METRIC (not just total revenue, not just customer count):
    Total revenue alone rewards pure volume growth and can mask a
    declining per-customer relationship (more customers spending
    less each). Customer count alone ignores value. Given what
    Phases 4-5 already established about this business — a 9.48%
    funnel conversion rate and a 97% one-time-buyer base — the real
    lever for growth here is less about acquiring more first-time
    browsers and more about extracting more value per customer who
    actually converts. Revenue per Active Customer is the single
    number that moves when EITHER conversion improves (more active
    customers) OR basket/pricing improves (more revenue per active
    customer) OR retention improves (repeat customers add revenue
    without adding new "customer" count) — it connects Customer
    Experience → Conversion → Retention → Revenue → Growth in one
    metric, as the plan requires.

    SUPPORTING METRICS (already computed in earlier phases, restated
    here as the metrics that move the North Star):
    - Funnel conversion rate (Phase 5): 9.48%
    - Repeat purchase rate (Phase 4): 3.00%
    - Average order value (Phase 4 context)
    - Revenue concentration: top 10% of customers = 41.14% of
      revenue (Phase 4)

    TECHNIQUES USED
    CTE, aggregation, window functions (LAG for trend), date logic.
    ============================================================
*/

-- ------------------------------------------------------------
-- North Star Metric — monthly trend
-- ------------------------------------------------------------

WITH MonthlyActive AS (
    SELECT
        d.year_number,
        d.month_number,
        d.month_name,
        SUM(foi.price) AS monthly_revenue,
        COUNT(DISTINCT dc.customer_unique_id) AS active_customers
    FROM dbo.Fact_Order_Items foi
    JOIN dbo.Dim_Customer dc ON foi.customer_sk = dc.customer_sk
    JOIN dbo.Dim_Date d ON foi.order_purchase_date_sk = d.date_sk
    WHERE foi.order_status = 'delivered'
    GROUP BY d.year_number, d.month_number, d.month_name
)
SELECT
    year_number, month_number, month_name,
    monthly_revenue, active_customers,
    ROUND(monthly_revenue / NULLIF(active_customers, 0), 2) AS north_star_revenue_per_active_customer,
    ROUND(
        (monthly_revenue / NULLIF(active_customers, 0))
        - LAG(monthly_revenue / NULLIF(active_customers, 0)) OVER (ORDER BY year_number, month_number),
        2
    ) AS change_vs_prior_month
FROM MonthlyActive
ORDER BY year_number, month_number;

-- ------------------------------------------------------------
-- North Star Metric — overall (whole observation period)
-- ------------------------------------------------------------

SELECT
    ROUND(SUM(foi.price), 2) AS total_delivered_revenue,
    COUNT(DISTINCT dc.customer_unique_id) AS total_active_customers,
    ROUND(SUM(foi.price) / COUNT(DISTINCT dc.customer_unique_id), 2) AS overall_revenue_per_active_customer
FROM dbo.Fact_Order_Items foi
JOIN dbo.Dim_Customer dc ON foi.customer_sk = dc.customer_sk
WHERE foi.order_status = 'delivered';

/*
    BUSINESS INTERPRETATION — fill in after running:
    - Is the North Star trending up, flat, or down over the
      observation period?
    - How much does it fluctuate month to month, and is that
      fluctuation seasonal or noise (small monthly customer counts)?

    BUSINESS IMPLICATION — fill in after running:
    - Which lever (conversion, AOV, or retention) would move this
      metric the most, given the supporting metrics already known
*/
