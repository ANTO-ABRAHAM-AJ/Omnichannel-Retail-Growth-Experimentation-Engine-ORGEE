/*
    ORGEE — Phase 3: Fact_Experiment_Assignments
    Grain: one row per (customer_id, experiment_id) assignment
    Source: experiment_assignments.csv
    Type: factless fact table — records which variant (control/
    treatment) each customer was assigned to. This is the table
    Phase 8's SRM check and statistical readout will query.
*/

IF OBJECT_ID('dbo.Fact_Experiment_Assignments', 'U') IS NOT NULL
    DROP TABLE dbo.Fact_Experiment_Assignments;
GO

CREATE TABLE dbo.Fact_Experiment_Assignments (
    experiment_assignment_sk    BIGINT          IDENTITY(1,1)  NOT NULL,

    experiment_assignment_id       VARCHAR(30)                 NOT NULL,

    experiment_sk                    INT                        NOT NULL,
    customer_sk                         INT                     NOT NULL,
    assignment_date_sk                     INT                  NULL,

    assignment_timestamp                  DATETIME2              NOT NULL,
    variant                                  VARCHAR(10)          NOT NULL,  -- control, treatment

    load_timestamp                              DATETIME2  DEFAULT SYSUTCDATETIME() NOT NULL,

    CONSTRAINT PK_Fact_Experiment_Assignments PRIMARY KEY CLUSTERED (experiment_assignment_sk),
    CONSTRAINT UQ_Fact_Experiment_Assignments_id UNIQUE (experiment_assignment_id),
    CONSTRAINT UQ_Fact_Experiment_Assignments_combo UNIQUE (experiment_sk, customer_sk)
);
GO
