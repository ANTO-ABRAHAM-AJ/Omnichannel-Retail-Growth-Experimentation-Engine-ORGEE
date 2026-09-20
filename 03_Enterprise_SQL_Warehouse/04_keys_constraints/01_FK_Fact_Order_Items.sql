/*
    ORGEE — Phase 3: Foreign Keys — Fact_Order_Items
*/

ALTER TABLE dbo.Fact_Order_Items
    ADD CONSTRAINT FK_FactOrderItems_Customer
        FOREIGN KEY (customer_sk) REFERENCES dbo.Dim_Customer (customer_sk);

ALTER TABLE dbo.Fact_Order_Items
    ADD CONSTRAINT FK_FactOrderItems_Product
        FOREIGN KEY (product_sk) REFERENCES dbo.Dim_Product (product_sk);

ALTER TABLE dbo.Fact_Order_Items
    ADD CONSTRAINT FK_FactOrderItems_Seller
        FOREIGN KEY (seller_sk) REFERENCES dbo.Dim_Seller (seller_sk);

ALTER TABLE dbo.Fact_Order_Items
    ADD CONSTRAINT FK_FactOrderItems_Date
        FOREIGN KEY (order_purchase_date_sk) REFERENCES dbo.Dim_Date (date_sk);
GO
