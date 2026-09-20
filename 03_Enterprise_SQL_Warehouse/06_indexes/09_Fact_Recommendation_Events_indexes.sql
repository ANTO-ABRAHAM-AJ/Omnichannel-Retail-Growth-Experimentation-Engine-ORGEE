/*
    ORGEE — Phase 3: Indexes — Fact_Recommendation_Events
    Small table (~10K rows) — this is the table Phase 8's primary
    metric (purchase conversion rate) and secondary metrics (CTR,
    AOV, revenue/user) get computed from, split by variant.
*/

CREATE NONCLUSTERED INDEX IX_FactRecommendationEvents_ExperimentSk
    ON dbo.Fact_Recommendation_Events (experiment_sk)
    INCLUDE (variant, event_type);
GO

CREATE NONCLUSTERED INDEX IX_FactRecommendationEvents_CustomerSk
    ON dbo.Fact_Recommendation_Events (customer_sk)
    WHERE customer_sk IS NOT NULL;
GO
