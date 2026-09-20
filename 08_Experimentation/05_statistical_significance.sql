/*
    ============================================================
    ORGEE — Phase 8: Experimentation Framework
    05_statistical_significance.sql ⭐ CRITICAL SCRIPT
    ============================================================

    BUSINESS QUESTION
    Is the observed difference in Purchase Conversion Rate between
    Control and Treatment unlikely to be explained by random
    variation under the null hypothesis — or is it well within
    normal noise?

    METHOD: Two-proportion z-test.
        p1 = Control conversion rate, n1 = Control eligible count
        p2 = Treatment conversion rate, n2 = Treatment eligible count
        Absolute Effect  = p2 - p1  (Treatment - Control)
        Relative Lift    = (p2 - p1) / p1
        Pooled SE (for the hypothesis test, assumes equal
                   proportions under H0) = sqrt(p_pooled*(1-p_pooled)*(1/n1+1/n2))
        z = (p2 - p1) / Pooled SE
        Unpooled SE (for the confidence interval — does NOT
                     assume the proportions are equal) =
                     sqrt(p1*(1-p1)/n1 + p2*(1-p2)/n2)
        95% CI = Absolute Effect +/- 1.96 * Unpooled SE

    SIGNIFICANCE THRESHOLD: alpha = 0.05, stated explicitly (matches
    the primary SRM threshold from Script 03 for consistency).

    P-VALUE CALCULATION: SQL Server has no built-in normal-
    distribution CDF function. Rather than approximate loosely or
    fabricate a number, this script implements a standard polynomial
    approximation for the standard normal upper-tail probability —
    a well-established numerical method used to calculate the
    two-tailed p-value.

    TECHNIQUES USED
    CTE, numerical approximation, z-test arithmetic.
    ============================================================
*/

;WITH Metrics AS (
    SELECT
        SUM(CASE WHEN ep.variant = 'control' THEN 1 ELSE 0 END) AS n1,
        SUM(CASE WHEN ep.variant = 'treatment' THEN 1 ELSE 0 END) AS n2,
        SUM(CASE WHEN ep.variant = 'control' AND cc.customer_sk IS NOT NULL THEN 1 ELSE 0 END) AS x1,
        SUM(CASE WHEN ep.variant = 'treatment' AND cc.customer_sk IS NOT NULL THEN 1 ELSE 0 END) AS x2
    FROM expt.experiment_population ep
    LEFT JOIN (
        SELECT DISTINCT customer_sk
        FROM dbo.Fact_Recommendation_Events
        WHERE experiment_sk = (SELECT experiment_sk FROM dbo.Dim_Experiment WHERE experiment_id = 'exp_001')
          AND event_type = 'recommendation_conversion'
    ) cc ON cc.customer_sk = ep.customer_sk
    WHERE ep.is_eligible = 1
),
Rates AS (
    SELECT
        n1, n2, x1, x2,
        CAST(x1 AS FLOAT) / n1 AS p1,
        CAST(x2 AS FLOAT) / n2 AS p2,
        CAST(x1 + x2 AS FLOAT) / (n1 + n2) AS p_pooled
    FROM Metrics
),
Effects AS (
    SELECT
        *,
        (p2 - p1) AS absolute_effect,
        (p2 - p1) / p1 AS relative_lift,
        SQRT(p_pooled * (1 - p_pooled) * (1.0 / n1 + 1.0 / n2)) AS se_pooled,
        SQRT(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2) AS se_unpooled
    FROM Rates
),
ZStat AS (
    SELECT *,
        (p2 - p1) / se_pooled AS z_statistic
    FROM Effects
),
PValueCalc AS (
    SELECT *,
        ABS(z_statistic) AS abs_z,
        1.0 / (1.0 + 0.2316419 * ABS(z_statistic)) AS t_term,
        EXP(-ABS(z_statistic) * ABS(z_statistic) / 2.0) / SQRT(2.0 * PI()) AS phi_abs_z
    FROM ZStat
),
FinalCalc AS (
    SELECT *,
        phi_abs_z * (
            0.319381530 * t_term
            - 0.356563782 * POWER(t_term, 2)
            + 1.781477937 * POWER(t_term, 3)
            - 1.821255978 * POWER(t_term, 4)
            + 1.330274429 * POWER(t_term, 5)
        ) AS upper_tail_prob
    FROM PValueCalc
)
SELECT
    n1 AS control_n,
    n2 AS treatment_n,
    ROUND(p1 * 100, 4) AS control_conversion_pct,
    ROUND(p2 * 100, 4) AS treatment_conversion_pct,
    ROUND(absolute_effect * 100, 4) AS absolute_effect_pp,
    ROUND(relative_lift * 100, 2) AS relative_lift_pct,
    ROUND(z_statistic, 4) AS z_statistic,
    ROUND(2 * upper_tail_prob, 4) AS p_value_two_tailed,
    CASE WHEN 2 * upper_tail_prob < 0.05 THEN 'SIGNIFICANT (p<0.05)' ELSE 'NOT SIGNIFICANT (p>=0.05)' END AS significance_at_alpha_05,
    ROUND(absolute_effect * 100 - 1.96 * se_unpooled * 100, 4) AS ci_95_lower_pp,
    ROUND(absolute_effect * 100 + 1.96 * se_unpooled * 100, 4) AS ci_95_upper_pp
FROM FinalCalc;

/*
    BUSINESS INTERPRETATION — fill in after running:
    - What is the actual p-value, and does it cross the 0.05
      threshold?
    - Does the 95% confidence interval span zero (uncertain effect),
      sit entirely above zero (positive effect), or entirely below
      zero (negative effect)?
    - Recall the design expectation from Script 01: no true
      treatment effect was built into this data, so "NOT
      SIGNIFICANT" with a CI spanning zero would be the honest,
      expected result — not a failure of the analysis.

    STATISTICAL INTERPRETATION:
    Statistical significance tells us whether the observed
    difference is unlikely under the null hypothesis of no true
    difference. It does NOT by itself tell us whether the
    difference (if significant) would be commercially meaningful —
    that judgment belongs in Script 07's business decision, not here.

    BUSINESS IMPLICATION — fill in after running:
    - Feeds directly into Script 06's consolidated readout and
      Script 07's final SHIP / DO NOT SHIP / CONTINUE TESTING call
*/
