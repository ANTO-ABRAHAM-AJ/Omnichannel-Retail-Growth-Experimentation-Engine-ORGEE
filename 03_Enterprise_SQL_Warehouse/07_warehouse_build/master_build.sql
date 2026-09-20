/*
    ORGEE — Phase 3: Master Warehouse Build

    Rebuilds the ENTIRE star schema from scratch, in the correct
    order, in one run: dimensions -> facts -> keys -> staging ->
    bulk load -> dimension load -> fact load -> indexes.

    Every fix discovered during the original build-and-load process
    (Dim_Experiment.objective width, Fact_Reviews grain, the
    inventory_observations.csv format mismatch) is folded directly
    into the referenced files below — a fresh run of this script
    will NOT hit any of those bugs again.

    ============================================================
    REQUIRES SQLCMD MODE — enable it first:
        SSMS: Query menu -> SQLCMD Mode
    Without SQLCMD Mode, the ":r" lines below are not valid T-SQL
    and this script will fail immediately with a syntax error.
    ============================================================

    Paths below are RELATIVE to this file's location. This script
    must stay in 03_Enterprise_SQL_Warehouse\07_warehouse_build\
    for the relative paths to resolve correctly.

    Before running: open 05_data_load\02_bulk_load_staging.sql and
    confirm @BasePath still points at your actual project folder.
*/

PRINT '=== ORGEE Warehouse Build — starting ===';
GO

-- ============================================================
-- STEP 1 — Dimension tables (7)
-- ============================================================
PRINT '--- Step 1: Dimension DDL ---';
:r ..\02_dimension_ddl\01_Dim_Customer.sql
:r ..\02_dimension_ddl\02_Dim_Product.sql
:r ..\02_dimension_ddl\03_Dim_Seller.sql
:r ..\02_dimension_ddl\04_Dim_Date.sql
:r ..\02_dimension_ddl\05_Dim_Campaign.sql
:r ..\02_dimension_ddl\06_Dim_Experiment.sql
:r ..\02_dimension_ddl\07_Dim_Device.sql

-- ============================================================
-- STEP 2 — Fact tables (9)
-- ============================================================
PRINT '--- Step 2: Fact DDL ---';
:r ..\03_fact_ddl\01_Fact_Order_Items.sql
:r ..\03_fact_ddl\02_Fact_Reviews.sql
:r ..\03_fact_ddl\03_Fact_Sessions.sql
:r ..\03_fact_ddl\04_Fact_Events.sql
:r ..\03_fact_ddl\05_Fact_Identity_Links.sql
:r ..\03_fact_ddl\06_Fact_Campaign_Exposures.sql
:r ..\03_fact_ddl\07_Fact_Inventory_Snapshot.sql
:r ..\03_fact_ddl\08_Fact_Experiment_Assignments.sql
:r ..\03_fact_ddl\09_Fact_Recommendation_Events.sql

-- ============================================================
-- STEP 3 — Foreign key constraints (dims + facts must both exist)
-- ============================================================
PRINT '--- Step 3: Keys & Constraints ---';
:r ..\04_keys_constraints\01_FK_Fact_Order_Items.sql
:r ..\04_keys_constraints\02_FK_Fact_Reviews.sql
:r ..\04_keys_constraints\03_FK_Fact_Sessions.sql
:r ..\04_keys_constraints\04_FK_Fact_Events.sql
:r ..\04_keys_constraints\05_FK_Fact_Identity_Links.sql
:r ..\04_keys_constraints\06_FK_Fact_Campaign_Exposures.sql
:r ..\04_keys_constraints\07_FK_Fact_Inventory_Snapshot.sql
:r ..\04_keys_constraints\08_FK_Fact_Experiment_Assignments.sql
:r ..\04_keys_constraints\09_FK_Fact_Recommendation_Events.sql

-- ============================================================
-- STEP 4 — Data load (staging -> dimensions -> facts)
-- ============================================================
PRINT '--- Step 4: Staging tables ---';
:r ..\05_data_load\01_staging_tables.sql

PRINT '--- Step 5: Bulk load staging from CSV ---';
:r ..\05_data_load\02_bulk_load_staging.sql

PRINT '--- Step 6: Load dimensions ---';
:r ..\05_data_load\03_load_dimensions.sql

PRINT '--- Step 7: Load facts ---';
:r ..\05_data_load\04_load_facts.sql

-- ============================================================
-- STEP 5 — Indexes (Fact_Events columnstore + supporting indexes)
-- ============================================================
PRINT '--- Step 8: Indexes ---';
:r ..\06_indexes\01_Fact_Events_indexes.sql
:r ..\06_indexes\02_Fact_Order_Items_indexes.sql
:r ..\06_indexes\03_Fact_Reviews_indexes.sql
:r ..\06_indexes\04_Fact_Sessions_indexes.sql
:r ..\06_indexes\05_Fact_Identity_Links_indexes.sql
:r ..\06_indexes\06_Fact_Campaign_Exposures_indexes.sql
:r ..\06_indexes\07_Fact_Inventory_Snapshot_indexes.sql
:r ..\06_indexes\08_Fact_Experiment_Assignments_indexes.sql
:r ..\06_indexes\09_Fact_Recommendation_Events_indexes.sql

PRINT '=== ORGEE Warehouse Build — complete ===';
GO

-- ============================================================
-- Final sanity check — row counts across every table
-- ============================================================

SELECT 'Dim_Customer' AS table_name, COUNT(*) AS row_count FROM dbo.Dim_Customer
UNION ALL SELECT 'Dim_Product', COUNT(*) FROM dbo.Dim_Product
UNION ALL SELECT 'Dim_Seller', COUNT(*) FROM dbo.Dim_Seller
UNION ALL SELECT 'Dim_Date', COUNT(*) FROM dbo.Dim_Date
UNION ALL SELECT 'Dim_Campaign', COUNT(*) FROM dbo.Dim_Campaign
UNION ALL SELECT 'Dim_Experiment', COUNT(*) FROM dbo.Dim_Experiment
UNION ALL SELECT 'Dim_Device', COUNT(*) FROM dbo.Dim_Device
UNION ALL SELECT 'Fact_Order_Items', COUNT(*) FROM dbo.Fact_Order_Items
UNION ALL SELECT 'Fact_Reviews', COUNT(*) FROM dbo.Fact_Reviews
UNION ALL SELECT 'Fact_Sessions', COUNT(*) FROM dbo.Fact_Sessions
UNION ALL SELECT 'Fact_Events', COUNT(*) FROM dbo.Fact_Events
UNION ALL SELECT 'Fact_Identity_Links', COUNT(*) FROM dbo.Fact_Identity_Links
UNION ALL SELECT 'Fact_Campaign_Exposures', COUNT(*) FROM dbo.Fact_Campaign_Exposures
UNION ALL SELECT 'Fact_Inventory_Snapshot', COUNT(*) FROM dbo.Fact_Inventory_Snapshot
UNION ALL SELECT 'Fact_Experiment_Assignments', COUNT(*) FROM dbo.Fact_Experiment_Assignments
UNION ALL SELECT 'Fact_Recommendation_Events', COUNT(*) FROM dbo.Fact_Recommendation_Events
ORDER BY table_name;
