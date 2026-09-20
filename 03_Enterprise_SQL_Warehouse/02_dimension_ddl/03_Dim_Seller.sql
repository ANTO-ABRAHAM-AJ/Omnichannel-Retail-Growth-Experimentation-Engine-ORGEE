/*
    ORGEE — Phase 3: Dim_Seller
    Grain: one row per seller_id
    Source: olist_sellers_dataset.csv
    Type 1 SCD — overwrite on reload
*/

IF OBJECT_ID('dbo.Dim_Seller', 'U') IS NOT NULL
    DROP TABLE dbo.Dim_Seller;
GO

CREATE TABLE dbo.Dim_Seller (
    seller_sk               INT             IDENTITY(1,1)   NOT NULL,
    seller_id               VARCHAR(32)                     NOT NULL,
    seller_zip_code_prefix  VARCHAR(10)                     NULL,
    seller_city             VARCHAR(50)                     NULL,
    seller_state            CHAR(2)                         NULL,
    load_timestamp          DATETIME2       DEFAULT SYSUTCDATETIME() NOT NULL,

    CONSTRAINT PK_Dim_Seller PRIMARY KEY CLUSTERED (seller_sk),
    CONSTRAINT UQ_Dim_Seller_seller_id UNIQUE (seller_id)
);
GO
