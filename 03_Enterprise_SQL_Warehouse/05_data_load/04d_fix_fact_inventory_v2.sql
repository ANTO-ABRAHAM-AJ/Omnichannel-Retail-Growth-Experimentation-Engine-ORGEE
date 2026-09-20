/*
    ORGEE — Phase 3: Fix — Fact_Inventory_Snapshot (real root cause)

    inventory_observations.csv was NEVER part of the Phase 2 fixes —
    it still has its ORIGINAL format, different from every other
    enterprise file:
        - Timestamp format: DD-MM-YYYY HH:MM  (e.g. '22-10-2016 06:53')
          NOT YYYY-MM-DD HH:MM:SS like sessions/events/etc.
        - Line endings: CRLF (\r\n), NOT LF-only like other enterprise files.
    Verified against all 1,000,000 rows — 100% consistent.

    Because ROWTERMINATOR was wrongly set to LF-only for this file,
    a trailing \r also got stuck onto inventory_status for every row
    (harmless-looking, but worth cleaning up). This script:
      1. Truncates and reloads stg_inventory_observations with the
         correct CRLF terminator
      2. Reloads Fact_Inventory_Snapshot with a manual DD-MM-YYYY HH:MM
         -> ISO rearrangement before TRY_CONVERT (no built-in T-SQL
         style code handles this exact combined format)

    Run this ONCE. It only touches stg_inventory_observations and
    Fact_Inventory_Snapshot.
*/

-- ============================================================
-- Step 1: reload staging with the correct line terminator
-- ============================================================

TRUNCATE TABLE staging.stg_inventory_observations;

DECLARE @BasePath VARCHAR(500) =
    'C:\Users\ANTO ABRAHAM AJ\Downloads\Omnichannel Retail & Growth Experimentation Engine (ORGEE)\data\';

DECLARE @sql NVARCHAR(MAX);

SET @sql = N'
BULK INSERT staging.stg_inventory_observations
FROM ''' + @BasePath + N'enterprise\inventory\inventory_observations.csv''
WITH (FORMAT = ''CSV'', FIRSTROW = 2, FIELDQUOTE = ''"'', CODEPAGE = ''65001'',
      ROWTERMINATOR = ''0x0d0a'', KEEPNULLS, TABLOCK);';
EXEC sp_executesql @sql;

SELECT 'stg_inventory_observations' AS staging_table, COUNT(*) AS row_count
FROM staging.stg_inventory_observations;

-- ============================================================
-- Step 2: reload the fact table with correct date parsing
-- DD-MM-YYYY HH:MM  ->  rearrange to  YYYY-MM-DD HH:MM:00
-- (fixed-width: chars 1-2=day, 4-5=month, 7-10=year, 12-16=HH:MM)
-- ============================================================

TRUNCATE TABLE dbo.Fact_Inventory_Snapshot;

;WITH InventoryConv AS (
    SELECT
        inventory_observation_id,
        product_id,
        RTRIM(REPLACE(inventory_location_id, CHAR(13), ''))     AS inventory_location_id,
        TRY_CONVERT(
            DATETIME2(7),
            SUBSTRING(observation_timestamp, 7, 4) + '-' +
            SUBSTRING(observation_timestamp, 4, 2) + '-' +
            SUBSTRING(observation_timestamp, 1, 2) + ' ' +
            SUBSTRING(observation_timestamp, 12, 5) + ':00',
            120
        ) AS observation_timestamp,
        TRY_CONVERT(INT, available_quantity)                        AS available_quantity,
        TRY_CONVERT(INT, reserved_quantity)                            AS reserved_quantity,
        RTRIM(REPLACE(inventory_status, CHAR(13), ''))                   AS inventory_status
    FROM staging.stg_inventory_observations
)
INSERT INTO dbo.Fact_Inventory_Snapshot (
    inventory_observation_id, inventory_location_id, product_sk,
    observation_date_sk, observation_timestamp, available_quantity,
    reserved_quantity, inventory_status
)
SELECT
    io.inventory_observation_id, io.inventory_location_id, dp.product_sk,
    CAST(CONVERT(VARCHAR(8), io.observation_timestamp, 112) AS INT),
    io.observation_timestamp, io.available_quantity, io.reserved_quantity, io.inventory_status
FROM InventoryConv io
LEFT JOIN dbo.Dim_Product dp ON io.product_id = dp.product_id;

SELECT 'Fact_Inventory_Snapshot' AS fact_table, COUNT(*) AS row_count FROM dbo.Fact_Inventory_Snapshot;

-- Should return 0 — confirms every timestamp converted successfully
SELECT COUNT(*) AS unexplained_null_timestamps
FROM dbo.Fact_Inventory_Snapshot fis
JOIN staging.stg_inventory_observations sio
    ON fis.inventory_observation_id = sio.inventory_observation_id
WHERE fis.observation_timestamp IS NULL AND sio.observation_timestamp IS NOT NULL;

-- Spot check — should show clean 'in_stock' etc, no trailing \r
SELECT DISTINCT inventory_status FROM dbo.Fact_Inventory_Snapshot;
