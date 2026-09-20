/*
    ORGEE — Phase 3: Fix — Fact_Reviews grain correction

    Original assumption: one row per review_id. WRONG — the public
    Olist review dataset genuinely contains 1,603 rows where the same
    review_id appears against a DIFFERENT order_id (customers leaving
    what looks like the same review text on more than one order, or a
    resubmission — this is a known quirk of the public dataset, not
    something introduced in this project). Verified: (review_id,
    order_id) together ARE unique across all 99,224 rows.

    This script:
      1. Drops the too-strict UNIQUE constraint on review_id alone
      2. Adds the correct composite UNIQUE constraint
      3. Reloads Fact_Reviews (it inserted 0 rows last time — the
         whole statement rolled back on the first duplicate)

    Run this ONCE. It only touches Fact_Reviews — your other 8 fact
    tables from 04_load_facts.sql are untouched.
*/

ALTER TABLE dbo.Fact_Reviews
    DROP CONSTRAINT UQ_Fact_Reviews_review_id;
GO

ALTER TABLE dbo.Fact_Reviews
    ADD CONSTRAINT UQ_Fact_Reviews_review_order UNIQUE (review_id, order_id);
GO

;WITH ReviewsConv AS (
    SELECT
        review_id, order_id,
        TRY_CONVERT(TINYINT, review_score)                            AS review_score,
        review_comment_title, review_comment_message,
        TRY_CONVERT(DATETIME2(7), review_creation_date, 120)             AS review_creation_date,
        TRY_CONVERT(DATETIME2(7), review_answer_timestamp, 120)            AS review_answer_timestamp
    FROM staging.stg_order_reviews
)
INSERT INTO dbo.Fact_Reviews (
    review_id, order_id, customer_sk, review_creation_date_sk,
    review_answer_date_sk, review_score, review_comment_title, review_comment_message
)
SELECT
    r.review_id, r.order_id, dc.customer_sk,
    CAST(CONVERT(VARCHAR(8), r.review_creation_date, 112) AS INT),
    CAST(CONVERT(VARCHAR(8), r.review_answer_timestamp, 112) AS INT),
    r.review_score, r.review_comment_title, r.review_comment_message
FROM ReviewsConv r
JOIN staging.stg_orders o      ON r.order_id = o.order_id
LEFT JOIN dbo.Dim_Customer dc  ON o.customer_id = dc.customer_id;

SELECT 'Fact_Reviews' AS fact_table, COUNT(*) AS row_count FROM dbo.Fact_Reviews;
