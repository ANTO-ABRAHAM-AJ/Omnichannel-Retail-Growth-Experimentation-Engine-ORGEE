/*
    ORGEE — Phase 3: Indexes — Fact_Identity_Links
    Small table (~90K rows) — customer_sk and anonymous_id already
    have UNIQUE constraints from 03_fact_ddl (which create their own
    supporting indexes), so only the date dimension needs one here.
*/

CREATE NONCLUSTERED INDEX IX_FactIdentityLinks_LinkDateSk
    ON dbo.Fact_Identity_Links (link_date_sk);
GO
