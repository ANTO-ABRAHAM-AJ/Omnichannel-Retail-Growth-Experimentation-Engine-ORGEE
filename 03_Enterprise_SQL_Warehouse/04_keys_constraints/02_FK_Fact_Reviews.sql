/*
    ORGEE — Phase 3: Foreign Keys — Fact_Reviews
*/

ALTER TABLE dbo.Fact_Reviews
    ADD CONSTRAINT FK_FactReviews_Customer
        FOREIGN KEY (customer_sk) REFERENCES dbo.Dim_Customer (customer_sk);

ALTER TABLE dbo.Fact_Reviews
    ADD CONSTRAINT FK_FactReviews_CreationDate
        FOREIGN KEY (review_creation_date_sk) REFERENCES dbo.Dim_Date (date_sk);

ALTER TABLE dbo.Fact_Reviews
    ADD CONSTRAINT FK_FactReviews_AnswerDate
        FOREIGN KEY (review_answer_date_sk) REFERENCES dbo.Dim_Date (date_sk);
GO
