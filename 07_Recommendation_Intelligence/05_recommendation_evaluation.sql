/*
    ============================================================
    ORGEE — Phase 7: Recommendation Intelligence
    05_recommendation_evaluation.sql ⭐ CRITICAL SCRIPT
    ============================================================

    BUSINESS QUESTION
    Are the generated recommendations actually relevant, or would
    we be fooling ourselves by claiming quality without evidence?

    LEAKAGE-SAFE DESIGN (the most important technical check in
    Phase 7, per the plan):
        CUTOFF DATE = 2018-05-01 (documented, fixed choice — leaves
        ~4 months of holdout out of the ~24-month dataset span,
        Sept 2016 - Aug 2018).

        TRAINING  = all interactions/purchases strictly BEFORE the
                    cutoff. Preference profiles and recommendations
                    for this evaluation are rebuilt from ONLY this
                    data — completely separate tables from the
                    "production" reco.* tables built in 01-04.
        HOLDOUT   = actual purchases ON OR AFTER the cutoff — the
                    "future" ground truth.

    TWO FIXES APPLIED AFTER REVIEW (both real, both confirmed
    against the prior version of this script):

    FIX 1 — BASELINE POPULATION MISMATCH. The baseline was
    previously evaluated on ALL 25,015 customers with a holdout
    purchase, while the engine was evaluated on only the 14,490
    who ALSO had training-period activity (and therefore a
    profile). That's not apples-to-apples — many of the extra
    ~10,525 customers have zero training interactions at all and
    could never have received an engine recommendation in the
    first place. Fixed: a single #EligibleForEvaluation temp table
    is now computed ONCE and used for BOTH the engine metrics and
    the baseline metrics, guaranteeing the same population.

    FIX 2 — PRICE FEATURE LEAKAGE. reco.product_features (built in
    Script 02) computes price_norm from Fact_Order_Items with NO
    date restriction — meaning it reflects each product's average
    price across the ENTIRE observation period, including
    transactions AFTER the cutoff. Category, weight, volume, and
    photo count are static catalog attributes with no time
    dimension, so those are genuinely leakage-free — but price_norm
    is derived from transactional data and carries real future
    information into what should be a training-only computation.
    Fixed: a training-period-only price_norm is computed fresh
    (Fact_Order_Items joined to Dim_Date, filtered to
    full_date < cutoff), combined with the static features into
    #EvalProductFeatures, which REPLACES every reference to
    reco.product_features in this script — including inside
    reco.eval_preferences itself, not just the final similarity
    step, since the customer's own preference vector was equally
    exposed to this leakage.

    METRICS: Precision@5, Recall@5, Hit Rate@5 — plus a naive
    popularity-based baseline, evaluated on the identical population.

    TECHNIQUES USED
    CTE, date filtering, aggregation, window functions.
    ============================================================
*/

DECLARE @CutoffDate DATE = '2018-05-01';

-- ------------------------------------------------------------
-- TRAINING interactions (strictly before cutoff)
-- ------------------------------------------------------------

IF OBJECT_ID('reco.eval_interactions', 'U') IS NOT NULL DROP TABLE reco.eval_interactions;

SELECT customer_unique_id, product_sk, interaction_type, interaction_weight, interaction_date
INTO reco.eval_interactions
FROM reco.interactions
WHERE interaction_date < @CutoffDate;

-- ------------------------------------------------------------
-- FIX 2: training-period-only product feature set. Category,
-- weight, volume, photos are static (no leakage risk) and are
-- carried over unchanged from reco.product_features. price_norm
-- is recomputed from ONLY pre-cutoff delivered transactions.
-- ------------------------------------------------------------

IF OBJECT_ID('tempdb..#EvalPriceNorm') IS NOT NULL DROP TABLE #EvalPriceNorm;

