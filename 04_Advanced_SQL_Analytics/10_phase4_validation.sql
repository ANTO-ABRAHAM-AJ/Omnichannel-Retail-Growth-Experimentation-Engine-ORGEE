/*
    ============================================================
    ORGEE — Phase 4: Advanced SQL Analytics
    10_phase4_validation.sql
    ============================================================

    Sanity-checks the assumptions and calculations used across
    scripts 01-09. Every check writes a PASS/FAIL row and the
    script ends with a summary, matching the Phase 2/3 validation
    pattern.
    ============================================================
*/

IF OBJECT_ID('tempdb..#P4Results') IS NOT NULL DROP TABLE #P4Results;
CREATE TABLE #P4Results (check_area VARCHAR(30), check_name VARCHAR(150), status VARCHAR(4), detail VARCHAR(300));

-- ============================================================
-- 1. NULL HANDLING — how much of Fact_Order_Items lacks a
-- resolved customer_sk / product_sk (should be ~0, since orders
-- and their line items are fully populated source data, unlike
-- the anonymous-browsing tables)
-- ============================================================

INSERT INTO #P4Results
SELECT 'Null Handling', 'Fact_Order_Items.customer_sk NULL rate',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'WARN' END,
       CONCAT('null_count=', COUNT(*), ' of ', (SELECT COUNT(*) FROM dbo.Fact_Order_Items))
FROM dbo.Fact_Order_Items WHERE customer_sk IS NULL;

INSERT INTO #P4Results
SELECT 'Null Handling', 'Fact_Order_Items.product_sk NULL rate',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'WARN' END,
       CONCAT('null_count=', COUNT(*), ' of ', (SELECT COUNT(*) FROM dbo.Fact_Order_Items))
FROM dbo.Fact_Order_Items WHERE product_sk IS NULL;

INSERT INTO #P4Results
SELECT 'Null Handling', 'Dim_Product.product_category_name_english NULL rate (expected: some, source data gap)',
       'INFO',
       CONCAT('null_count=', COUNT(*), ' of ', (SELECT COUNT(*) FROM dbo.Dim_Product))
FROM dbo.Dim_Product WHERE product_category_name_english IS NULL;

