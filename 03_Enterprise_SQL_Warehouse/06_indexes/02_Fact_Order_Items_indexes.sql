/*
    ORGEE — Phase 3: Indexes — Fact_Order_Items
    Supports revenue trends, customer purchase analysis, product/seller
    performance queries (Phase 4/6).
*/

CREATE NONCLUSTERED INDEX IX_FactOrderItems_CustomerSk
    ON dbo.Fact_Order_Items (customer_sk)
    WHERE customer_sk IS NOT NULL;
GO

CREATE NONCLUSTERED INDEX IX_FactOrderItems_ProductSk
    ON dbo.Fact_Order_Items (product_sk)
    INCLUDE (price, freight_value);
GO

CREATE NONCLUSTERED INDEX IX_FactOrderItems_SellerSk
    ON dbo.Fact_Order_Items (seller_sk);
GO

CREATE NONCLUSTERED INDEX IX_FactOrderItems_PurchaseDateSk
    ON dbo.Fact_Order_Items (order_purchase_date_sk)
    INCLUDE (price, payment_value_order_total);
GO
