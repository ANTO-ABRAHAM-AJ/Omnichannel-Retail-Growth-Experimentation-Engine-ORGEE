/*
    ORGEE — Phase 3: Fix — Dim_Experiment.objective was too narrow
    Original DDL: VARCHAR(20). Actual data needs up to 47 characters.
    Run this once. It only touches Dim_Experiment — your other 6
    dimensions (Customer, Product, Seller, Campaign, Device, Date)
    already loaded successfully and are untouched by this script.
*/

ALTER TABLE dbo.Dim_Experiment
    ALTER COLUMN objective VARCHAR(60) NULL;
GO

-- Re-run just the Dim_Experiment load (it inserted 0 rows last time
-- since the whole statement was rolled back on the truncation error)

INSERT INTO dbo.Dim_Experiment (
    experiment_id, experiment_name, objective, start_timestamp,
    end_timestamp, primary_metric, control_variant_label, treatment_variant_label
)
SELECT
    experiment_id, experiment_name, objective,
    TRY_CONVERT(DATETIME2(7), start_timestamp, 120),
    TRY_CONVERT(DATETIME2(7), end_timestamp, 120),
    primary_metric, control_variant, treatment_variant
FROM staging.stg_experiments;

SELECT 'Dim_Experiment' AS dim_table, COUNT(*) AS row_count FROM dbo.Dim_Experiment;
