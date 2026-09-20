/*
    ORGEE — Phase 3: Foreign Keys — Fact_Events
*/

ALTER TABLE dbo.Fact_Events
    ADD CONSTRAINT FK_FactEvents_Customer
        FOREIGN KEY (customer_sk) REFERENCES dbo.Dim_Customer (customer_sk);

ALTER TABLE dbo.Fact_Events
    ADD CONSTRAINT FK_FactEvents_Product
        FOREIGN KEY (product_sk) REFERENCES dbo.Dim_Product (product_sk);

ALTER TABLE dbo.Fact_Events
    ADD CONSTRAINT FK_FactEvents_Device
        FOREIGN KEY (device_sk) REFERENCES dbo.Dim_Device (device_sk);

ALTER TABLE dbo.Fact_Events
    ADD CONSTRAINT FK_FactEvents_Date
        FOREIGN KEY (event_date_sk) REFERENCES dbo.Dim_Date (date_sk);

-- Fact-to-fact reference: ties each event back to its parent session
-- via the natural key (session_id), since Fact_Sessions.session_id
-- carries a UNIQUE constraint.
ALTER TABLE dbo.Fact_Events
    ADD CONSTRAINT FK_FactEvents_Session
        FOREIGN KEY (session_id) REFERENCES dbo.Fact_Sessions (session_id);
GO
