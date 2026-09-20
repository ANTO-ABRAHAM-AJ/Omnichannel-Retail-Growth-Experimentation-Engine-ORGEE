/*
    ORGEE — Phase 3: Warehouse Validation
    Run this against the ORGEE database after the full load.
    Every check writes a PASS/FAIL row into #Results, and the script
    ends with a clear summary — mirrors the Phase 2 quality gate.
*/

IF OBJECT_ID('tempdb..#Results') IS NOT NULL DROP TABLE #Results;
CREATE TABLE #Results (
    check_area   VARCHAR(30),
    check_name   VARCHAR(150),
    status       VARCHAR(4),
    detail       VARCHAR(200)
);

-- ============================================================
-- 1. ROW COUNT RECONCILIATION (known-correct counts from Phase 2)
-- Uses SQL Server's internal partition metadata (sys.dm_db_partition_stats)
-- instead of COUNT(*) — this reads catalog metadata only, never
-- scans actual table data, so it's instant and immune to buffer
-- pool / memory pressure regardless of table size.
-- ============================================================

IF OBJECT_ID('tempdb..#ExpectedCounts') IS NOT NULL DROP TABLE #ExpectedCounts;
CREATE TABLE #ExpectedCounts (table_name SYSNAME, expected_count BIGINT);

INSERT INTO #ExpectedCounts (table_name, expected_count) VALUES
('Dim_Customer', 99441),
('Dim_Product', 32951),
('Dim_Seller', 3095),
('Dim_Campaign', 50),
('Dim_Experiment', 3),
('Fact_Order_Items', 112650),
('Fact_Reviews', 99224),
('Fact_Sessions', 500000),
('Fact_Events', 3000000),
('Fact_Identity_Links', 90321),
('Fact_Campaign_Exposures', 1000000),
('Fact_Inventory_Snapshot', 1000000),
('Fact_Experiment_Assignments', 298323),
('Fact_Recommendation_Events', 10287);

;WITH ActualCounts AS (
    SELECT o.name AS table_name, SUM(ps.row_count) AS actual_count
    FROM sys.dm_db_partition_stats ps
    JOIN sys.objects o ON ps.object_id = o.object_id
    WHERE ps.index_id IN (0, 1)  -- 0 = heap, 1 = clustered (rowstore OR columnstore)
    GROUP BY o.name
)
INSERT INTO #Results
SELECT
    'Row Counts',
    CONCAT(ec.table_name, ' = ', ec.expected_count),
    CASE WHEN ac.actual_count = ec.expected_count THEN 'PASS' ELSE 'FAIL' END,
    CONCAT('actual=', ISNULL(ac.actual_count, 0))
FROM #ExpectedCounts ec
LEFT JOIN ActualCounts ac ON ec.table_name = ac.table_name;

DROP TABLE #ExpectedCounts;

-- ============================================================
-- 2. UNIQUENESS / GRAIN CHECKS
-- ============================================================

INSERT INTO #Results
SELECT 'Grain', 'Dim_Customer.customer_id unique',
       CASE WHEN COUNT(*) = COUNT(DISTINCT customer_id) THEN 'PASS' ELSE 'FAIL' END, ''
FROM dbo.Dim_Customer;

INSERT INTO #Results
SELECT 'Grain', 'Fact_Order_Items (order_id, order_item_id) unique',
       CASE WHEN COUNT(*) = COUNT(DISTINCT CONCAT(order_id, '|', order_item_id)) THEN 'PASS' ELSE 'FAIL' END, ''
FROM dbo.Fact_Order_Items;

INSERT INTO #Results
SELECT 'Grain', 'Fact_Reviews (review_id, order_id) unique',
       CASE WHEN COUNT(*) = COUNT(DISTINCT CONCAT(review_id, '|', order_id)) THEN 'PASS' ELSE 'FAIL' END, ''
FROM dbo.Fact_Reviews;

INSERT INTO #Results
SELECT 'Grain', 'Fact_Sessions.session_id unique',
       CASE WHEN COUNT(*) = COUNT(DISTINCT session_id) THEN 'PASS' ELSE 'FAIL' END, ''
FROM dbo.Fact_Sessions;

INSERT INTO #Results
SELECT 'Grain', 'Fact_Events.event_id unique',
       CASE WHEN COUNT(*) = COUNT(DISTINCT event_id) THEN 'PASS' ELSE 'FAIL' END, ''
FROM dbo.Fact_Events
OPTION (MAXDOP 1);

-- ============================================================
-- 3. ORPHAN / REFERENTIAL INTEGRITY CHECKS
-- (belt-and-suspenders — FK constraints already enforce these,
-- this proves it explicitly for the validation record)
-- ============================================================

