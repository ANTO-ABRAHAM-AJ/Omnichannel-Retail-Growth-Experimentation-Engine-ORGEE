/*
    ORGEE — Phase 3: Fix — Fact_Inventory_Snapshot reload

    Root cause: TRY_CONVERT(DATETIME2(7), text) without an explicit
    style code can behave inconsistently depending on SQL Server
    session language/date-format settings — even though every one of
    the 1,000,000 source timestamps was verified perfectly formatted.
    Fixed by pinning style 120 (ODBC canonical 'yyyy-mm-dd hh:mi:ss'),
    which is session-independent.

    Run this ONCE. It only touches Fact_Inventory_Snapshot — your
    other 8 fact tables from 04_load_facts.sql are untouched.
*/

;WITH InventoryConv AS (
    SELECT
        inventory_observation_id, product_id, inventory_location_id,
        TRY_CONVERT(DATETIME2(7), observation_timestamp, 120) AS observation_timestamp,
        TRY_CONVERT(INT, available_quantity)                     AS available_quantity,
        TRY_CONVERT(INT, reserved_quantity)                         AS reserved_quantity,
        inventory_status
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

-- Should return 0 — confirms no row silently lost a valid timestamp
SELECT COUNT(*) AS unexplained_null_timestamps
FROM dbo.Fact_Inventory_Snapshot fis
JOIN staging.stg_inventory_observations sio
    ON fis.inventory_observation_id = sio.inventory_observation_id
WHERE fis.observation_timestamp IS NULL AND sio.observation_timestamp IS NOT NULL;