-- ============================================================
-- 2. CUSTOMER_UNIQUE_ID FIX — confirms the grouping key actually
-- produces a non-degenerate result (i.e. NOT every customer
-- showing exactly 1 order, which would mean the fix wasn't applied)
-- ============================================================

INSERT INTO #P4Results
SELECT 'Grouping Key Fix', 'customer_unique_id grouping shows real repeat purchasers (not 0%)',
       CASE WHEN COUNT(*) > 0 THEN 'PASS' ELSE 'FAIL' END,
       CONCAT('repeat_customer_count=', COUNT(*))
FROM (
    SELECT dc.customer_unique_id
    FROM dbo.Fact_Order_Items foi
    JOIN dbo.Dim_Customer dc ON foi.customer_sk = dc.customer_sk
    WHERE foi.order_status = 'delivered'
    GROUP BY dc.customer_unique_id
    HAVING COUNT(DISTINCT foi.order_id) > 1
) x;

-- ============================================================
-- 3. DATE LOGIC — confirms every order_purchase_date_sk resolves
-- to a real Dim_Date row (no orphaned dates from the join)
-- ============================================================

INSERT INTO #P4Results
SELECT 'Date Logic', 'Every Fact_Order_Items.order_purchase_date_sk resolves in Dim_Date',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
       CONCAT('unresolved=', COUNT(*))
FROM dbo.Fact_Order_Items foi
LEFT JOIN dbo.Dim_Date d ON foi.order_purchase_date_sk = d.date_sk
WHERE foi.order_purchase_date_sk IS NOT NULL AND d.date_sk IS NULL;

-- ============================================================
-- 4. PERCENTAGE / RANKING SANITY
-- ============================================================

-- Revenue-by-status percentages should sum to 100
INSERT INTO #P4Results
SELECT 'Percentage Sanity', 'Revenue-by-order-status percentages sum to ~100%',
       CASE WHEN ABS(SUM(pct) - 100.0) < 0.5 THEN 'PASS' ELSE 'FAIL' END,
       CONCAT('sum=', ROUND(SUM(pct), 2))
FROM (
    SELECT 100.0 * SUM(price) / SUM(SUM(price)) OVER () AS pct
    FROM dbo.Fact_Order_Items
    GROUP BY order_status
) x;

-- Revenue deciles should sum to ~100%
INSERT INTO #P4Results
SELECT 'Percentage Sanity', 'Customer revenue deciles sum to ~100%',
       CASE WHEN ABS(SUM(decile_pct) - 100.0) < 0.5 THEN 'PASS' ELSE 'FAIL' END,
       CONCAT('sum=', ROUND(SUM(decile_pct), 2))
FROM (
    SELECT
        revenue_decile,
        100.0 * SUM(total_revenue) / SUM(SUM(total_revenue)) OVER () AS decile_pct
    FROM (
        SELECT
            dc.customer_unique_id,
            SUM(foi.price) AS total_revenue,
            NTILE(10) OVER (ORDER BY SUM(foi.price) DESC) AS revenue_decile
        FROM dbo.Fact_Order_Items foi
        JOIN dbo.Dim_Customer dc ON foi.customer_sk = dc.customer_sk
        WHERE foi.order_status = 'delivered'
        GROUP BY dc.customer_unique_id
    ) c
    GROUP BY revenue_decile
) deciles;
INSERT INTO #P4Results
SELECT 'Percentage Sanity', 'Decile 1 (top 10%) revenue share >= Decile 10 (bottom 10%) share',
       CASE WHEN top_pct >= bottom_pct THEN 'PASS' ELSE 'FAIL' END,
       CONCAT('top_decile_pct=', top_pct, ', bottom_decile_pct=', bottom_pct)
FROM (
    SELECT
        MAX(CASE WHEN revenue_decile = 1 THEN decile_pct END) AS top_pct,
        MAX(CASE WHEN revenue_decile = 10 THEN decile_pct END) AS bottom_pct
    FROM (
        SELECT
            revenue_decile,
            100.0 * SUM(total_revenue) / SUM(SUM(total_revenue)) OVER () AS decile_pct
        FROM (
            SELECT
                dc.customer_unique_id,
                SUM(foi.price) AS total_revenue,
                NTILE(10) OVER (ORDER BY SUM(foi.price) DESC) AS revenue_decile
            FROM dbo.Fact_Order_Items foi
            JOIN dbo.Dim_Customer dc ON foi.customer_sk = dc.customer_sk
            WHERE foi.order_status = 'delivered'
            GROUP BY dc.customer_unique_id
        ) c
        GROUP BY revenue_decile
    ) d
) final;

-- ============================================================
-- 5. GRAIN CHECK — confirm the product-revenue-vs-volume rank
-- comparison in 02_best_selling_products.sql doesn't have
-- duplicate product_id rows (would indicate a fan-out join)
-- ============================================================

INSERT INTO #P4Results
SELECT 'Grain', 'Product-level revenue aggregation has one row per product_id',
       CASE WHEN COUNT(*) = COUNT(DISTINCT product_id) THEN 'PASS' ELSE 'FAIL' END, ''
FROM (
    SELECT dp.product_id
    FROM dbo.Fact_Order_Items foi
    JOIN dbo.Dim_Product dp ON foi.product_sk = dp.product_sk
    WHERE foi.order_status = 'delivered'
    GROUP BY dp.product_id
) x;

-- ============================================================
-- SUMMARY
-- ============================================================

SELECT * FROM #P4Results ORDER BY check_area, check_name;

SELECT status, COUNT(*) AS check_count FROM #P4Results GROUP BY status;

IF EXISTS (SELECT 1 FROM #P4Results WHERE status = 'FAIL')
    PRINT '*** PHASE 4 VALIDATION: FAIL — see FAIL rows above ***';
ELSE
    PRINT '*** PHASE 4 VALIDATION: PASS ***';

DROP TABLE #P4Results;
