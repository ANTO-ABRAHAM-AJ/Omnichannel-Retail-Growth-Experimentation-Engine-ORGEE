/*
    ORGEE — Phase 3: Indexes — Fact_Sessions
    Supports funnel/journey/cohort analysis (Phase 5) — the primary
    consumer of this table.
*/

CREATE NONCLUSTERED INDEX IX_FactSessions_CustomerSk
    ON dbo.Fact_Sessions (customer_sk)
    WHERE customer_sk IS NOT NULL;
GO

CREATE NONCLUSTERED INDEX IX_FactSessions_StartDateSk
    ON dbo.Fact_Sessions (session_start_date_sk);
GO

CREATE NONCLUSTERED INDEX IX_FactSessions_DeviceSk
    ON dbo.Fact_Sessions (device_sk);
GO
