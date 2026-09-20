/*
    ORGEE — Phase 3: Load Dimensions from Staging (v2)
    Run AFTER 02_bulk_load_staging.sql.
    Every conversion from staging (now all-text) uses TRY_CONVERT,
    so a malformed value becomes NULL instead of aborting the load.
*/

-- ============================================================
-- Dim_Customer
-- ============================================================

INSERT INTO dbo.Dim_Customer (
    customer_id, customer_unique_id, customer_zip_code_prefix,
    customer_city, customer_state
)
SELECT DISTINCT
    customer_id, customer_unique_id, customer_zip_code_prefix,
    customer_city, LEFT(customer_state, 2)
FROM staging.stg_customers;

-- ============================================================
-- Dim_Product
-- ============================================================

INSERT INTO dbo.Dim_Product (
    product_id, product_category_name, product_category_name_english,
    product_name_length, product_description_length, product_photos_qty,
    product_weight_g, product_length_cm, product_height_cm, product_width_cm
)
SELECT
    p.product_id, p.product_category_name, t.product_category_name_english,
    TRY_CONVERT(INT, NULLIF(p.product_name_lenght, '')),
    TRY_CONVERT(INT, NULLIF(p.product_description_lenght, '')),
    TRY_CONVERT(INT, NULLIF(p.product_photos_qty, '')),
    TRY_CONVERT(DECIMAL(10,2), NULLIF(p.product_weight_g, '')),
    TRY_CONVERT(DECIMAL(10,2), NULLIF(p.product_length_cm, '')),
    TRY_CONVERT(DECIMAL(10,2), NULLIF(p.product_height_cm, '')),
    TRY_CONVERT(DECIMAL(10,2), NULLIF(p.product_width_cm, ''))
FROM staging.stg_products p
LEFT JOIN staging.stg_category_translation t
    ON p.product_category_name = t.product_category_name;

-- ============================================================
-- Dim_Seller
-- ============================================================

INSERT INTO dbo.Dim_Seller (
    seller_id, seller_zip_code_prefix, seller_city, seller_state
)
SELECT DISTINCT
    seller_id, seller_zip_code_prefix, seller_city, LEFT(seller_state, 2)
FROM staging.stg_sellers;

-- ============================================================
-- Dim_Campaign
-- ============================================================

INSERT INTO dbo.Dim_Campaign (
    campaign_id, campaign_name, channel, campaign_type, objective,
    start_date, end_date
)
SELECT
    campaign_id, campaign_name, channel, campaign_type, objective,
    TRY_CONVERT(DATE, TRY_CONVERT(DATETIME2(7), start_date, 120)),
    TRY_CONVERT(DATE, TRY_CONVERT(DATETIME2(7), end_date, 120))
FROM staging.stg_campaigns;

-- ============================================================
-- Dim_Experiment
-- ============================================================

INSERT INTO dbo.Dim_Experiment (
    experiment_id, experiment_name, objective, start_timestamp,
    end_timestamp, primary_metric, control_variant_label, treatment_variant_label
)
SELECT
    experiment_id, experiment_name, objective,
    TRY_CONVERT(DATETIME2(7), start_timestamp, 120),
    TRY_CONVERT(DATETIME2(7), end_timestamp, 120),
    primary_metric, control_variant, treatment_variant
FROM staging.stg_experiments;

-- ============================================================
-- Dim_Device — derived from distinct (device_type, platform)
-- combinations across BOTH sessions and events.
-- ============================================================

INSERT INTO dbo.Dim_Device (device_type, platform)
SELECT DISTINCT device_type, platform
FROM (
    SELECT device_type, platform FROM staging.stg_sessions
    UNION
    SELECT device_type, platform FROM staging.stg_events
) combined;

-- ============================================================
-- Dim_Date — generated to span the earliest to latest timestamp
-- across all fact sources, with a safety buffer on both ends.
-- ============================================================

DECLARE @StartDate DATE = '2016-01-01';
DECLARE @EndDate   DATE = '2018-12-31';

;WITH Numbers AS (
    SELECT TOP (DATEDIFF(DAY, @StartDate, @EndDate) + 1)
        ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) - 1 AS n
    FROM sys.all_objects a
    CROSS JOIN sys.all_objects b
),
Dates AS (
    SELECT DATEADD(DAY, n, @StartDate) AS full_date
    FROM Numbers
)
INSERT INTO dbo.Dim_Date (
    date_sk, full_date, day_of_month, day_name, day_of_week, is_weekend,
    month_number, month_name, quarter_number, year_number
)
SELECT
    CAST(CONVERT(VARCHAR(8), full_date, 112) AS INT)      AS date_sk,
    full_date,
    DAY(full_date)                                         AS day_of_month,
    DATENAME(WEEKDAY, full_date)                            AS day_name,
    DATEPART(WEEKDAY, full_date)                             AS day_of_week,
    CASE WHEN DATEPART(WEEKDAY, full_date) IN (1, 7)
         THEN CAST(1 AS BIT) ELSE CAST(0 AS BIT) END          AS is_weekend,
    MONTH(full_date)                                            AS month_number,
    DATENAME(MONTH, full_date)                                   AS month_name,
    DATEPART(QUARTER, full_date)                                  AS quarter_number,
    YEAR(full_date)                                                AS year_number
FROM Dates;

-- ============================================================
-- Row count check
-- ============================================================

SELECT 'Dim_Customer' AS dim_table, COUNT(*) AS row_count FROM dbo.Dim_Customer
UNION ALL SELECT 'Dim_Product', COUNT(*) FROM dbo.Dim_Product
UNION ALL SELECT 'Dim_Seller', COUNT(*) FROM dbo.Dim_Seller
UNION ALL SELECT 'Dim_Campaign', COUNT(*) FROM dbo.Dim_Campaign
UNION ALL SELECT 'Dim_Experiment', COUNT(*) FROM dbo.Dim_Experiment
UNION ALL SELECT 'Dim_Device', COUNT(*) FROM dbo.Dim_Device
UNION ALL SELECT 'Dim_Date', COUNT(*) FROM dbo.Dim_Date;

-- ============================================================
-- Conversion-failure check — should all return 0.
-- If any of these are nonzero, some staging text didn't survive
-- TRY_CONVERT and silently became NULL — worth a look.
-- ============================================================

SELECT 'Dim_Campaign NULL start_date despite staging value' AS check_name, COUNT(*) AS bad_rows
FROM dbo.Dim_Campaign dc
JOIN staging.stg_campaigns sc ON dc.campaign_id = sc.campaign_id
WHERE dc.start_date IS NULL AND sc.start_date IS NOT NULL AND sc.start_date <> ''

UNION ALL

SELECT 'Dim_Experiment NULL start_timestamp despite staging value', COUNT(*)
FROM dbo.Dim_Experiment de
JOIN staging.stg_experiments se ON de.experiment_id = se.experiment_id
WHERE de.start_timestamp IS NULL AND se.start_timestamp IS NOT NULL AND se.start_timestamp <> '';
