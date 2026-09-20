/*
    ORGEE — Phase 3: Fact_Identity_Links
    Grain: one row per anonymous_id -> customer_id link
    Source: identity_links.csv
    Type: factless fact table (bridge) — records the event of a
    successful login resolving an anonymous session to a known
    customer. No numeric measures; existence of the row IS the fact.
*/

IF OBJECT_ID('dbo.Fact_Identity_Links', 'U') IS NOT NULL
    DROP TABLE dbo.Fact_Identity_Links;
GO

CREATE TABLE dbo.Fact_Identity_Links (
    identity_link_sk       BIGINT          IDENTITY(1,1)  NOT NULL,

    identity_link_id          VARCHAR(20)                 NOT NULL,  -- e.g. 'identity_00000001'
    anonymous_id                 VARCHAR(20)               NOT NULL,
    session_id                      VARCHAR(20)             NOT NULL,

    customer_sk                 INT                        NOT NULL,  -- always known — this row only
                                                                       -- exists because a login succeeded
    link_date_sk                   INT                      NULL,

    link_timestamp                DATETIME2                 NOT NULL,
    link_method                      VARCHAR(20)             NOT NULL,  -- always 'successful_login'

    load_timestamp                    DATETIME2  DEFAULT SYSUTCDATETIME() NOT NULL,

    CONSTRAINT PK_Fact_Identity_Links PRIMARY KEY CLUSTERED (identity_link_sk),
    CONSTRAINT UQ_Fact_Identity_Links_id UNIQUE (identity_link_id),
    CONSTRAINT UQ_Fact_Identity_Links_anon_id UNIQUE (anonymous_id)  -- one link per anonymous_id
);
GO
