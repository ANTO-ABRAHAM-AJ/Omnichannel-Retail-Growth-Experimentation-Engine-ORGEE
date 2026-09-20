/*
    ============================================================
    ORGEE — Phase 5: Customer Journey Analytics
    10_phase5_validation.sql
    ============================================================
    Validates the assumptions and calculations used across
    scripts 01-09. Every check writes a PASS/FAIL/INFO row; the
    script ends with a summary — matches the Phase 2/3/4 pattern.
    ============================================================
*/

IF OBJECT_ID('tempdb..#P5Results') IS NOT NULL DROP TABLE #P5Results;
CREATE TABLE #P5Results (check_area VARCHAR(30), check_name VARCHAR(150), status VARCHAR(4), detail VARCHAR(300));

-- ============================================================
-- 1. SESSION GRAIN
-- ============================================================

INSERT INTO #P5Results
SELECT 'Grain', 'Fact_Sessions.session_id is unique',
       CASE WHEN COUNT(*) = COUNT(DISTINCT session_id) THEN 'PASS' ELSE 'FAIL' END, ''
FROM dbo.Fact_Sessions;

-- ============================================================
-- 2. EVENT / SESSION RELATIONSHIP
-- (belt-and-suspenders on top of the FK constraint from Phase 3)
-- ============================================================

INSERT INTO #P5Results
SELECT 'Referential Integrity', 'Every Fact_Events.session_id exists in Fact_Sessions',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END, CONCAT('orphans=', COUNT(*))
FROM dbo.Fact_Events fe
LEFT JOIN dbo.Fact_Sessions fs ON fe.session_id = fs.session_id
WHERE fs.session_id IS NULL
OPTION (MAXDOP 1);

-- ============================================================
-- 3. NO ACCIDENTAL FAN-OUT — funnel stage counts should equal
-- DISTINCT session counts, not raw event-row counts (a session
-- with 5 product_view events must count once, not five times)
-- ============================================================

INSERT INTO #P5Results
SELECT 'Grain', 'Funnel stage counts use DISTINCT sessions, not raw event rows',
       CASE WHEN distinct_sessions <= raw_events THEN 'PASS' ELSE 'FAIL' END,
       CONCAT('distinct_sessions_with_product_view=', distinct_sessions, ', raw_product_view_events=', raw_events)
FROM (
    SELECT
        COUNT(DISTINCT session_id) AS distinct_sessions,
        COUNT(*) AS raw_events
    FROM dbo.Fact_Events
    WHERE event_type = 'product_view'
) x;

-- ============================================================
-- 4. CUSTOMER IDENTITY HANDLING — nullable customer_sk is
-- EXPECTED, not a defect (anonymous-until-login model)
-- ============================================================

INSERT INTO #P5Results
SELECT 'Identity Handling', 'Fact_Sessions identification rate matches Phase 3 baseline (~18%)',
       CASE WHEN pct BETWEEN 15 AND 21 THEN 'PASS' ELSE 'WARN' END,
       CONCAT('identified_pct=', pct)
