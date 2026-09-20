/*
    ORGEE — Phase 3: Foreign Keys — Fact_Experiment_Assignments
*/

ALTER TABLE dbo.Fact_Experiment_Assignments
    ADD CONSTRAINT FK_FactExperimentAssignments_Experiment
        FOREIGN KEY (experiment_sk) REFERENCES dbo.Dim_Experiment (experiment_sk);

ALTER TABLE dbo.Fact_Experiment_Assignments
    ADD CONSTRAINT FK_FactExperimentAssignments_Customer
        FOREIGN KEY (customer_sk) REFERENCES dbo.Dim_Customer (customer_sk);

ALTER TABLE dbo.Fact_Experiment_Assignments
    ADD CONSTRAINT FK_FactExperimentAssignments_Date
        FOREIGN KEY (assignment_date_sk) REFERENCES dbo.Dim_Date (date_sk);
GO
