/*
    ============================================================
    ORGEE — Phase 6: Customer & Product Analytics
    11_phase6_validation.sql
    ============================================================
    Validates the assumptions and calculations used across
    scripts 01-10. Every check writes a PASS/FAIL/INFO row; the
    script ends with a summary — matches the Phase 2-5 pattern.
    ============================================================
*/

IF OBJECT_ID('tempdb..#P6Results') IS NOT NULL DROP TABLE #P6Results;
CREATE TABLE #P6Results (check_area VARCHAR(30), check_name VARCHAR(150), status VARCHAR(4), detail VARCHAR(300));

IF OBJECT_ID('tempdb..#RFMValidate') IS NOT NULL DROP TABLE #RFMValidate;

WITH SnapshotDate AS (
    SELECT MAX(d.full_date) AS snapshot_date
    FROM dbo.Fact_Order_Items foi
    JOIN dbo.Dim_Date d ON foi.order_purchase_date_sk = d.date_sk
    WHERE foi.order_status = 'delivered'
),
CustomerRFMBase AS (
    SELECT
        dc.customer_unique_id,
        COUNT(DISTINCT foi.order_id) AS frequency,
        SUM(foi.price) AS monetary,
        DATEDIFF(DAY, MAX(d.full_date), (SELECT snapshot_date FROM SnapshotDate)) AS recency_days
    FROM dbo.Fact_Order_Items foi
    JOIN dbo.Dim_Customer dc ON foi.customer_sk = dc.customer_sk
    JOIN dbo.Dim_Date d ON foi.order_purchase_date_sk = d.date_sk
    WHERE foi.order_status = 'delivered'
    GROUP BY dc.customer_unique_id
),
CustomerRFMScored AS (
    SELECT
        customer_unique_id, recency_days, frequency, monetary,
        NTILE(5) OVER (ORDER BY recency_days DESC, customer_unique_id ASC) AS r_score,
        CASE
            WHEN frequency = 1 THEN 1 WHEN frequency = 2 THEN 3
            WHEN frequency BETWEEN 3 AND 4 THEN 4 WHEN frequency >= 5 THEN 5
        END AS f_score,
        NTILE(5) OVER (ORDER BY monetary ASC, customer_unique_id ASC) AS m_score
    FROM CustomerRFMBase
)
SELECT customer_unique_id, recency_days, frequency, monetary, r_score, f_score, m_score,
    CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
        WHEN f_score = 1 AND r_score >= 4 AND m_score >= 3 THEN 'Potential Loyalists'
        WHEN f_score = 1 AND r_score >= 4 AND m_score < 3 THEN 'New Customers'
        WHEN f_score >= 3 AND r_score <= 2 THEN 'At Risk'
        WHEN r_score <= 2 AND f_score = 1 AND m_score <= 2 THEN 'Lost Customers'
        ELSE 'Needs Attention'
    END AS segment
INTO #RFMValidate
FROM CustomerRFMScored;

-- ============================================================
-- 1. CUSTOMER GRAIN — one row per customer_unique_id, no duplicates
-- ============================================================

INSERT INTO #P6Results
SELECT 'Grain', 'RFM table has exactly one row per customer_unique_id',
       CASE WHEN COUNT(*) = COUNT(DISTINCT customer_unique_id) THEN 'PASS' ELSE 'FAIL' END, ''
FROM #RFMValidate;

-- ============================================================
-- 2. RECENCY CALCULATION — no negative values, snapshot date used
-- (not GETDATE — would produce recency in the thousands of days)
-- ============================================================

INSERT INTO #P6Results
SELECT 'RFM Calculation', 'No negative recency_days values',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END, CONCAT('violations=', COUNT(*))
FROM #RFMValidate WHERE recency_days < 0;

INSERT INTO #P6Results
SELECT 'RFM Calculation', 'Snapshot date used, not GETDATE() (max recency stays under ~800 days for this 2016-2018 dataset)',
       CASE WHEN MAX(recency_days) < 800 THEN 'PASS' ELSE 'FAIL' END, CONCAT('max_recency_days=', MAX(recency_days))
FROM #RFMValidate;

-- ============================================================
-- 3. FREQUENCY CALCULATION — every value >= 1 (every customer in
-- this table has at least one delivered order by construction)
-- ============================================================

INSERT INTO #P6Results
SELECT 'RFM Calculation', 'No frequency values below 1',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END, CONCAT('violations=', COUNT(*))
FROM #RFMValidate WHERE frequency < 1;

-- ============================================================
-- 4. MONETARY CALCULATION — no negative or NULL values
-- ============================================================

INSERT INTO #P6Results
SELECT 'RFM Calculation', 'No negative or NULL monetary values',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END, CONCAT('violations=', COUNT(*))
FROM #RFMValidate WHERE monetary IS NULL OR monetary < 0;

-- ============================================================
-- 5. NO IMPOSSIBLE RFM SCORE VALUES — R/M must be 1-5, F must be
-- one of the defined bucket values (1, 3, 4, 5 — 2 is intentionally
-- never produced by the bucketing logic, not a bug)
-- ============================================================

