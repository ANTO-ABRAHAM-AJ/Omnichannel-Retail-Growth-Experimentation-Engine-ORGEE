/*
    ORGEE — Phase 3: Fact_Inventory_Snapshot
    Grain: one row per inventory observation (product x location x timestamp)
    Source: inventory_observations.csv
    Type: periodic snapshot fact
*/

IF OBJECT_ID('dbo.Fact_Inventory_Snapshot', 'U') IS NOT NULL
    DROP TABLE dbo.Fact_Inventory_Snapshot;
GO

CREATE TABLE dbo.Fact_Inventory_Snapshot (
    inventory_snapshot_sk     BIGINT          IDENTITY(1,1)  NOT NULL,

    inventory_observation_id     VARCHAR(24)                 NOT NULL,
    inventory_location_id           VARCHAR(15)               NULL,   -- e.g. 'inv_loc_01'

    product_sk                        INT                     NULL,
    observation_date_sk                  INT                  NULL,

    observation_timestamp               DATETIME2              NOT NULL,
    available_quantity                     INT                 NULL,
    reserved_quantity                         INT              NULL,
    inventory_status                            VARCHAR(15)    NULL,   -- in_stock, low_stock, out_of_stock

    load_timestamp                                DATETIME2  DEFAULT SYSUTCDATETIME() NOT NULL,

    CONSTRAINT PK_Fact_Inventory_Snapshot PRIMARY KEY CLUSTERED (inventory_snapshot_sk),
    CONSTRAINT UQ_Fact_Inventory_Snapshot_id UNIQUE (inventory_observation_id)
);
GO
