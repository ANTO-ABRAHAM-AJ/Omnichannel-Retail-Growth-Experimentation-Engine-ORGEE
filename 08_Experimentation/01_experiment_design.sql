/*
    ============================================================
    ORGEE — Phase 8: Experimentation Framework
    01_experiment_design.sql
    ============================================================

    BUSINESS QUESTION
    Does personalized product recommendation improve purchase
    conversion compared with a control experience using
    top-selling products?

    HYPOTHESIS
    H0: There is no difference in purchase conversion rate
        between Control and Treatment.
    H1: Purchase conversion rate differs between Control and
        Treatment.

    LOCKED SCOPE DECISIONS (made before writing this script, after
    checking the actual Python generator source, not just the
    warehouse DDL):

    1. This analysis is scoped to experiment 'exp_001' ONLY.
       Dim_Experiment contains 3 experiments (exp_001/002/003),
       but the original generator only ever produced
       Fact_Recommendation_Events for the alphabetically-first
       experiment_id. exp_002 and exp_003 have customer
       ASSIGNMENTS but zero recommendation events — CTR/AOV/
       conversion analysis is only possible for exp_001. This is
       also, conveniently, exactly the right experiment: its
       variant labels are literally "Top Sellers Recommendations"
       (control) vs "Personalized Content-Based Recommendations"
       (treatment) — an exact match to this phase's hypothesis.

    2. Purchase Conversion Rate is defined as: customers with >=1
       'recommendation_conversion' event event_type in
       Fact_Recommendation_Events, divided by eligible assigned
       customers — using ONLY Fact_Recommendation_Events, not
       cross-referenced against real Fact_Order_Items purchases.
       The recommendation-conversion signal was generated as a
       self-contained probabilistic outcome (12% impression->click,
       8% click->purchase), independent of any real order data —
       stating this explicitly avoids any future ambiguity about
       what "conversion" means in this phase.

    3. EXPECTATION SET BEFORE ANALYSIS (checked directly against
       the generator source): impression->click and click->purchase
       probabilities are GLOBAL CONSTANTS applied identically to
       both control and treatment — there is no synthetic treatment
       effect built into this data by design. A defensible, likely
       outcome of this experiment is therefore "no significant
       difference" (DO NOT SHIP / CONTINUE TESTING), not "SHIP".
       This is stated here, before any metric is computed, so the
       final decision cannot be accused of being reverse-engineered
       to match a result we already knew was coming.

    4. Assignment allocation is a DETERMINISTIC near-exact 50/50 split
       (customer IDs sorted and split into two exact halves), not
       a probabilistic coin-flip per customer — so the SRM check
       in Script 03 is expected to pass cleanly, and that
       expectation is stated here rather than treated as a
       surprising result later.

    TECHNIQUES USED
    Simple SELECT against Dim_Experiment / Fact_Experiment_Assignments.
    ============================================================
*/

-- ------------------------------------------------------------
-- Experiment definition (confirms the exp_001 scope decision
-- against the live warehouse, not just the generator source)
-- ------------------------------------------------------------

SELECT
    experiment_id,
    experiment_name,
    objective,
    start_timestamp,
    end_timestamp,
    primary_metric,
    control_variant_label,
    treatment_variant_label
FROM dbo.Dim_Experiment
WHERE experiment_id = 'exp_001';

-- ------------------------------------------------------------
-- Confirm scope decision #1: only exp_001 has recommendation
-- event data (this should show 0 for exp_002 and exp_003)
--
-- FIX: the original version joined Fact_Experiment_Assignments
-- and Fact_Recommendation_Events directly on the shared
-- experiment_sk key, which only has 3 distinct values —
-- creating a cross-join-like row explosion for each experiment
-- (assignments x events, potentially ~1 billion intermediate
-- rows) and exhausting buffer pool memory. Fixed by aggregating
-- each fact table SEPARATELY first, then joining the two
-- already-collapsed one-row-per-experiment summaries — no
-- row-level fan-out.
-- ------------------------------------------------------------

;WITH AssignmentCounts AS (
    SELECT experiment_sk, COUNT(DISTINCT customer_sk) AS assigned_customers
    FROM dbo.Fact_Experiment_Assignments
    GROUP BY experiment_sk
),
RecommendationCounts AS (
    SELECT experiment_sk, COUNT(*) AS recommendation_events
    FROM dbo.Fact_Recommendation_Events
    GROUP BY experiment_sk
)
SELECT
    de.experiment_id,
    de.experiment_name,
    ISNULL(ac.assigned_customers, 0) AS assigned_customers,
    ISNULL(rc.recommendation_events, 0) AS recommendation_events
FROM dbo.Dim_Experiment de
LEFT JOIN AssignmentCounts ac ON ac.experiment_sk = de.experiment_sk
LEFT JOIN RecommendationCounts rc ON rc.experiment_sk = de.experiment_sk
ORDER BY de.experiment_id;

-- ------------------------------------------------------------
-- High-level population for exp_001: assigned participants,
-- Control/Treatment split, allocation %
-- ------------------------------------------------------------

SELECT
    fea.variant,
    COUNT(*) AS assigned_participants,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS allocation_pct
FROM dbo.Fact_Experiment_Assignments fea
JOIN dbo.Dim_Experiment de ON de.experiment_sk = fea.experiment_sk
WHERE de.experiment_id = 'exp_001'
GROUP BY fea.variant
ORDER BY fea.variant;

/*
    BUSINESS INTERPRETATION — fill in after running:
    - Does the experiment definition confirm exp_001 as the
      correct "Top Sellers" vs "Personalized" experiment?
    - Does the recommendation-event confirmation show 0 events
      for exp_002/exp_003, confirming the scope decision?
    - Is the assigned allocation close to 50/50, as expected?

    BUSINESS IMPLICATION — fill in after running:
    - Confirms whether Script 02 onward can proceed with exp_001
      as the sole analysis target
*/
