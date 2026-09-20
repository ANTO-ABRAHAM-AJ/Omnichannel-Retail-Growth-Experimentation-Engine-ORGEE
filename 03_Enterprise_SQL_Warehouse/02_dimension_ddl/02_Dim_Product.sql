/*
    ORGEE — Phase 3: Dim_Product
    Grain: one row per product_id
    Source: olist_products_dataset.csv LEFT JOIN product_category_name_translation.csv
    Type 1 SCD — overwrite on reload
*/

IF OBJECT_ID('dbo.Dim_Product', 'U') IS NOT NULL
    DROP TABLE dbo.Dim_Product;
GO

CREATE TABLE dbo.Dim_Product (
    product_sk                  INT            IDENTITY(1,1)  NOT NULL,
    product_id                  VARCHAR(32)                   NOT NULL,
    product_category_name       VARCHAR(60)                   NULL,
    product_category_name_english VARCHAR(60)                 NULL,
    product_name_length         INT                           NULL,
    product_description_length  INT                           NULL,
    product_photos_qty          INT                           NULL,
    product_weight_g            DECIMAL(10,2)                 NULL,
    product_length_cm           DECIMAL(10,2)                 NULL,
    product_height_cm           DECIMAL(10,2)                 NULL,
    product_width_cm            DECIMAL(10,2)                 NULL,
    load_timestamp              DATETIME2      DEFAULT SYSUTCDATETIME() NOT NULL,

    CONSTRAINT PK_Dim_Product PRIMARY KEY CLUSTERED (product_sk),
    CONSTRAINT UQ_Dim_Product_product_id UNIQUE (product_id)
);
GO
