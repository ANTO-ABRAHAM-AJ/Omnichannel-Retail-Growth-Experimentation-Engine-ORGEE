/*
    ============================================================
    ORGEE — Phase 7: Recommendation Intelligence
    04_content_based_recommendation_engine.sql ⭐ SIGNATURE SCRIPT
    ============================================================

    BUSINESS QUESTION
    Which products are most relevant to this customer?

    CANDIDATE GENERATION DESIGN (stated explicitly, not hidden):
    Comparing every customer against all 32,951 products directly
    would mean ~95,137 x 32,951 ≈ 3.1 BILLION pairs — computationally
    infeasible in plain T-SQL. Instead, per the plan's own
    architecture ("Candidate Products -> Filtering -> Top-N"):
        1. Each customer's SINGLE highest-preference category
           becomes their candidate pool.
        2. Within that pool, full cosine similarity is computed
           across ALL 5 features (category + price + weight +
           volume + photos) — not just category — so the ranking
           still reflects the whole preference profile, not only
           the category match.

    FIX APPLIED (a first version joining every customer directly to
    every product in their top category exhausted tempdb at
    159,461,416 candidate rows — a handful of large/popular
    categories shared by tens of thousands of customers multiplied
    out catastrophically): each category's candidate pool is now
    capped to its top 100 most-popular products (by total
    interaction count), computed once independent of any customer,
    before joining customers to that shortlist. Still a legitimate,
    standard candidate-generation technique — popular items within
    a customer's preferred category are sensible candidates — not a
    shortcut that skips real recommendation logic.

    SIMILARITY: cosine similarity = dot product / (magnitude_a * magnitude_b)
        dot product   = SUM of (customer_value * product_value) over
                        shared feature_name (a missing feature on
                        either side contributes 0 naturally, via JOIN)
        magnitude     = SQRT(SUM(value^2)) over a vector's OWN full
                        feature set (computed once, independent of
                        which product/customer it's being compared to)

    FILTERING:
        - Already-purchased products EXCLUDED (these are discovery
          recommendations — re-suggesting what they already bought
          isn't useful).
        - Products with zero features (Script 02's coverage check)
          cannot be scored and are naturally excluded (no feature
          rows to join against).

    TOP-N: 5 (documented choice — "Top 5", per the plan's own example).

    PERFORMANCE NOTE: this is a genuinely heavy query even after
    the category-based candidate reduction (95,137 customers x
    ~hundreds of candidates each). Consider testing on a small
    customer sample first (see the commented TOP filter below)
    before running the full population.

    TECHNIQUES USED
    CTE, window functions (RANK), aggregation, SQRT.
    ============================================================
*/

IF OBJECT_ID('reco.recommendations', 'U') IS NOT NULL DROP TABLE reco.recommendations;

CREATE TABLE reco.recommendations (
    rec_sk                  BIGINT IDENTITY(1,1) NOT NULL,
    customer_unique_id      VARCHAR(32)          NOT NULL,
    recommended_product_id  VARCHAR(32)          NOT NULL,
    recommendation_rank     INT                  NOT NULL,
    similarity_score        DECIMAL(10,6)        NOT NULL,
    top_category            VARCHAR(80)          NULL,  -- the "reason" — the customer's top category driving candidate selection

    CONSTRAINT PK_reco_recommendations PRIMARY KEY CLUSTERED (rec_sk)
);
GO

-- ------------------------------------------------------------
-- Step 1: precompute customer preference vector magnitudes
-- ------------------------------------------------------------

IF OBJECT_ID('tempdb..#CustomerMagnitude') IS NOT NULL DROP TABLE #CustomerMagnitude;

SELECT
    customer_unique_id,
    SQRT(SUM(preference_value * preference_value)) AS customer_magnitude
INTO #CustomerMagnitude
FROM reco.customer_preferences
GROUP BY customer_unique_id;

-- ------------------------------------------------------------
-- Step 2: precompute product feature vector magnitudes
-- ------------------------------------------------------------