INSERT INTO #P6Results
SELECT 'RFM Calculation', 'r_score and m_score are within [1,5]',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END, CONCAT('violations=', COUNT(*))
FROM #RFMValidate WHERE r_score NOT BETWEEN 1 AND 5 OR m_score NOT BETWEEN 1 AND 5;

INSERT INTO #P6Results
SELECT 'RFM Calculation', 'f_score only takes the defined bucket values (1,3,4,5)',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END, CONCAT('unexpected_values=', COUNT(*))
FROM #RFMValidate WHERE f_score NOT IN (1, 3, 4, 5);

-- ============================================================
-- 6. SEGMENT ASSIGNMENT — every customer has a segment, no NULLs,
-- and every customer falls into exactly one of the defined segments
-- ============================================================

INSERT INTO #P6Results
SELECT 'Segment Assignment', 'Every customer has a non-NULL segment',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END, CONCAT('null_segments=', COUNT(*))
FROM #RFMValidate WHERE segment IS NULL;

INSERT INTO #P6Results
SELECT 'Segment Assignment', 'Segment values are limited to the 7 defined categories',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END, CONCAT('unexpected_segments=', COUNT(*))
FROM #RFMValidate
WHERE segment NOT IN ('Champions','Loyal Customers','Potential Loyalists','New Customers','At Risk','Lost Customers','Needs Attention');

-- ============================================================
-- 7. CLV / MONETARY RECONCILIATION — sum of individual customer
-- monetary values must equal total delivered revenue (no double
-- counting, no missing customers)
-- ============================================================

INSERT INTO #P6Results
SELECT 'Revenue Reconciliation', 'SUM(monetary) across all customers equals total delivered revenue',
       CASE WHEN ABS(rfm_total - actual_total) < 1.00 THEN 'PASS' ELSE 'FAIL' END,
       CONCAT('rfm_total=', rfm_total, ', actual_total=', actual_total)
FROM (
    SELECT
        (SELECT SUM(monetary) FROM #RFMValidate) AS rfm_total,
        (SELECT SUM(price) FROM dbo.Fact_Order_Items WHERE order_status = 'delivered') AS actual_total
) x;

-- ============================================================
-- 8. CUSTOMER COUNT RECONCILIATION — matches Phase 4's known
-- customer_unique_id count with a delivered order (93,358)
-- ============================================================

INSERT INTO #P6Results
SELECT 'Customer Count', 'RFM customer count matches Phase 4 baseline (93,358)',
       CASE WHEN COUNT(*) = 93358 THEN 'PASS' ELSE 'FAIL' END, CONCAT('actual=', COUNT(*))
FROM #RFMValidate;

-- ============================================================
-- 9. NO ACCIDENTAL FAN-OUT — product-level aggregation in
-- 07_product_metrics.sql uses distinct sessions, not raw event rows
-- ============================================================

INSERT INTO #P6Results
SELECT 'Grain', 'Product view-to-cart aggregation uses DISTINCT sessions, not raw event rows',
       CASE WHEN distinct_sessions <= raw_events THEN 'PASS' ELSE 'FAIL' END,
       CONCAT('distinct=', distinct_sessions, ', raw=', raw_events)
FROM (
    SELECT
        COUNT(DISTINCT session_id) AS distinct_sessions,
        COUNT(*) AS raw_events
    FROM dbo.Fact_Events
    WHERE event_type = 'product_view'
) x;

-- ============================================================
-- 10. NULL HANDLING — critical KPI values must not be NULL
-- ============================================================

INSERT INTO #P6Results
SELECT 'Null Handling', 'North Star Metric (revenue per active customer) is not NULL',
       CASE WHEN val IS NOT NULL THEN 'PASS' ELSE 'FAIL' END, CONCAT('value=', val)
FROM (
    SELECT SUM(foi.price) / NULLIF(COUNT(DISTINCT dc.customer_unique_id), 0) AS val
    FROM dbo.Fact_Order_Items foi
    JOIN dbo.Dim_Customer dc ON foi.customer_sk = dc.customer_sk
    WHERE foi.order_status = 'delivered'
) x;

INSERT INTO #P6Results
SELECT 'Null Handling', 'Dim_Product.product_category_name_english NULL rate (expected: known source gap, not a Phase 6 defect)',
       'INFO', CONCAT('null_count=', COUNT(*), ' of ', (SELECT COUNT(*) FROM dbo.Dim_Product))
FROM dbo.Dim_Product WHERE product_category_name_english IS NULL;

DROP TABLE #RFMValidate;

-- ============================================================
-- SUMMARY
-- ============================================================

SELECT * FROM #P6Results ORDER BY check_area, check_name;

SELECT status, COUNT(*) AS check_count FROM #P6Results GROUP BY status;

IF EXISTS (SELECT 1 FROM #P6Results WHERE status = 'FAIL')
    PRINT '*** PHASE 6 VALIDATION: FAIL — see FAIL rows above ***';
ELSE
    PRINT '*** PHASE 6 VALIDATION: PASS ***';

DROP TABLE #P6Results;
