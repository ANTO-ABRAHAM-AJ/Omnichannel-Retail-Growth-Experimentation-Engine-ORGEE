/*
    ORGEE — Phase 3: Foreign Keys — Fact_Campaign_Exposures
*/

ALTER TABLE dbo.Fact_Campaign_Exposures
    ADD CONSTRAINT FK_FactCampaignExposures_Campaign
        FOREIGN KEY (campaign_sk) REFERENCES dbo.Dim_Campaign (campaign_sk);

ALTER TABLE dbo.Fact_Campaign_Exposures
    ADD CONSTRAINT FK_FactCampaignExposures_Customer
        FOREIGN KEY (customer_sk) REFERENCES dbo.Dim_Customer (customer_sk);

ALTER TABLE dbo.Fact_Campaign_Exposures
    ADD CONSTRAINT FK_FactCampaignExposures_Date
        FOREIGN KEY (exposure_date_sk) REFERENCES dbo.Dim_Date (date_sk);
GO