IF OBJECT_ID('tempdb..#ProductMagnitude') IS NOT NULL DROP TABLE #ProductMagnitude;

SELECT
    product_sk,
    SQRT(SUM(feature_value * feature_value)) AS product_magnitude
INTO #ProductMagnitude
FROM reco.product_features
GROUP BY product_sk;

-- ------------------------------------------------------------
-- Step 3: each customer's single top-preference category
-- ------------------------------------------------------------

IF OBJECT_ID('tempdb..#CustomerTopCategory') IS NOT NULL DROP TABLE #CustomerTopCategory;

;WITH RankedCategories AS (
    SELECT
        customer_unique_id,
        feature_name AS top_category,
        preference_value,
        ROW_NUMBER() OVER (PARTITION BY customer_unique_id ORDER BY preference_value DESC, feature_name ASC) AS rn
    FROM reco.customer_preferences
    WHERE feature_name LIKE 'cat_%'
)
SELECT customer_unique_id, top_category
INTO #CustomerTopCategory
FROM RankedCategories
WHERE rn = 1;

-- ------------------------------------------------------------
-- Step 4: candidate pool — products in the customer's top category
--
-- FIX APPLIED (after the first version exhausted tempdb at
-- 159,461,416 candidate rows): joining every customer directly to
-- EVERY product in their top category multiplies out catastrophically
-- when a handful of large/popular categories are shared by tens of
-- thousands of customers. Fixed with a two-stage approach:
--   1. Build a per-category SHORTLIST of the top 100 most-popular
--      products (by total interaction count) — computed ONCE,
--      independent of any customer. At most 71 categories x 100 =
--      7,100 rows.
--   2. Join customers to their top category's SHORTLIST, not the
--      full category — bounding worst-case candidate rows to
--      (customers) x 100, not (customers) x (full category size).
-- ------------------------------------------------------------

IF OBJECT_ID('tempdb..#CategoryPopularity') IS NOT NULL DROP TABLE #CategoryPopularity;

SELECT
    pf.feature_name AS category,
    pf.product_sk,
    COUNT(i.interaction_sk) AS interaction_count
INTO #CategoryPopularity
FROM reco.product_features pf
LEFT JOIN reco.interactions i ON i.product_sk = pf.product_sk
WHERE pf.feature_name LIKE 'cat_%'
GROUP BY pf.feature_name, pf.product_sk;

IF OBJECT_ID('tempdb..#CategoryShortlist') IS NOT NULL DROP TABLE #CategoryShortlist;

;WITH RankedByPopularity AS (
    SELECT
        category, product_sk, interaction_count,
        ROW_NUMBER() OVER (PARTITION BY category ORDER BY interaction_count DESC, product_sk ASC) AS rn
    FROM #CategoryPopularity
)
SELECT category, product_sk
INTO #CategoryShortlist
FROM RankedByPopularity
WHERE rn <= 100;

DROP TABLE #CategoryPopularity;

IF OBJECT_ID('tempdb..#Candidates') IS NOT NULL DROP TABLE #Candidates;

SELECT
    ctc.customer_unique_id,
    ctc.top_category,
    cs.product_sk
