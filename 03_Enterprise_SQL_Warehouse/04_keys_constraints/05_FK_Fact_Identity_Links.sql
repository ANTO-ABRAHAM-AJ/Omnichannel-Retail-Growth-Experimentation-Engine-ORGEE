/*
    ORGEE — Phase 3: Foreign Keys — Fact_Identity_Links
*/

ALTER TABLE dbo.Fact_Identity_Links
    ADD CONSTRAINT FK_FactIdentityLinks_Customer
        FOREIGN KEY (customer_sk) REFERENCES dbo.Dim_Customer (customer_sk);

ALTER TABLE dbo.Fact_Identity_Links
    ADD CONSTRAINT FK_FactIdentityLinks_Date
        FOREIGN KEY (link_date_sk) REFERENCES dbo.Dim_Date (date_sk);

ALTER TABLE dbo.Fact_Identity_Links
    ADD CONSTRAINT FK_FactIdentityLinks_Session
        FOREIGN KEY (session_id) REFERENCES dbo.Fact_Sessions (session_id);
GO
