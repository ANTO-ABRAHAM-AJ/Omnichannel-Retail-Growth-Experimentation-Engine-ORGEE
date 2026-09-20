/*
    ORGEE — Phase 3: Dim_Experiment
    Grain: one row per experiment_id
    Source: experiments.csv
    Type 1 SCD — overwrite on reload
*/

IF OBJECT_ID('dbo.Dim_Experiment', 'U') IS NOT NULL
    DROP TABLE dbo.Dim_Experiment;
GO

CREATE TABLE dbo.Dim_Experiment (
    experiment_sk       INT             IDENTITY(1,1)  NOT NULL,
    experiment_id        VARCHAR(20)                   NOT NULL,  -- e.g. 'exp_001'
    experiment_name       VARCHAR(50)                  NULL,
    objective              VARCHAR(60)                 NULL,  -- fix: was VARCHAR(20), real values run to 47 chars
    start_timestamp         DATETIME2                  NULL,
    end_timestamp            DATETIME2                 NULL,
    primary_metric            VARCHAR(50)               NULL,      -- locked: purchase_conversion_rate
    control_variant_label      VARCHAR(60)              NULL,
    treatment_variant_label     VARCHAR(60)              NULL,
    load_timestamp               DATETIME2  DEFAULT SYSUTCDATETIME() NOT NULL,

    CONSTRAINT PK_Dim_Experiment PRIMARY KEY CLUSTERED (experiment_sk),
    CONSTRAINT UQ_Dim_Experiment_experiment_id UNIQUE (experiment_id)
);
GO
