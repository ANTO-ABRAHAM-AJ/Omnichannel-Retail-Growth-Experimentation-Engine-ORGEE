/*
    ORGEE — Phase 3: Dim_Device
    Grain: one row per distinct (device_type, platform) combination
    Source: derived — DISTINCT device_type, platform FROM sessions.csv
    Observed cardinality (Phase 2 data):
        device_type: mobile, desktop, tablet
        platform:    web, mobile_app, desktop
    Small lookup table — populated once in 05_data_load, rarely changes.
*/

IF OBJECT_ID('dbo.Dim_Device', 'U') IS NOT NULL
    DROP TABLE dbo.Dim_Device;
GO

CREATE TABLE dbo.Dim_Device (
    device_sk     INT             IDENTITY(1,1)  NOT NULL,
    device_type   VARCHAR(20)                    NOT NULL,  -- mobile, desktop, tablet
    platform      VARCHAR(20)                    NOT NULL,  -- web, mobile_app, desktop

    CONSTRAINT PK_Dim_Device PRIMARY KEY CLUSTERED (device_sk),
    CONSTRAINT UQ_Dim_Device_combo UNIQUE (device_type, platform)
);
GO