INTO #Candidates
FROM #CustomerTopCategory ctc
JOIN #CategoryShortlist cs ON cs.category = ctc.top_category;
-- Uncomment to test on a small sample first:
-- WHERE ctc.customer_unique_id IN (SELECT TOP 100 customer_unique_id FROM #CustomerTopCategory ORDER BY customer_unique_id)

DROP TABLE #CategoryShortlist;

-- ------------------------------------------------------------
-- Step 5-8: dot product, cosine similarity, exclude already-
-- purchased, rank, Top-5
-- ------------------------------------------------------------

;WITH DotProduct AS (
    SELECT
        c.customer_unique_id,
        c.top_category,
        c.product_sk,
        SUM(cp.preference_value * pf.feature_value) AS dot_product
    FROM #Candidates c
    JOIN reco.customer_preferences cp ON cp.customer_unique_id = c.customer_unique_id
    JOIN reco.product_features pf ON pf.product_sk = c.product_sk AND pf.feature_name = cp.feature_name
    GROUP BY c.customer_unique_id, c.top_category, c.product_sk
),
Similarity AS (
    SELECT
        dp.customer_unique_id,
        dp.top_category,
        dp.product_sk,
        dp.dot_product / NULLIF(cm.customer_magnitude * pm.product_magnitude, 0) AS similarity_score
    FROM DotProduct dp
    JOIN #CustomerMagnitude cm ON cm.customer_unique_id = dp.customer_unique_id
    JOIN #ProductMagnitude pm ON pm.product_sk = dp.product_sk
),
NotAlreadyPurchased AS (
    SELECT s.*
    FROM Similarity s
    WHERE NOT EXISTS (
        SELECT 1 FROM reco.interactions i
        WHERE i.customer_unique_id = s.customer_unique_id
          AND i.product_sk = s.product_sk
          AND i.interaction_type = 'purchase'
    )
),
Ranked AS (
    SELECT
        customer_unique_id,
        top_category,
        product_sk,
        similarity_score,
        ROW_NUMBER() OVER (PARTITION BY customer_unique_id ORDER BY similarity_score DESC, product_sk ASC) AS rnk
    FROM NotAlreadyPurchased
)
INSERT INTO reco.recommendations (customer_unique_id, recommended_product_id, recommendation_rank, similarity_score, top_category)
SELECT
    r.customer_unique_id,
    dp.product_id,
    r.rnk,
    r.similarity_score,
    r.top_category
FROM Ranked r
JOIN dbo.Dim_Product dp ON r.product_sk = dp.product_sk
WHERE r.rnk <= 5;

DROP TABLE #CustomerMagnitude;
DROP TABLE #ProductMagnitude;
DROP TABLE #CustomerTopCategory;
DROP TABLE #Candidates;

-- ------------------------------------------------------------
-- Coverage: how many eligible customers actually got recommendations?
-- ------------------------------------------------------------

SELECT
    COUNT(DISTINCT customer_unique_id) AS customers_with_recommendations,
    (SELECT COUNT(DISTINCT customer_unique_id) FROM reco.customer_preferences) AS customers_with_a_profile,
    ROUND(
        100.0 * COUNT(DISTINCT customer_unique_id)
        / (SELECT COUNT(DISTINCT customer_unique_id) FROM reco.customer_preferences), 2
    ) AS coverage_pct
FROM reco.recommendations;

-- ------------------------------------------------------------
-- Example: Top-5 recommendations for 2 sample customers
-- ------------------------------------------------------------

SELECT TOP 10
    customer_unique_id, recommended_product_id, recommendation_rank, similarity_score, top_category
FROM reco.recommendations
WHERE customer_unique_id IN (
    SELECT TOP 2 customer_unique_id FROM reco.recommendations ORDER BY customer_unique_id
)
ORDER BY customer_unique_id, recommendation_rank;

-- ------------------------------------------------------------
-- Similarity score distribution — sanity check (should be
-- roughly between -1 and 1, and mostly positive since all our
-- features are non-negative)
-- ------------------------------------------------------------

SELECT
    MIN(similarity_score) AS min_similarity,
    MAX(similarity_score) AS max_similarity,
    AVG(similarity_score) AS avg_similarity
FROM reco.recommendations;

/*
    BUSINESS INTERPRETATION — fill in after running:
    - What's the actual coverage % — are most profiled customers
      getting recommendations, or are many falling through (e.g.
      because their top category has too few candidate products)?
    - Do the example recommendations look sensible (same/adjacent
      category, similar price point) when you look up the actual
      product details?

    BUSINESS IMPLICATION — fill in after running:
    - Whether the single-top-category candidate pool is too
      narrow for some customers (a customer whose top category has
      very few products gets very few — or zero — candidates)
*/
