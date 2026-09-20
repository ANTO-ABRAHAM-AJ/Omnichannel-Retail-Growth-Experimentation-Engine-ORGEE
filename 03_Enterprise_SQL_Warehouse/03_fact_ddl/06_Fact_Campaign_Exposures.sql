/*
    ORGEE — Phase 3: Fact_Campaign_Exposures
    Grain: one row per campaign exposure
    Source: campaign_exposures.csv

    NOTE: customer_sk is nullable — most exposures land on anonymous
    sessions (marketing reaches people before they've logged in).
*/

IF OBJECT_ID('dbo.Fact_Campaign_Exposures', 'U') IS NOT NULL
    DROP TABLE dbo.Fact_Campaign_Exposures;
GO

CREATE TABLE dbo.Fact_Campaign_Exposures (
    campaign_exposure_sk     BIGINT          IDENTITY(1,1)  NOT NULL,

    campaign_exposure_id        VARCHAR(20)                 NOT NULL,
    session_id                     VARCHAR(20)               NULL,
    anonymous_id                      VARCHAR(20)             NULL,

    campaign_sk                    INT                        NULL,
    customer_sk                       INT                     NULL,   -- nullable: see note above
    exposure_date_sk                     INT                  NULL,

    exposure_timestamp                DATETIME2                NOT NULL,
    channel                              VARCHAR(20)            NULL,   -- email, search, social, display, push
    exposure_outcome                       VARCHAR(20)          NULL,   -- impression, click, conversion

    load_timestamp                          DATETIME2  DEFAULT SYSUTCDATETIME() NOT NULL,

    CONSTRAINT PK_Fact_Campaign_Exposures PRIMARY KEY CLUSTERED (campaign_exposure_sk),
    CONSTRAINT UQ_Fact_Campaign_Exposures_id UNIQUE (campaign_exposure_id)
);
GO