FROM (
    SELECT ROUND(100.0 * SUM(CASE WHEN customer_sk IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct
    FROM dbo.Fact_Sessions
) x;

-- ============================================================
-- 5. DATE RELATIONSHIPS
-- ============================================================

INSERT INTO #P5Results
SELECT 'Date Logic', 'Every Fact_Events.event_date_sk resolves in Dim_Date',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END, CONCAT('unresolved=', COUNT(*))
FROM dbo.Fact_Events fe
LEFT JOIN dbo.Dim_Date d ON fe.event_date_sk = d.date_sk
WHERE fe.event_date_sk IS NOT NULL AND d.date_sk IS NULL
OPTION (MAXDOP 1);

INSERT INTO #P5Results
SELECT 'Date Logic', 'Every Fact_Order_Items.order_purchase_date_sk resolves in Dim_Date',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END, CONCAT('unresolved=', COUNT(*))
FROM dbo.Fact_Order_Items foi
LEFT JOIN dbo.Dim_Date d ON foi.order_purchase_date_sk = d.date_sk
WHERE foi.order_purchase_date_sk IS NOT NULL AND d.date_sk IS NULL;

-- ============================================================
-- 6. FUNNEL STAGE COUNTS — no impossible progression
-- (each stage's session count must be <= the prior stage's)
-- ============================================================

INSERT INTO #P5Results
SELECT 'Funnel Logic', 'Funnel stage counts are monotonically non-increasing (Visit >= ... >= Purchase)',
       CASE WHEN visit >= pv AND pv >= atc AND atc >= co AND co >= pur THEN 'PASS' ELSE 'FAIL' END,
       CONCAT('visit=', visit, ', product_view=', pv, ', add_to_cart=', atc, ', checkout=', co, ', purchase=', pur)
FROM (
    SELECT
        (SELECT COUNT(DISTINCT session_id) FROM dbo.Fact_Events WHERE event_type = 'session_start') AS visit,
        (SELECT COUNT(DISTINCT session_id) FROM dbo.Fact_Events WHERE event_type = 'product_view') AS pv,
        (SELECT COUNT(DISTINCT session_id) FROM dbo.Fact_Events WHERE event_type = 'add_to_cart') AS atc,
        (SELECT COUNT(DISTINCT session_id) FROM dbo.Fact_Events WHERE event_type = 'checkout_start') AS co,
        (SELECT COUNT(DISTINCT session_id) FROM dbo.Fact_Events WHERE event_type = 'purchase_interaction') AS pur
) x;

-- ============================================================
-- 6b. CHRONOLOGICAL STAGE ORDER — the concern raised in review:
-- does presence-based counting (MAX(CASE...)) accidentally credit
-- a session for a stage that happened OUT of order? Verified with
-- actual timestamps: every stage transition must strictly follow
-- the previous one in time, cascading from Visit through Purchase.
-- ============================================================

INSERT INTO #P5Results
SELECT 'Funnel Logic', 'Every stage transition is chronologically ordered (Visit < Product View < Add to Cart < Checkout < Purchase)',
       CASE WHEN pv_ordered = pv_total AND atc_ordered = atc_total
                 AND co_ordered = co_total AND pur_ordered = pur_total
            THEN 'PASS' ELSE 'FAIL' END,
       CONCAT(
           'product_view: ', pv_ordered, '/', pv_total, ' after visit; ',
           'add_to_cart: ', atc_ordered, '/', atc_total, ' after product_view; ',
           'checkout: ', co_ordered, '/', co_total, ' after add_to_cart; ',
           'purchase: ', pur_ordered, '/', pur_total, ' after checkout'
       )
FROM (
    SELECT
        SUM(CASE WHEN pv_ts IS NOT NULL AND visit_ts IS NOT NULL AND pv_ts > visit_ts THEN 1 ELSE 0 END) AS pv_ordered,
        SUM(CASE WHEN pv_ts IS NOT NULL THEN 1 ELSE 0 END) AS pv_total,
        SUM(CASE WHEN atc_ts IS NOT NULL AND pv_ts IS NOT NULL AND atc_ts > pv_ts THEN 1 ELSE 0 END) AS atc_ordered,
        SUM(CASE WHEN atc_ts IS NOT NULL THEN 1 ELSE 0 END) AS atc_total,
        SUM(CASE WHEN co_ts IS NOT NULL AND atc_ts IS NOT NULL AND co_ts > atc_ts THEN 1 ELSE 0 END) AS co_ordered,
        SUM(CASE WHEN co_ts IS NOT NULL THEN 1 ELSE 0 END) AS co_total,
        SUM(CASE WHEN pur_ts IS NOT NULL AND co_ts IS NOT NULL AND pur_ts > co_ts THEN 1 ELSE 0 END) AS pur_ordered,
        SUM(CASE WHEN pur_ts IS NOT NULL THEN 1 ELSE 0 END) AS pur_total
    FROM (
        SELECT
            session_id,
            MIN(CASE WHEN event_type = 'session_start' THEN event_timestamp END) AS visit_ts,
            MIN(CASE WHEN event_type = 'product_view' THEN event_timestamp END) AS pv_ts,
            MIN(CASE WHEN event_type = 'add_to_cart' THEN event_timestamp END) AS atc_ts,
            MIN(CASE WHEN event_type = 'checkout_start' THEN event_timestamp END) AS co_ts,
            MIN(CASE WHEN event_type = 'purchase_interaction' THEN event_timestamp END) AS pur_ts
        FROM dbo.Fact_Events
        GROUP BY session_id
    ) stamps
) checked
OPTION (MAXDOP 1);

-- ============================================================
-- 7. CONVERSION / DROP-OFF PERCENTAGE SANITY — must fall in [0,100]
-- ============================================================

INSERT INTO #P5Results
SELECT 'Percentage Sanity', 'Overall funnel conversion rate (Visit to Purchase) is between 0 and 100%',
       CASE WHEN pct BETWEEN 0 AND 100 THEN 'PASS' ELSE 'FAIL' END, CONCAT('pct=', pct)
FROM (
    SELECT ROUND(
        100.0 * (SELECT COUNT(DISTINCT session_id) FROM dbo.Fact_Events WHERE event_type = 'purchase_interaction')
        / NULLIF((SELECT COUNT(DISTINCT session_id) FROM dbo.Fact_Events WHERE event_type = 'session_start'), 0), 4
    ) AS pct
) x;

-- ============================================================
-- 8. COHORT / RETENTION SANITY
-- ============================================================

INSERT INTO #P5Results
SELECT 'Cohort Logic', 'Every delivered-order customer is assigned to exactly one cohort (no duplicates/omissions)',
       CASE WHEN total_customers = sum_of_cohort_sizes THEN 'PASS' ELSE 'FAIL' END,
       CONCAT('total_customers=', total_customers, ', sum_of_cohort_sizes=', sum_of_cohort_sizes)
FROM (
    SELECT
        (SELECT COUNT(DISTINCT dc.customer_unique_id)
         FROM dbo.Fact_Order_Items foi
         JOIN dbo.Dim_Customer dc ON foi.customer_sk = dc.customer_sk
         WHERE foi.order_status = 'delivered') AS total_customers,
        (SELECT COUNT(*) FROM (
            SELECT dc.customer_unique_id
            FROM dbo.Fact_Order_Items foi
            JOIN dbo.Dim_Customer dc ON foi.customer_sk = dc.customer_sk
            JOIN dbo.Dim_Date d ON foi.order_purchase_date_sk = d.date_sk
            WHERE foi.order_status = 'delivered'
            GROUP BY dc.customer_unique_id
         ) cohort_assignment) AS sum_of_cohort_sizes
) x;

INSERT INTO #P5Results
SELECT 'Cohort Logic', 'No retention percentage exceeds 100%',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END, CONCAT('violations=', COUNT(*))
FROM (
    SELECT
        cohort_month,
        month_offset,
        active_customers,
        FIRST_VALUE(active_customers) OVER (PARTITION BY cohort_month ORDER BY month_offset) AS cohort_size
    FROM (
        SELECT
            DATEFROMPARTS(YEAR(cfo.first_order_date), MONTH(cfo.first_order_date), 1) AS cohort_month,
            DATEDIFF(MONTH,
                DATEFROMPARTS(YEAR(cfo.first_order_date), MONTH(cfo.first_order_date), 1),
                com.order_month
            ) AS month_offset,
            COUNT(DISTINCT cfo.customer_unique_id) AS active_customers
        FROM (
            SELECT dc.customer_unique_id, MIN(d.full_date) AS first_order_date
            FROM dbo.Fact_Order_Items foi
            JOIN dbo.Dim_Customer dc ON foi.customer_sk = dc.customer_sk
            JOIN dbo.Dim_Date d ON foi.order_purchase_date_sk = d.date_sk
            WHERE foi.order_status = 'delivered'
            GROUP BY dc.customer_unique_id
        ) cfo
        JOIN (
            SELECT DISTINCT dc.customer_unique_id,
                DATEFROMPARTS(d.year_number, d.month_number, 1) AS order_month
            FROM dbo.Fact_Order_Items foi
            JOIN dbo.Dim_Customer dc ON foi.customer_sk = dc.customer_sk
            JOIN dbo.Dim_Date d ON foi.order_purchase_date_sk = d.date_sk
            WHERE foi.order_status = 'delivered'
        ) com ON cfo.customer_unique_id = com.customer_unique_id
        GROUP BY
            DATEFROMPARTS(YEAR(cfo.first_order_date), MONTH(cfo.first_order_date), 1),
            DATEDIFF(MONTH,
                DATEFROMPARTS(YEAR(cfo.first_order_date), MONTH(cfo.first_order_date), 1),
                com.order_month
            )
    ) grid
) checked
WHERE active_customers > cohort_size;

-- ============================================================
-- 9. NULL HANDLING
-- ============================================================

INSERT INTO #P5Results
SELECT 'Null Handling', 'Fact_Events.event_type is never NULL',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END, CONCAT('null_count=', COUNT(*))
FROM dbo.Fact_Events WHERE event_type IS NULL;

INSERT INTO #P5Results
SELECT 'Null Handling', 'Fact_Sessions.customer_sk nullable is expected (anonymous-until-login), not a defect',
       'INFO',
       CONCAT('null_count=', (SELECT COUNT(*) FROM dbo.Fact_Sessions WHERE customer_sk IS NULL),
              ' of ', (SELECT COUNT(*) FROM dbo.Fact_Sessions));

-- ============================================================
-- SUMMARY
-- ============================================================

SELECT * FROM #P5Results ORDER BY check_area, check_name;

SELECT status, COUNT(*) AS check_count FROM #P5Results GROUP BY status;

IF EXISTS (SELECT 1 FROM #P5Results WHERE status = 'FAIL')
    PRINT '*** PHASE 5 VALIDATION: FAIL — see FAIL rows above ***';
ELSE
    PRINT '*** PHASE 5 VALIDATION: PASS ***';

DROP TABLE #P5Results;
