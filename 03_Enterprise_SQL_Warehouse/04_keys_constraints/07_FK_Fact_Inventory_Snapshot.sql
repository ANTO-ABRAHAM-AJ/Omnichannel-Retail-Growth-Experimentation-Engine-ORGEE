/*
    ORGEE — Phase 3: Foreign Keys — Fact_Inventory_Snapshot
*/

ALTER TABLE dbo.Fact_Inventory_Snapshot
    ADD CONSTRAINT FK_FactInventorySnapshot_Product
        FOREIGN KEY (product_sk) REFERENCES dbo.Dim_Product (product_sk);

ALTER TABLE dbo.Fact_Inventory_Snapshot
    ADD CONSTRAINT FK_FactInventorySnapshot_Date
        FOREIGN KEY (observation_date_sk) REFERENCES dbo.Dim_Date (date_sk);
GO
