/*
    ORGEE — Phase 3: Fact_Order_Items
    Grain: one row per order line item (order_id, order_item_id)
    Source: olist_order_items_dataset.csv
             LEFT JOIN olist_order_payments_dataset.csv (aggregated per order_id)
             LEFT JOIN olist_orders_dataset.csv (for order_status, purchase date -> date_sk)
    Payments are rolled up per order_id (SUM payment_value, MAX installments,
    a representative payment_type) and repeated across that order's line
    items — see design decision in 01_schema_design.
*/

IF OBJECT_ID('dbo.Fact_Order_Items', 'U') IS NOT NULL
    DROP TABLE dbo.Fact_Order_Items;
GO

CREATE TABLE dbo.Fact_Order_Items (
    order_item_sk         BIGINT          IDENTITY(1,1)  NOT NULL,

    -- degenerate dimensions (natural keys, kept on the fact directly)
    order_id               VARCHAR(32)                   NOT NULL,
    order_item_id           SMALLINT                     NOT NULL,
    order_status              VARCHAR(20)                NULL,

    -- foreign keys
    customer_sk            INT                           NULL,
    product_sk               INT                          NULL,
    seller_sk                  INT                        NULL,
    order_purchase_date_sk       INT                      NULL,

    -- measures
    price                    DECIMAL(10,2)                NULL,
    freight_value              DECIMAL(10,2)              NULL,
    payment_value_order_total    DECIMAL(10,2)            NULL,   -- SUM(payment_value) per order_id
    payment_installments_max       TINYINT                NULL,   -- MAX(payment_installments) per order_id
    payment_type_primary             VARCHAR(20)          NULL,   -- most common payment_type per order_id

    load_timestamp             DATETIME2  DEFAULT SYSUTCDATETIME() NOT NULL,

    CONSTRAINT PK_Fact_Order_Items PRIMARY KEY CLUSTERED (order_item_sk)
);
GO
