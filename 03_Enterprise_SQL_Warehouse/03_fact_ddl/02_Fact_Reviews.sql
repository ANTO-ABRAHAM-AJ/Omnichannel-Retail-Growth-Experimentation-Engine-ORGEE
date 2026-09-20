/*
    ORGEE — Phase 3: Fact_Reviews
    Grain: one row per review_id
    Source: olist_order_reviews_dataset.csv
             JOIN olist_orders_dataset.csv (to get customer_id for the FK)
*/

IF OBJECT_ID('dbo.Fact_Reviews', 'U') IS NOT NULL
    DROP TABLE dbo.Fact_Reviews;
GO

CREATE TABLE dbo.Fact_Reviews (
    review_sk               BIGINT          IDENTITY(1,1)  NOT NULL,

    review_id                 VARCHAR(32)                  NOT NULL,
    order_id                    VARCHAR(32)                NOT NULL,

    customer_sk               INT                          NULL,
    review_creation_date_sk      INT                       NULL,
    review_answer_date_sk          INT                     NULL,

    review_score                 TINYINT                   NULL,   -- 1-5
    review_comment_title            VARCHAR(60)             NULL,
    review_comment_message            VARCHAR(MAX)          NULL,

    load_timestamp                DATETIME2  DEFAULT SYSUTCDATETIME() NOT NULL,

    CONSTRAINT PK_Fact_Reviews PRIMARY KEY CLUSTERED (review_sk),
    -- fix: grain is actually (review_id, order_id), not review_id
    -- alone — the public Olist dataset has 1,603 rows where the same
    -- review_id legitimately appears against a different order_id.
    CONSTRAINT UQ_Fact_Reviews_review_order UNIQUE (review_id, order_id)
);
GO
