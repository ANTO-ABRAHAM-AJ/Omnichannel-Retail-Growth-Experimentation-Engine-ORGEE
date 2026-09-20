/*
    ORGEE — Phase 3: Indexes — Fact_Reviews
*/

CREATE NONCLUSTERED INDEX IX_FactReviews_CustomerSk
    ON dbo.Fact_Reviews (customer_sk)
    WHERE customer_sk IS NOT NULL;
GO

CREATE NONCLUSTERED INDEX IX_FactReviews_CreationDateSk
    ON dbo.Fact_Reviews (review_creation_date_sk)
    INCLUDE (review_score);
GO
