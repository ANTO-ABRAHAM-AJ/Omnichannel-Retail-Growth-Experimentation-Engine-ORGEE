/*
    ============================================================
    ORGEE — Phase 6: Customer & Product Analytics
    06_kpi_tree.sql ⭐
    ============================================================

    BUSINESS QUESTION
    What does the full KPI hierarchy look like, with actual current
    values at every level — from the North Star down to the raw
    funnel stages that drive it?

    KPI TREE STRUCTURE (values populated by the queries below):

                        NORTH STAR
              Revenue per Active Customer
                         |
              ------------------------
              |                      |
          Customers               Revenue
        (active count)         (total delivered)
              |                      |
        ---------------        --------------
        |             |        |            |
    Acquisition   Retention   AOV      Purchases
    (new/month)  (repeat %)  (avg $)   (order count)
        |
    Conversion Rate (Phase 5 funnel)
        |
    Visit -> View -> Cart -> Checkout -> Purchase

    This script queries every node's actual current value in one
    place — a single "KPI dashboard" result set per branch. It
    intentionally reuses (not recomputes independently from raw
    events) the funnel and retention numbers already validated in
    Phase 5, per the "build on Phase 4-5" instruction.

    FIX APPLIED POST-REVIEW: the tree diagram above always listed
    "Acquisition" as a Level 3 sibling of Retention, but the
    original query set only implemented Retention/AOV/Purchases —
    Acquisition was documented, never queried. Added below as
    "Avg New Customers per Month" (mean count of customers making
    their first delivered purchase, grouped by that first-purchase
    month) — the natural acquisition-rate counterpart to
    Retention's "Repeat Purchase Rate %".

    TECHNIQUES USED
    CTE, aggregation, UNION ALL for a single flat KPI table.
    ============================================================
*/

-- ------------------------------------------------------------
-- Level 1: North Star
-- ------------------------------------------------------------

SELECT
    'L1 - North Star' AS kpi_level,
    'Revenue per Active Customer' AS kpi_name,
    CAST(ROUND(SUM(foi.price) / COUNT(DISTINCT dc.customer_unique_id), 2) AS VARCHAR(20)) AS kpi_value
FROM dbo.Fact_Order_Items foi
JOIN dbo.Dim_Customer dc ON foi.customer_sk = dc.customer_sk
WHERE foi.order_status = 'delivered'

UNION ALL

-- ------------------------------------------------------------
-- Level 2: Customers and Revenue
-- ------------------------------------------------------------

SELECT 'L2 - Customers', 'Total Active Customers',
    CAST(COUNT(DISTINCT dc.customer_unique_id) AS VARCHAR(20))
FROM dbo.Fact_Order_Items foi
JOIN dbo.Dim_Customer dc ON foi.customer_sk = dc.customer_sk
WHERE foi.order_status = 'delivered'

UNION ALL

SELECT 'L2 - Revenue', 'Total Delivered Revenue',
    CAST(ROUND(SUM(price), 2) AS VARCHAR(20))
FROM dbo.Fact_Order_Items
WHERE order_status = 'delivered'

UNION ALL

-- ------------------------------------------------------------
-- Level 3: Acquisition, Retention, AOV, Purchases
-- ------------------------------------------------------------

SELECT 'L3 - Acquisition', 'Avg New Customers per Month',
    CAST(ROUND(AVG(new_customers * 1.0), 1) AS VARCHAR(20))
FROM (
    SELECT
        first_order_month,
        COUNT(*) AS new_customers
    FROM (
        SELECT
            dc.customer_unique_id,
            MIN(DATEFROMPARTS(d.year_number, d.month_number, 1)) AS first_order_month
        FROM dbo.Fact_Order_Items foi
        JOIN dbo.Dim_Customer dc ON foi.customer_sk = dc.customer_sk
        JOIN dbo.Dim_Date d ON foi.order_purchase_date_sk = d.date_sk
        WHERE foi.order_status = 'delivered'
        GROUP BY dc.customer_unique_id
    ) first_orders
    GROUP BY first_order_month
) monthly_new

UNION ALL

SELECT 'L3 - Retention', 'Repeat Purchase Rate %',
    CAST(ROUND(
        100.0 * SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) / COUNT(*), 2
    ) AS VARCHAR(20))
FROM (
    SELECT dc.customer_unique_id, COUNT(DISTINCT foi.order_id) AS order_count
    FROM dbo.Fact_Order_Items foi
    JOIN dbo.Dim_Customer dc ON foi.customer_sk = dc.customer_sk
    WHERE foi.order_status = 'delivered'
    GROUP BY dc.customer_unique_id
) x

UNION ALL

SELECT 'L3 - AOV', 'Average Order Value',
    CAST(ROUND(SUM(price) / COUNT(DISTINCT order_id), 2) AS VARCHAR(20))
FROM dbo.Fact_Order_Items
WHERE order_status = 'delivered'

UNION ALL

SELECT 'L3 - Purchases', 'Total Delivered Orders',
    CAST(COUNT(DISTINCT order_id) AS VARCHAR(20))
FROM dbo.Fact_Order_Items
WHERE order_status = 'delivered'

UNION ALL

-- ------------------------------------------------------------
-- Level 4: Conversion (from Phase 5, restated here as a KPI node)
-- ------------------------------------------------------------

SELECT 'L4 - Conversion', 'Visit-to-Purchase Conversion Rate %',
    CAST(ROUND(
        100.0 * (SELECT COUNT(DISTINCT session_id) FROM dbo.Fact_Events WHERE event_type = 'purchase_interaction')
        / NULLIF((SELECT COUNT(DISTINCT session_id) FROM dbo.Fact_Events WHERE event_type = 'session_start'), 0), 2
    ) AS VARCHAR(20))

UNION ALL

-- ------------------------------------------------------------
-- Level 5: Raw funnel stages (from Phase 5)
-- ------------------------------------------------------------

SELECT 'L5 - Funnel', 'Visit', CAST(COUNT(DISTINCT session_id) AS VARCHAR(20))
FROM dbo.Fact_Events WHERE event_type = 'session_start'

UNION ALL

SELECT 'L5 - Funnel', 'Product View', CAST(COUNT(DISTINCT session_id) AS VARCHAR(20))
FROM dbo.Fact_Events WHERE event_type = 'product_view'

UNION ALL

SELECT 'L5 - Funnel', 'Add to Cart', CAST(COUNT(DISTINCT session_id) AS VARCHAR(20))
FROM dbo.Fact_Events WHERE event_type = 'add_to_cart'

UNION ALL

SELECT 'L5 - Funnel', 'Checkout', CAST(COUNT(DISTINCT session_id) AS VARCHAR(20))
FROM dbo.Fact_Events WHERE event_type = 'checkout_start'

UNION ALL

SELECT 'L5 - Funnel', 'Purchase', CAST(COUNT(DISTINCT session_id) AS VARCHAR(20))
FROM dbo.Fact_Events WHERE event_type = 'purchase_interaction';

/*
    BUSINESS INTERPRETATION — fill in after running:
    - Walk the tree top to bottom: does the North Star's current
      value make sense given the L2-L5 values feeding it?

    BUSINESS IMPLICATION — fill in after running:
    - Which single node, if improved, would move the North Star
      the most (this directly feeds 08_feature_prioritization.sql)
*/
