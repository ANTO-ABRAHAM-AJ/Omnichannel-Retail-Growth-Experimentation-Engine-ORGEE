/*
    ORGEE — Phase 3: Fact_Recommendation_Events
    Grain: one row per recommendation interaction (impression/click/conversion)
    Source: recommendation_events.csv
    This is the table Phase 8's primary metric (purchase conversion
    rate) and secondary metrics (CTR, AOV, revenue/user) will be
    computed from, split by variant.

    NOTE: customer_sk is nullable. Per the sizing decision after the
    Phase 2 fix, only sessions with a resolved identity are eligible
    for personalized recommendations, but the eligibility join
    happens upstream in generation — customer_sk should be populated
    for effectively all rows here. Left nullable defensively.
*/

IF OBJECT_ID('dbo.Fact_Recommendation_Events', 'U') IS NOT NULL
    DROP TABLE dbo.Fact_Recommendation_Events;
GO

CREATE TABLE dbo.Fact_Recommendation_Events (
    recommendation_event_sk    BIGINT          IDENTITY(1,1)  NOT NULL,

    recommendation_event_id       VARCHAR(24)                 NOT NULL,
    session_id                       VARCHAR(20)               NULL,
    anonymous_id                        VARCHAR(20)             NULL,

    experiment_sk                          INT                  NULL,
    customer_sk                               INT                NULL,
    product_sk                                   INT              NULL,
    event_date_sk                                   INT           NULL,

    event_timestamp                                DATETIME2       NOT NULL,
    variant                                           VARCHAR(10)   NULL,   -- control, treatment
    event_type                                          VARCHAR(30) NOT NULL, -- recommendation_impression,
                                                                              -- recommendation_click,
                                                                              -- recommendation_conversion

    load_timestamp                                        DATETIME2  DEFAULT SYSUTCDATETIME() NOT NULL,

    CONSTRAINT PK_Fact_Recommendation_Events PRIMARY KEY CLUSTERED (recommendation_event_sk),
    CONSTRAINT UQ_Fact_Recommendation_Events_id UNIQUE (recommendation_event_id)
);
GO
