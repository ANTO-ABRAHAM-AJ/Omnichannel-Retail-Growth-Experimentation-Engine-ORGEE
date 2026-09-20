/*
    ============================================================
    ORGEE — Phase 5: Customer Journey Analytics
    08_cohort_analysis.sql ⭐
    ============================================================

    BUSINESS QUESTION
    When customers are grouped by the month of their first
    purchase (their "cohort"), how many come back to purchase
    again in each subsequent month?

    DATA SOURCE — DELIBERATE CHOICE
    Built on Fact_Order_Items (real order data), NOT Fact_Sessions.
    Only ~18% of sessions ever resolve to a known customer, which
    would produce thin, noisy cohorts with almost no members past
    month 0. Fact_Order_Items has clean order dates across a real
    ~2-year span with every row resolved to a customer.

    GRAIN NOTE — SAME FIX AS PHASE 4
    Grouped by customer_unique_id (person-level), not customer_id
    (which is one-per-order in this dataset and would make cohort
    analysis meaningless — every "customer" would appear in exactly
    one month with no way to ever show retention).

    KNOWN CONTEXT FROM PHASE 4
    Only 3.00% of customers repeat-purchase at all. Expect a very
    steep cliff after month 0 — that is a real, expected pattern
    given that context, not a query error.

    TECHNIQUES USED
    CTE, window functions, DATEDIFF-based cohort bucketing,
    aggregation.
    ============================================================
*/

-- ------------------------------------------------------------
-- Assign each customer to a cohort (month of first delivered order)
-- ------------------------------------------------------------

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
    -- every distinct (customer, order month) they were active in
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
        com.order_month,
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
INTO #CohortActivity
FROM CohortActivity
GROUP BY cohort_month, month_offset;

-- ------------------------------------------------------------
-- Cohort retention table: cohort size (month 0) alongside each
-- subsequent month's active customer count and retention %
-- ------------------------------------------------------------

WITH CohortSize AS (
    SELECT cohort_month, active_customers AS cohort_size
    FROM #CohortActivity
    WHERE month_offset = 0
)
SELECT
    ca.cohort_month,
    cs.cohort_size,
    ca.month_offset,
    ca.active_customers,
    ROUND(100.0 * ca.active_customers / cs.cohort_size, 2) AS retention_pct
FROM #CohortActivity ca
JOIN CohortSize cs ON ca.cohort_month = cs.cohort_month
ORDER BY ca.cohort_month, ca.month_offset;

-- ------------------------------------------------------------
-- Cohort sizes — how many customers per acquisition month
-- (context for how much weight each cohort carries)
-- ------------------------------------------------------------

SELECT cohort_month, active_customers AS cohort_size
FROM #CohortActivity
WHERE month_offset = 0
ORDER BY cohort_month;

DROP TABLE #CohortActivity;

/*
    BUSINESS INTERPRETATION — fill in after running:
    - How steep is the month-0-to-month-1 drop specifically?
    - Do any cohorts retain meaningfully better than others?

    BUSINESS IMPLICATION — fill in after running:
    - Whether retention investment should focus on the immediate
      post-purchase window given how the curve actually looks
      (full curve shape explored in 09_retention_curves.sql)
*/
