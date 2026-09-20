/*
    ORGEE — Phase 3: Foreign Keys — Fact_Sessions
*/

ALTER TABLE dbo.Fact_Sessions
    ADD CONSTRAINT FK_FactSessions_Customer
        FOREIGN KEY (customer_sk) REFERENCES dbo.Dim_Customer (customer_sk);

ALTER TABLE dbo.Fact_Sessions
    ADD CONSTRAINT FK_FactSessions_Device
        FOREIGN KEY (device_sk) REFERENCES dbo.Dim_Device (device_sk);

ALTER TABLE dbo.Fact_Sessions
    ADD CONSTRAINT FK_FactSessions_StartDate
        FOREIGN KEY (session_start_date_sk) REFERENCES dbo.Dim_Date (date_sk);
GO