;WITH TrainingAvgPrice AS (
    SELECT foi.product_sk, AVG(foi.price) AS avg_price
    FROM dbo.Fact_Order_Items foi
    JOIN dbo.Dim_Date d ON foi.order_purchase_date_sk = d.date_sk
    WHERE foi.order_status = 'delivered' AND d.full_date < @CutoffDate
    GROUP BY foi.product_sk
)
SELECT
    product_sk,
    'price_norm' AS feature_name,
    CASE
        WHEN (SELECT MAX(avg_price) FROM TrainingAvgPrice) = (SELECT MIN(avg_price) FROM TrainingAvgPrice) THEN 0.5
        ELSE (avg_price - (SELECT MIN(avg_price) FROM TrainingAvgPrice))
             / ((SELECT MAX(avg_price) FROM TrainingAvgPrice) - (SELECT MIN(avg_price) FROM TrainingAvgPrice))
    END AS feature_value
INTO #EvalPriceNorm
FROM TrainingAvgPrice;

IF OBJECT_ID('tempdb..#EvalProductFeatures') IS NOT NULL DROP TABLE #EvalProductFeatures;

SELECT product_sk, feature_name, feature_value
INTO #EvalProductFeatures
FROM reco.product_features
WHERE feature_name <> 'price_norm'

UNION ALL

SELECT product_sk, feature_name, feature_value
FROM #EvalPriceNorm;

DROP TABLE #EvalPriceNorm;

-- ------------------------------------------------------------
-- TRAINING-only preference profiles — now built from
-- #EvalProductFeatures (leakage-free), not reco.product_features
-- ------------------------------------------------------------

IF OBJECT_ID('reco.eval_preferences', 'U') IS NOT NULL DROP TABLE reco.eval_preferences;

;WITH CustomerProductInterest AS (
    SELECT customer_unique_id, product_sk, SUM(interaction_weight) AS total_interest_weight
    FROM reco.eval_interactions
    GROUP BY customer_unique_id, product_sk
)
SELECT
    cpi.customer_unique_id,
    pf.feature_name,
    SUM(cpi.total_interest_weight * pf.feature_value) AS preference_value
INTO reco.eval_preferences
FROM CustomerProductInterest cpi
JOIN #EvalProductFeatures pf ON cpi.product_sk = pf.product_sk
GROUP BY cpi.customer_unique_id, pf.feature_name;

-- ------------------------------------------------------------
-- TRAINING-only recommendations — same candidate-shortlist
-- design as Script 04 (top-100-per-category), now consistently
-- using #EvalProductFeatures throughout
-- ------------------------------------------------------------

IF OBJECT_ID('reco.eval_recommendations', 'U') IS NOT NULL DROP TABLE reco.eval_recommendations;

IF OBJECT_ID('tempdb..#EvalCustMag') IS NOT NULL DROP TABLE #EvalCustMag;
SELECT customer_unique_id, SQRT(SUM(preference_value * preference_value)) AS customer_magnitude
INTO #EvalCustMag
FROM reco.eval_preferences
GROUP BY customer_unique_id;

IF OBJECT_ID('tempdb..#EvalProdMag') IS NOT NULL DROP TABLE #EvalProdMag;
SELECT product_sk, SQRT(SUM(feature_value * feature_value)) AS product_magnitude
INTO #EvalProdMag
FROM #EvalProductFeatures
GROUP BY product_sk;

IF OBJECT_ID('tempdb..#EvalTopCategory') IS NOT NULL DROP TABLE #EvalTopCategory;
;WITH RankedCategories AS (
    SELECT customer_unique_id, feature_name AS top_category,
        ROW_NUMBER() OVER (PARTITION BY customer_unique_id ORDER BY preference_value DESC, feature_name ASC) AS rn
    FROM reco.eval_preferences
    WHERE feature_name LIKE 'cat_%'
)
SELECT customer_unique_id, top_category
INTO #EvalTopCategory
FROM RankedCategories
WHERE rn = 1;
-- Top-1 category, cap-100 shortlist: the configuration confirmed
-- to outperform a widened top-3/cap-250 test (see README).

IF OBJECT_ID('tempdb..#EvalCategoryPop') IS NOT NULL DROP TABLE #EvalCategoryPop;
SELECT
    pf.feature_name AS category, pf.product_sk,
    COUNT(i.product_sk) AS interaction_count
INTO #EvalCategoryPop
FROM #EvalProductFeatures pf
LEFT JOIN reco.eval_interactions i ON i.product_sk = pf.product_sk
WHERE pf.feature_name LIKE 'cat_%'
GROUP BY pf.feature_name, pf.product_sk;

