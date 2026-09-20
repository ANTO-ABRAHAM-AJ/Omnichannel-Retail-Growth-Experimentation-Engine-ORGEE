/*
    ORGEE — Phase 3: Indexes — Fact_Experiment_Assignments
    This is the table Phase 8's SRM check and variant-level analysis
    will query most — index the columns that split/group by variant.
*/

CREATE NONCLUSTERED INDEX IX_FactExperimentAssignments_ExperimentSk
    ON dbo.Fact_Experiment_Assignments (experiment_sk)
    INCLUDE (variant);
GO

CREATE NONCLUSTERED INDEX IX_FactExperimentAssignments_CustomerSk
    ON dbo.Fact_Experiment_Assignments (customer_sk);
GO
