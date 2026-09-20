/*
    ORGEE — Phase 3: Fact_Sessions
    Grain: one row per session_id
    Source: sessions.csv

    NOTE: customer_sk is NULLABLE. Per the Phase 2 identity-resolution
    fix, a session only carries a known customer_id once a successful
    login event occurred within it (~18% of sessions). The remaining
    ~82% are legitimately anonymous. Always LEFT JOIN Dim_Customer here
    — an inner join will silently drop most rows.
*/

IF OBJECT_ID('dbo.Fact_Sessions', 'U') IS NOT NULL
    DROP TABLE dbo.Fact_Sessions;
GO

CREATE TABLE dbo.Fact_Sessions (
    session_sk              BIGINT          IDENTITY(1,1)  NOT NULL,

    session_id                VARCHAR(20)                  NOT NULL,   -- e.g. 'sess_000000001'
    anonymous_id                VARCHAR(20)                NOT NULL,   -- e.g. 'anon_000000001'

    customer_sk              INT                           NULL,       -- nullable: anonymous until login
    device_sk                   INT                        NULL,
    session_start_date_sk         INT                      NULL,

    session_start_timestamp    DATETIME2                   NOT NULL,
    session_end_timestamp        DATETIME2                 NOT NULL,
    session_duration_seconds       AS DATEDIFF(
                                        SECOND,
                                        session_start_timestamp,
                                        session_end_timestamp
                                    ) PERSISTED,
    session_type                    VARCHAR(10)             NULL,      -- short, medium, long
    expected_event_count               SMALLINT             NULL,

    load_timestamp                     DATETIME2  DEFAULT SYSUTCDATETIME() NOT NULL,

    CONSTRAINT PK_Fact_Sessions PRIMARY KEY CLUSTERED (session_sk),
    CONSTRAINT UQ_Fact_Sessions_session_id UNIQUE (session_id)
);
GO
