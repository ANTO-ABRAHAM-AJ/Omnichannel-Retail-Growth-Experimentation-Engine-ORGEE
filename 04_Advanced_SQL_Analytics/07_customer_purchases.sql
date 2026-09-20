/*
    ============================================================
    ORGEE — Phase 4: Advanced SQL Analytics
    07_customer_purchases.sql
    ============================================================

    BUSINESS QUESTION
    How often do customers actually purchase — is this a
    predominantly one-time-buyer business, or is there a meaningful
    repeat-purchase base?

    CRITICAL DATA NOTE
    Dim_Customer.customer_id is essentially one-per-order in the
    Olist dataset — all 99,441 customer_id values are unique, so
    grouping by customer_id would show a false 0% repeat-purchase
    rate for every customer. The real person-level identifier is
    customer_unique_id (96,096 distinct people; verified 2,997 of
    them placed more than one order). Every query below groups by
    customer_unique_id, not customer_id.

    TECHNIQUES USED
    CTE, CASE (purchase-frequency buckets), aggregation, window
    functions.
    ============================================================
*/

-- ------------------------------------------------------------
-- Orders per unique customer — overall distribution
-- ------------------------------------------------------------

WITH CustomerOrders AS (
    SELECT
        dc.customer_unique_id,
        COUNT(DISTINCT foi.order_id) AS order_count
    FROM dbo.Fact_Order_Items foi
    JOIN dbo.Dim_Customer dc ON foi.customer_sk = dc.customer_sk
    WHERE foi.order_status = 'delivered'
    GROUP BY dc.customer_unique_id
)
SELECT
    CASE
        WHEN order_count = 1 THEN '1. One-time buyer'
        WHEN order_count = 2 THEN '2. Two orders'
        WHEN order_count BETWEEN 3 AND 5 THEN '3. Three to five orders'
        ELSE '4. Six or more orders'
    END AS purchase_frequency_bucket,
    COUNT(*) AS customer_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_customers
FROM CustomerOrders
GROUP BY
    CASE
        WHEN order_count = 1 THEN '1. One-time buyer'
        WHEN order_count = 2 THEN '2. Two orders'
        WHEN order_count BETWEEN 3 AND 5 THEN '3. Three to five orders'
        ELSE '4. Six or more orders'
    END
ORDER BY purchase_frequency_bucket;

-- ------------------------------------------------------------
-- Overall repeat-purchase rate (single headline number)
-- ------------------------------------------------------------

WITH CustomerOrders AS (
    SELECT
        dc.customer_unique_id,
        COUNT(DISTINCT foi.order_id) AS order_count
    FROM dbo.Fact_Order_Items foi
    JOIN dbo.Dim_Customer dc ON foi.customer_sk = dc.customer_sk
    WHERE foi.order_status = 'delivered'
    GROUP BY dc.customer_unique_id
)
SELECT
    COUNT(*) AS total_unique_customers,
    SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) AS repeat_customers,
    ROUND(
        100.0 * SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) / COUNT(*), 2
    ) AS repeat_purchase_rate_pct
FROM CustomerOrders;

-- ------------------------------------------------------------
-- Time between first and second order, for customers who did
-- come back (days) — how quickly do repeat customers return?
-- ------------------------------------------------------------

WITH CustomerOrderDates AS (
    SELECT
        dc.customer_unique_id,
        d.full_date AS order_date,
        ROW_NUMBER() OVER (
            PARTITION BY dc.customer_unique_id ORDER BY d.full_date
        ) AS order_sequence
    FROM dbo.Fact_Order_Items foi
    JOIN dbo.Dim_Customer dc ON foi.customer_sk = dc.customer_sk
    JOIN dbo.Dim_Date d ON foi.order_purchase_date_sk = d.date_sk
    WHERE foi.order_status = 'delivered'
    GROUP BY dc.customer_unique_id, d.full_date
),
FirstSecond AS (
    SELECT
        customer_unique_id,
        MAX(CASE WHEN order_sequence = 1 THEN order_date END) AS first_order_date,
        MAX(CASE WHEN order_sequence = 2 THEN order_date END) AS second_order_date
    FROM CustomerOrderDates
    WHERE order_sequence IN (1, 2)
    GROUP BY customer_unique_id
    HAVING COUNT(*) = 2
)
SELECT
    COUNT(*) AS repeat_customers_with_2plus_orders,
    AVG(DATEDIFF(DAY, first_order_date, second_order_date)) AS avg_days_to_second_order,
    MIN(DATEDIFF(DAY, first_order_date, second_order_date)) AS min_days,
    MAX(DATEDIFF(DAY, first_order_date, second_order_date)) AS max_days
FROM FirstSecond;

/*
    BUSINESS INTERPRETATION — fill in after running:
    - The actual repeat-purchase rate, and how it compares to
      typical e-commerce benchmarks
    - How long repeat customers take to come back

    BUSINESS IMPLICATION — fill in after running:
    - Whether retention/re-engagement investment is warranted given
      how small (or large) the repeat base actually is
*/