IF OBJECT_ID('tempdb..#EvalCategoryShortlist') IS NOT NULL DROP TABLE #EvalCategoryShortlist;
;WITH RankedByPop AS (
    SELECT category, product_sk,
        ROW_NUMBER() OVER (PARTITION BY category ORDER BY interaction_count DESC, product_sk ASC) AS rn
    FROM #EvalCategoryPop
)
SELECT category, product_sk
INTO #EvalCategoryShortlist
FROM RankedByPop
WHERE rn <= 100;
DROP TABLE #EvalCategoryPop;

IF OBJECT_ID('tempdb..#EvalCandidates') IS NOT NULL DROP TABLE #EvalCandidates;
SELECT etc.customer_unique_id, ecs.product_sk
INTO #EvalCandidates
FROM #EvalTopCategory etc
JOIN #EvalCategoryShortlist ecs ON ecs.category = etc.top_category;
DROP TABLE #EvalCategoryShortlist;

;WITH DotProduct AS (
    SELECT
        c.customer_unique_id, c.product_sk,
        SUM(ep.preference_value * pf.feature_value) AS dot_product
    FROM #EvalCandidates c
    JOIN reco.eval_preferences ep ON ep.customer_unique_id = c.customer_unique_id
    JOIN #EvalProductFeatures pf ON pf.product_sk = c.product_sk AND pf.feature_name = ep.feature_name
    GROUP BY c.customer_unique_id, c.product_sk
),
Similarity AS (
    SELECT
        dp.customer_unique_id, dp.product_sk,
        dp.dot_product / NULLIF(cm.customer_magnitude * pm.product_magnitude, 0) AS similarity_score
    FROM DotProduct dp
    JOIN #EvalCustMag cm ON cm.customer_unique_id = dp.customer_unique_id
    JOIN #EvalProdMag pm ON pm.product_sk = dp.product_sk
),
NotAlreadyPurchasedInTraining AS (
    SELECT s.* FROM Similarity s
    WHERE NOT EXISTS (
        SELECT 1 FROM reco.eval_interactions ei
        WHERE ei.customer_unique_id = s.customer_unique_id
          AND ei.product_sk = s.product_sk
          AND ei.interaction_type = 'purchase'
    )
),
Ranked AS (
    SELECT customer_unique_id, product_sk, similarity_score,
        ROW_NUMBER() OVER (PARTITION BY customer_unique_id ORDER BY similarity_score DESC, product_sk ASC) AS rnk
    FROM NotAlreadyPurchasedInTraining
)
SELECT customer_unique_id, product_sk, rnk AS recommendation_rank, similarity_score
INTO reco.eval_recommendations
FROM Ranked
WHERE rnk <= 5;

DROP TABLE #EvalCustMag;
DROP TABLE #EvalProdMag;
DROP TABLE #EvalTopCategory;
DROP TABLE #EvalCandidates;
DROP TABLE #EvalProductFeatures;

-- ------------------------------------------------------------
-- HOLDOUT ground truth: actual purchases on/after the cutoff
-- ------------------------------------------------------------

IF OBJECT_ID('tempdb..#HoldoutPurchases') IS NOT NULL DROP TABLE #HoldoutPurchases;
SELECT DISTINCT customer_unique_id, product_sk
INTO #HoldoutPurchases
FROM reco.interactions
WHERE interaction_type = 'purchase' AND interaction_date >= @CutoffDate;

-- ------------------------------------------------------------
-- FIX 1: the SAME eligible population, computed ONCE, used for
-- BOTH the engine metrics and the baseline metrics below —
-- customers with training-period recommendations AND a holdout
-- purchase. This is the one population both comparisons must
-- share for the result to be apples-to-apples.
-- ------------------------------------------------------------

IF OBJECT_ID('tempdb..#EligibleForEvaluation') IS NOT NULL DROP TABLE #EligibleForEvaluation;
SELECT DISTINCT r.customer_unique_id
INTO #EligibleForEvaluation
FROM reco.eval_recommendations r
JOIN #HoldoutPurchases h ON h.customer_unique_id = r.customer_unique_id;

