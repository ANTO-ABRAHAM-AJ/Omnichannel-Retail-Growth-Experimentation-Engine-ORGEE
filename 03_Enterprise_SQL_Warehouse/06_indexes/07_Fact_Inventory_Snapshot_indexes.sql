/*
    ORGEE — Phase 3: Indexes — Fact_Inventory_Snapshot
    1,000,000 rows — periodic snapshot fact, supports inventory
    health / stockout analysis.
*/

CREATE NONCLUSTERED INDEX IX_FactInventorySnapshot_ProductSk
    ON dbo.Fact_Inventory_Snapshot (product_sk)
    INCLUDE (available_quantity, inventory_status);
GO

CREATE NONCLUSTERED INDEX IX_FactInventorySnapshot_ObservationDateSk
    ON dbo.Fact_Inventory_Snapshot (observation_date_sk);
GO

CREATE NONCLUSTERED INDEX IX_FactInventorySnapshot_Status
    ON dbo.Fact_Inventory_Snapshot (inventory_status)
    WHERE inventory_status IN ('low_stock', 'out_of_stock');
GO
