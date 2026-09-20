/*
    ORGEE — Phase 3: Indexes — Fact_Campaign_Exposures
    1,000,000 rows — supports marketing performance analysis
    (Phase 9 marketing dashboard, if the data supports it).
*/

CREATE NONCLUSTERED INDEX IX_FactCampaignExposures_CampaignSk
    ON dbo.Fact_Campaign_Exposures (campaign_sk)
    INCLUDE (exposure_outcome);
GO

CREATE NONCLUSTERED INDEX IX_FactCampaignExposures_CustomerSk
    ON dbo.Fact_Campaign_Exposures (customer_sk)
    WHERE customer_sk IS NOT NULL;
GO

CREATE NONCLUSTERED INDEX IX_FactCampaignExposures_ExposureDateSk
    ON dbo.Fact_Campaign_Exposures (exposure_date_sk);
GO
