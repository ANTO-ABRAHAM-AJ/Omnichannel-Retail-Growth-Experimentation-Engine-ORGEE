/*
    ORGEE — Phase 3: Dim_Date
    Grain: one row per calendar date
    Source: generated (not sourced from a CSV) — spans the earliest to
    latest timestamp across all fact sources (2016-09-04 to 2018-10-17,
    per the marketing period observed in Phase 2).
    Populated in 05_data_load (date dimensions are generated, not loaded).
*/

IF OBJECT_ID('dbo.Dim_Date', 'U') IS NOT NULL
    DROP TABLE dbo.Dim_Date;
GO

CREATE TABLE dbo.Dim_Date (
    date_sk         INT             NOT NULL,   -- YYYYMMDD, e.g. 20180807
    full_date       DATE                        NOT NULL,
    day_of_month    TINYINT                     NOT NULL,
    day_name        VARCHAR(10)                 NOT NULL,
    day_of_week     TINYINT                     NOT NULL,   -- 1=Sunday .. 7=Saturday
    is_weekend      BIT                         NOT NULL,
    month_number    TINYINT                     NOT NULL,
    month_name      VARCHAR(10)                 NOT NULL,
    quarter_number  TINYINT                     NOT NULL,
    year_number     SMALLINT                    NOT NULL,

    CONSTRAINT PK_Dim_Date PRIMARY KEY CLUSTERED (date_sk)
);
GO