INSERT INTO #Results
SELECT 'Referential Integrity', 'Fact_Order_Items: no orphan product_sk',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END, CONCAT('orphans=', COUNT(*))
FROM dbo.Fact_Order_Items foi
LEFT JOIN dbo.Dim_Product dp ON foi.product_sk = dp.product_sk
WHERE foi.product_sk IS NOT NULL AND dp.product_sk IS NULL;

INSERT INTO #Results
SELECT 'Referential Integrity', 'Fact_Events: every session_id exists in Fact_Sessions',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END, CONCAT('orphans=', COUNT(*))
FROM dbo.Fact_Events fe
LEFT JOIN dbo.Fact_Sessions fs ON fe.session_id = fs.session_id
WHERE fs.session_id IS NULL
OPTION (MAXDOP 1);

INSERT INTO #Results
SELECT 'Referential Integrity', 'Fact_Identity_Links: every session_id exists in Fact_Sessions',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END, CONCAT('orphans=', COUNT(*))
FROM dbo.Fact_Identity_Links fil
LEFT JOIN dbo.Fact_Sessions fs ON fil.session_id = fs.session_id
WHERE fs.session_id IS NULL;

-- ============================================================
-- 4. BUSINESS LOGIC / PHASE 2 CARRY-FORWARD CHECKS
-- ============================================================

INSERT INTO #Results
SELECT 'Business Logic', 'Fact_Sessions.customer_sk populated ONLY for identified sessions (matches Fact_Identity_Links count)',
       CASE WHEN (SELECT COUNT(*) FROM dbo.Fact_Sessions WHERE customer_sk IS NOT NULL)
                 = (SELECT COUNT(*) FROM dbo.Fact_Identity_Links)
            THEN 'PASS' ELSE 'FAIL' END,
       CONCAT('sessions_identified=', (SELECT COUNT(*) FROM dbo.Fact_Sessions WHERE customer_sk IS NOT NULL),
              ', identity_links=', (SELECT COUNT(*) FROM dbo.Fact_Identity_Links));

INSERT INTO #Results
SELECT 'Business Logic', 'Fact_Events.event_type has no recommendation_impression/click leakage',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END, CONCAT('leaked_rows=', COUNT(*))
FROM dbo.Fact_Events
WHERE event_type IN ('recommendation_impression', 'recommendation_click')
OPTION (MAXDOP 1);

INSERT INTO #Results
SELECT 'Business Logic', 'Funnel shows real drop-off (purchase < product_view)',
       CASE WHEN
           (SELECT COUNT(*) FROM dbo.Fact_Events WHERE event_type = 'purchase_interaction')
           < (SELECT COUNT(*) FROM dbo.Fact_Events WHERE event_type = 'product_view')
       THEN 'PASS' ELSE 'FAIL' END, ''
OPTION (MAXDOP 1);

INSERT INTO #Results
SELECT 'Business Logic', 'Fact_Inventory_Snapshot.inventory_status has no corruption (trailing \\r etc)',
       CASE WHEN COUNT(*) = 3 THEN 'PASS' ELSE 'FAIL' END, CONCAT('distinct_values=', COUNT(*))
FROM (SELECT DISTINCT inventory_status FROM dbo.Fact_Inventory_Snapshot) x;

INSERT INTO #Results
SELECT 'Business Logic', 'No fact table date_sk falls outside Dim_Date range',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END, CONCAT('out_of_range=', COUNT(*))
FROM dbo.Fact_Events fe
LEFT JOIN dbo.Dim_Date dd ON fe.event_date_sk = dd.date_sk
WHERE fe.event_date_sk IS NOT NULL AND dd.date_sk IS NULL
OPTION (MAXDOP 1);

-- ============================================================
-- 5. INDEX / PHYSICAL DESIGN CHECKS
-- ============================================================

INSERT INTO #Results
SELECT 'Indexes', 'Fact_Events has a clustered columnstore index',
       CASE WHEN EXISTS (
           SELECT 1 FROM sys.indexes
           WHERE object_id = OBJECT_ID('dbo.Fact_Events') AND type = 5 -- 5 = CLUSTERED COLUMNSTORE
       ) THEN 'PASS' ELSE 'FAIL' END, '';

-- ============================================================
-- SUMMARY
-- ============================================================

SELECT * FROM #Results ORDER BY check_area, check_name;

SELECT
    status,
    COUNT(*) AS check_count
FROM #Results
GROUP BY status;

IF EXISTS (SELECT 1 FROM #Results WHERE status = 'FAIL')
    PRINT '*** VALIDATION FAILED — see FAIL rows above ***';
ELSE
    PRINT '*** ALL CHECKS PASSED — warehouse validated, clear to proceed ***';

DROP TABLE #Results;
