/*
    ============================================================
    ORGEE — Phase 8: Experimentation Framework
    03_srm_validation.sql ⭐ GATE SCRIPT
    ============================================================

    BUSINESS QUESTION
    Was the experiment assignment itself distributed according to
    the planned 50/50 allocation?

    CORRECTION APPLIED (methodological, not cosmetic): a first
    version of this script ran the chi-square test on the ELIGIBLE
    population (2,223 control / 2,188 treatment) and called that
    "SRM". That is not the canonical definition. SRM (Sample Ratio
    Mismatch) specifically tests the ASSIGNMENT mechanism — did the
    experiment assignment remain consistent with the planned split?
    That question can only be answered on the ASSIGNED population
    (49,720 / 49,721), which is what this script now tests as the
    PRIMARY gate. The eligible-population comparison is still a
    real, useful diagnostic — it just measures something different
    (whether something AFTER assignment, e.g. differential session
    activity, introduced an imbalance in who actually got exposed)
    — so it's kept here as a clearly separate, explicitly-labeled
    INFORMATIONAL check, not conflated with SRM.

    METHOD: Chi-Square Goodness-of-Fit test, 1 degree of freedom,
    compared against the same three standard critical values as
    before (3.841 / 6.635 / 10.828 for p<0.05/0.01/0.001).

    DECISION: PASS = proceed to Script 04. FAIL = stop and
    investigate the assignment mechanism before trusting anything
    built on top of it.

    TECHNIQUES USED
    Aggregation, chi-square goodness-of-fit arithmetic.
    ============================================================
*/

-- ============================================================
-- PRIMARY: SRM check on the ASSIGNED population (the canonical
-- definition — tests the randomization mechanism itself)
-- ============================================================

;WITH Observed AS (
    SELECT variant, COUNT(*) AS observed_count
    FROM expt.experiment_population
    GROUP BY variant
),
Totals AS (
    SELECT SUM(observed_count) AS total_assigned FROM Observed
),
ChiSquare AS (
    SELECT
        o.variant,
        o.observed_count,
        t.total_assigned * 0.5 AS expected_count,
        SQUARE(o.observed_count - t.total_assigned * 0.5) / (t.total_assigned * 0.5) AS chi_sq_contribution
    FROM Observed o
    CROSS JOIN Totals t
)
SELECT
    variant,
    observed_count,
    expected_count,
    ROUND(100.0 * observed_count / SUM(observed_count) OVER (), 4) AS observed_pct,
    ROUND(chi_sq_contribution, 6) AS chi_sq_contribution
FROM ChiSquare

UNION ALL

SELECT
    'TOTAL / CHI-SQUARE STATISTIC',
    SUM(observed_count),
    SUM(expected_count),
    100.00,
    ROUND(SUM(chi_sq_contribution), 6)
FROM ChiSquare;

;WITH Observed AS (
    SELECT variant, COUNT(*) AS observed_count
    FROM expt.experiment_population
    GROUP BY variant
),
Totals AS (
    SELECT SUM(observed_count) AS total_assigned FROM Observed
),
ChiSqStat AS (
    SELECT SUM(SQUARE(o.observed_count - t.total_assigned * 0.5) / (t.total_assigned * 0.5)) AS chi_square_statistic
    FROM Observed o CROSS JOIN Totals t
)
SELECT
    ROUND(chi_square_statistic, 6) AS chi_square_statistic,
    CASE WHEN chi_square_statistic >= 3.841 THEN 'FAIL' ELSE 'PASS' END AS srm_at_p05,
    CASE WHEN chi_square_statistic >= 6.635 THEN 'FAIL' ELSE 'PASS' END AS srm_at_p01,
    CASE WHEN chi_square_statistic >= 10.828 THEN 'FAIL' ELSE 'PASS' END AS srm_at_p001,
    CASE WHEN chi_square_statistic >= 3.841 THEN 'STOP — investigate before Script 04' ELSE 'PROCEED to Script 04' END AS overall_gate_decision
FROM ChiSqStat;

-- ============================================================
-- INFORMATIONAL (NOT SRM): Eligible/Exposed population balance
-- — a separate, useful diagnostic for post-assignment exposure
-- imbalance, explicitly not labeled as the SRM gate
-- ============================================================

;WITH Observed AS (
    SELECT variant, COUNT(*) AS observed_count
    FROM expt.experiment_population
    WHERE is_eligible = 1
    GROUP BY variant
),
Totals AS (
    SELECT SUM(observed_count) AS total_eligible FROM Observed
),
ChiSqStat AS (
    SELECT SUM(SQUARE(o.observed_count - t.total_eligible * 0.5) / (t.total_eligible * 0.5)) AS chi_square_statistic
    FROM Observed o CROSS JOIN Totals t
)
SELECT
    'INFORMATIONAL — exposure balance, NOT the SRM gate' AS label,
    (SELECT COUNT(*) FROM expt.experiment_population WHERE is_eligible = 1 AND variant = 'control') AS eligible_control,
    (SELECT COUNT(*) FROM expt.experiment_population WHERE is_eligible = 1 AND variant = 'treatment') AS eligible_treatment,
    ROUND(chi_square_statistic, 4) AS exposure_chi_square,
    CASE WHEN chi_square_statistic >= 3.841 THEN 'IMBALANCED — investigate exposure mechanism' ELSE 'BALANCED' END AS exposure_assessment
FROM ChiSqStat;

/*
    BUSINESS INTERPRETATION — fill in after running:
    - What is the PRIMARY (assigned-population) chi-square
      statistic — expected to be extremely small, near-confirming
      the deterministic 50/50 split already seen in Script 01?
    - Does the informational exposure-balance check also come back
      balanced (it should, per the earlier 2,223 vs 2,188 result)?

    BUSINESS IMPLICATION — fill in after running:
    - Whether Script 04 onward can proceed — gated on the PRIMARY
      SRM result only, not the informational exposure check
*/