-- ------------------------------------------------------------
-- Evaluable population size — the honest constraint
-- ------------------------------------------------------------

SELECT
    (SELECT COUNT(DISTINCT customer_unique_id) FROM reco.eval_recommendations) AS customers_with_training_recs,
    (SELECT COUNT(DISTINCT customer_unique_id) FROM #HoldoutPurchases) AS customers_with_holdout_purchase,
    (SELECT COUNT(*) FROM #EligibleForEvaluation) AS eligible_for_evaluation;

-- ------------------------------------------------------------
-- *** Precision@5 / Recall@5 / Hit Rate@5 — content-based engine ***
-- ------------------------------------------------------------

;WITH PerCustomerMetrics AS (
    SELECT
        ec.customer_unique_id,
        (SELECT COUNT(*) FROM reco.eval_recommendations r
         WHERE r.customer_unique_id = ec.customer_unique_id
           AND EXISTS (SELECT 1 FROM #HoldoutPurchases h WHERE h.customer_unique_id = r.customer_unique_id AND h.product_sk = r.product_sk)
        ) AS hits,
        (SELECT COUNT(*) FROM reco.eval_recommendations r WHERE r.customer_unique_id = ec.customer_unique_id) AS recs_given,
        (SELECT COUNT(*) FROM #HoldoutPurchases h WHERE h.customer_unique_id = ec.customer_unique_id) AS holdout_purchase_count
    FROM #EligibleForEvaluation ec
)
SELECT
    COUNT(*) AS evaluated_customers,
    ROUND(AVG(1.0 * hits / NULLIF(recs_given, 0)), 4) AS avg_precision_at_5,
    ROUND(AVG(1.0 * hits / NULLIF(holdout_purchase_count, 0)), 4) AS avg_recall_at_5,
    ROUND(1.0 * SUM(CASE WHEN hits > 0 THEN 1 ELSE 0 END) / COUNT(*), 4) AS hit_rate_at_5
FROM PerCustomerMetrics;

-- ------------------------------------------------------------
-- BASELINE COMPARISON: naive "recommend the 5 most popular
-- products overall" — evaluated on the IDENTICAL population as
-- the engine above (#EligibleForEvaluation, not all holdout
-- purchasers) — this is the apples-to-apples fix.
-- ------------------------------------------------------------

IF OBJECT_ID('tempdb..#PopularTop5') IS NOT NULL DROP TABLE #PopularTop5;
SELECT TOP 5 product_sk, COUNT(*) AS purchase_count
INTO #PopularTop5
FROM reco.eval_interactions
WHERE interaction_type = 'purchase'
GROUP BY product_sk
ORDER BY purchase_count DESC;

;WITH BaselineHits AS (
    SELECT
        ec.customer_unique_id,
        (SELECT COUNT(*) FROM #PopularTop5 p
         WHERE EXISTS (SELECT 1 FROM #HoldoutPurchases h WHERE h.customer_unique_id = ec.customer_unique_id AND h.product_sk = p.product_sk)
        ) AS hits
    FROM #EligibleForEvaluation ec
)
SELECT
    COUNT(*) AS evaluated_customers,
    ROUND(1.0 * SUM(CASE WHEN hits > 0 THEN 1 ELSE 0 END) / COUNT(*), 4) AS baseline_hit_rate_at_5
FROM BaselineHits;

DROP TABLE #PopularTop5;
DROP TABLE #HoldoutPurchases;
DROP TABLE #EligibleForEvaluation;

/*
    BUSINESS INTERPRETATION — fill in with the numbers from THIS
    corrected run (both prior runs used a mismatched baseline
    population and price-leaked features — superseded):
    - The actual Precision@5 / Recall@5 / Hit Rate@5 numbers
    - The baseline Hit Rate@5, now on the SAME population as the
      engine — do not assume it stays at 1.00%; report whatever
      this run actually produces
    - Does the content-based engine beat the corrected baseline?

    BUSINESS IMPLICATION — fill in after running:
    - Whether the engine shows genuine signal worth deploying, or
      whether it performs no better than recommending best-sellers,
      now on a fully fair, leakage-free comparison
*/
