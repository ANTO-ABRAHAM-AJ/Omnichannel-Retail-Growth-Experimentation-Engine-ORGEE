/*
    ORGEE — Phase 3: Indexes — Fact_Events
    3,000,000 rows — the largest table in the warehouse.

    A CLUSTERED COLUMNSTORE INDEX replaces the need for a traditional
    clustered B-tree here: it compresses this table dramatically
    (columnstore is built for exactly this — a wide, write-once,
    scan-heavy fact table) and is far faster for the aggregation-heavy
    queries Phase 4/5 will run (funnels, cohort counts, event-type
    breakdowns over millions of rows).

    This coexists fine with the NONCLUSTERED primary key we
    deliberately declared back in 03_fact_ddl — SQL Server supports a
    clustered columnstore index alongside nonclustered B-tree indexes
    for point lookups, which is exactly the combination used below.
*/

CREATE CLUSTERED COLUMNSTORE INDEX CCI_Fact_Events
    ON dbo.Fact_Events;
GO

-- Point-lookup / join-pattern indexes on top of the columnstore.
-- Filtered indexes are used on customer_sk since it's only populated
-- for ~18% of events (post-login) — indexing just those rows keeps
-- the index small and fast rather than wasting space on 82% NULLs.

CREATE NONCLUSTERED INDEX IX_FactEvents_SessionId
    ON dbo.Fact_Events (session_id);
GO

CREATE NONCLUSTERED INDEX IX_FactEvents_CustomerSk
    ON dbo.Fact_Events (customer_sk)
    WHERE customer_sk IS NOT NULL;
GO

CREATE NONCLUSTERED INDEX IX_FactEvents_EventDateSk
    ON dbo.Fact_Events (event_date_sk);
GO

CREATE NONCLUSTERED INDEX IX_FactEvents_EventType
    ON dbo.Fact_Events (event_type)
    INCLUDE (event_date_sk, session_id);
GO
