/*
    ORGEE — Phase 3: Dim_Campaign
    Grain: one row per campaign_id
    Source: campaigns.csv
    Type 1 SCD — overwrite on reload
*/

IF OBJECT_ID('dbo.Dim_Campaign', 'U') IS NOT NULL
    DROP TABLE dbo.Dim_Campaign;
GO

CREATE TABLE dbo.Dim_Campaign (
    campaign_sk       INT             IDENTITY(1,1)   NOT NULL,
    campaign_id        VARCHAR(20)                    NOT NULL,   -- e.g. 'camp_0001'
    campaign_name       VARCHAR(50)                   NULL,
    channel             VARCHAR(20)                   NULL,       -- email, push, social, search, display
    campaign_type        VARCHAR(30)                  NULL,       -- e.g. 'engagement_campaign'
    objective            VARCHAR(20)                  NULL,       -- e.g. 'engagement'
    start_date            DATE                        NULL,
    end_date              DATE                        NULL,
    load_timestamp        DATETIME2  DEFAULT SYSUTCDATETIME() NOT NULL,

    CONSTRAINT PK_Dim_Campaign PRIMARY KEY CLUSTERED (campaign_sk),
    CONSTRAINT UQ_Dim_Campaign_campaign_id UNIQUE (campaign_id)
);
GO
