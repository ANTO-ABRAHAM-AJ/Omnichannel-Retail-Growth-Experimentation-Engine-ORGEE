/*
    ORGEE — Phase 3: Dim_Customer
    Grain: one row per customer_id (public Olist customer)
    Source: olist_customers_dataset.csv
    Type 1 SCD — overwrite on reload
*/

IF OBJECT_ID('dbo.Dim_Customer', 'U') IS NOT NULL
    DROP TABLE dbo.Dim_Customer;
GO

CREATE TABLE dbo.Dim_Customer (
    customer_sk             INT             IDENTITY(1,1)   NOT NULL,
    customer_id             VARCHAR(32)                     NOT NULL,
    customer_unique_id      VARCHAR(32)                     NOT NULL,
    customer_zip_code_prefix VARCHAR(10)                    NULL,
    customer_city           VARCHAR(50)                     NULL,
    customer_state          CHAR(2)                         NULL,
    load_timestamp          DATETIME2       DEFAULT SYSUTCDATETIME() NOT NULL,

    CONSTRAINT PK_Dim_Customer PRIMARY KEY CLUSTERED (customer_sk),
    CONSTRAINT UQ_Dim_Customer_customer_id UNIQUE (customer_id)
);
GO
