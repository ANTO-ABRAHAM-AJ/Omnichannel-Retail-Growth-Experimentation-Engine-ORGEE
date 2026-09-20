/*
    ============================================================
    ORGEE — Phase 8: Experimentation Framework
    02_experiment_population.sql
    ============================================================

    BUSINESS QUESTION
    Who is the clean, valid analysis population for this
    experiment — and does the assignment data itself hold up to
    scrutiny before we trust anything built on top of it?

    POPULATION LAYERS (per the plan, and per the lesson learned in
    Phase 7 about population mismatches):
        ASSIGNED  = every customer with an exp_001 assignment
                    (99,441, confirmed in Script 01).
        ELIGIBLE  = assigned customers who actually appear in
                    Fact_Recommendation_Events for exp_001 — i.e.
                    they had qualifying session activity during the
                    experiment window and therefore could have
                    converted. An assigned customer with zero
                    recommendation events was never actually exposed
                    to either experience and cannot meaningfully be
                    counted as a "did not convert" — they were never
                    in the game at all.
        ANALYZED  = eligible customers with valid, usable outcome
                    data. For this dataset, ANALYZED = ELIGIBLE — no
                    further filtering is warranted (every eligible
                    customer's recommendation events are already
                    complete data; there is no partial/corrupted
                    record concept in this table). Stated explicitly
                    rather than inventing an unneeded extra filter.

    OUTPUT
    expt.experiment_population (schema) — one row per customer
    assigned to exp_001, with variant and an is_eligible flag,
    that Scripts 03-08 will all build on.

    TECHNIQUES USED
    Schema creation, CTE, data-quality validation queries.
    ============================================================
*/

IF SCHEMA_ID('expt') IS NULL
    EXEC('CREATE SCHEMA expt');
GO

DECLARE @Exp1Sk INT = (SELECT experiment_sk FROM dbo.Dim_Experiment WHERE experiment_id = 'exp_001');

-- ------------------------------------------------------------
-- Data quality checks on the raw assignment data BEFORE trusting
-- it as the population source
-- ------------------------------------------------------------

SELECT
    'Duplicate assignments (customer assigned >1x to exp_001)' AS check_name,
    COUNT(*) AS violation_count
FROM (
    SELECT customer_sk FROM dbo.Fact_Experiment_Assignments
    WHERE experiment_sk = @Exp1Sk
    GROUP BY customer_sk HAVING COUNT(*) > 1
) x

UNION ALL

SELECT
    'Invalid variant values (not control/treatment)',
    COUNT(*)
FROM dbo.Fact_Experiment_Assignments
WHERE experiment_sk = @Exp1Sk AND variant NOT IN ('control', 'treatment')

UNION ALL

SELECT
    'Missing/NULL customer_sk in assignment',
    COUNT(*)
FROM dbo.Fact_Experiment_Assignments
WHERE experiment_sk = @Exp1Sk AND customer_sk IS NULL

UNION ALL

SELECT
    'Recommendation events referencing an unassigned customer',
    COUNT(*)
FROM dbo.Fact_Recommendation_Events fre
WHERE fre.experiment_sk = @Exp1Sk
  AND NOT EXISTS (
      SELECT 1 FROM dbo.Fact_Experiment_Assignments fea
      WHERE fea.experiment_sk = fre.experiment_sk AND fea.customer_sk = fre.customer_sk
  );

-- ------------------------------------------------------------
-- Build the persistent experiment population table
-- ------------------------------------------------------------

IF OBJECT_ID('expt.experiment_population', 'U') IS NOT NULL DROP TABLE expt.experiment_population;

;WITH EligibleCustomers AS (
    SELECT DISTINCT customer_sk
    FROM dbo.Fact_Recommendation_Events
    WHERE experiment_sk = @Exp1Sk
)
SELECT
    fea.customer_sk,
    fea.variant,
    fea.assignment_timestamp,
    CASE WHEN ec.customer_sk IS NOT NULL THEN 1 ELSE 0 END AS is_eligible
INTO expt.experiment_population
FROM dbo.Fact_Experiment_Assignments fea
LEFT JOIN EligibleCustomers ec ON ec.customer_sk = fea.customer_sk
WHERE fea.experiment_sk = @Exp1Sk;

-- ------------------------------------------------------------
-- Population funnel: Assigned -> Eligible -> Analyzed, by variant
-- ------------------------------------------------------------

SELECT
    variant,
    COUNT(*) AS assigned_participants,
    SUM(is_eligible) AS eligible_participants,
    SUM(is_eligible) AS analyzed_participants,  -- ANALYZED = ELIGIBLE, per the design note above
    ROUND(100.0 * SUM(is_eligible) / COUNT(*), 2) AS pct_eligible_of_assigned
FROM expt.experiment_population
GROUP BY variant

UNION ALL

SELECT
    'TOTAL',
    COUNT(*),
    SUM(is_eligible),
    SUM(is_eligible),
    ROUND(100.0 * SUM(is_eligible) / COUNT(*), 2)
FROM expt.experiment_population;

/*
    BUSINESS INTERPRETATION — fill in after running:
    - Do all 4 data-quality checks come back at 0 (a clean
      assignment mechanism), or is there something to investigate?
    - What fraction of assigned customers are actually eligible
      (had real exposure), and is that fraction similar between
      Control and Treatment?

    BUSINESS IMPLICATION — fill in after running:
    - The ELIGIBLE population (not the assigned 99,441) is what
      Script 03's SRM check and all subsequent metrics should be
      based on — the assigned count only tells us who WOULD have
      been exposed, not who actually was
*/
