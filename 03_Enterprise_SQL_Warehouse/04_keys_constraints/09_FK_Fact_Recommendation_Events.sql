/*
    ORGEE — Phase 3: Foreign Keys — Fact_Recommendation_Events
*/

ALTER TABLE dbo.Fact_Recommendation_Events
    ADD CONSTRAINT FK_FactRecommendationEvents_Experiment
        FOREIGN KEY (experiment_sk) REFERENCES dbo.Dim_Experiment (experiment_sk);

ALTER TABLE dbo.Fact_Recommendation_Events
    ADD CONSTRAINT FK_FactRecommendationEvents_Customer
        FOREIGN KEY (customer_sk) REFERENCES dbo.Dim_Customer (customer_sk);

ALTER TABLE dbo.Fact_Recommendation_Events
    ADD CONSTRAINT FK_FactRecommendationEvents_Product
        FOREIGN KEY (product_sk) REFERENCES dbo.Dim_Product (product_sk);

ALTER TABLE dbo.Fact_Recommendation_Events
    ADD CONSTRAINT FK_FactRecommendationEvents_Date
        FOREIGN KEY (event_date_sk) REFERENCES dbo.Dim_Date (date_sk);
GO
