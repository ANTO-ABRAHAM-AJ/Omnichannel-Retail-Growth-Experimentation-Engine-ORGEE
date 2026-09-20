/*
    ============================================================
    ORGEE — Phase 7: Recommendation Intelligence
    03_customer_preference_profiles.sql
    ============================================================

    BUSINESS QUESTION
    What does each customer appear to prefer, based on their
    observed behavior — not a stated preference, an inferred one?

    METHODOLOGY (explicit, documented):
    1. For each (customer, product) pair, sum ALL interaction
       weights the customer has with that product (e.g. a customer
       who viewed a product (1.0), added it to cart (2.0), AND
       purchased it (3.0) gets a combined interest weight of 6.0
       for that product — stronger evidence than a single purchase
       alone). This is a deliberate design choice: repeated/varied
       engagement with the same product is treated as a stronger
       signal than one-off engagement.
    2. A customer's preference profile is the WEIGHTED SUM (not an
       average) of every interacted product's feature vector,
       weighted by that product's combined interest weight from
       step 1. Using a sum rather than an average is intentional —
       cosine similarity (Script 04) normalizes by vector magnitude
       at comparison time anyway, so the profile's raw scale does
       not need to be pre-normalized here.
    3. This is BEHAVIORAL PREFERENCE INFERENCE, not a claim the
       customer explicitly stated a preference — stated plainly per
       the plan's analytical principle.

    OUTPUT
    reco.customer_preferences: customer_unique_id, feature_name,
    preference_value — the SAME feature space as
    reco.product_features, which is what makes direct cosine
    similarity comparison possible in Script 04.

    TECHNIQUES USED
    CTE, aggregation, weighted sum.
    ============================================================
*/

IF OBJECT_ID('reco.customer_preferences', 'U') IS NOT NULL DROP TABLE reco.customer_preferences;

CREATE TABLE reco.customer_preferences (
    pref_sk               BIGINT IDENTITY(1,1) NOT NULL,
    customer_unique_id     VARCHAR(32)          NOT NULL,
    feature_name           VARCHAR(80)          NOT NULL,
    preference_value        DECIMAL(14,6)        NOT NULL,

    CONSTRAINT PK_reco_customer_preferences PRIMARY KEY CLUSTERED (pref_sk)
);
GO

-- ------------------------------------------------------------
-- Step 1: combined interest weight per (customer, product)
-- ------------------------------------------------------------

IF OBJECT_ID('tempdb..#CustomerProductInterest') IS NOT NULL DROP TABLE #CustomerProductInterest;

SELECT
    customer_unique_id,
    product_sk,
    SUM(interaction_weight) AS total_interest_weight
INTO #CustomerProductInterest
FROM reco.interactions
GROUP BY customer_unique_id, product_sk;

-- ------------------------------------------------------------
-- Step 2: weighted-sum preference profile per customer, across
-- the same feature space as reco.product_features
-- ------------------------------------------------------------

INSERT INTO reco.customer_preferences (customer_unique_id, feature_name, preference_value)
SELECT
    cpi.customer_unique_id,
    pf.feature_name,
    SUM(cpi.total_interest_weight * pf.feature_value)
FROM #CustomerProductInterest cpi
JOIN reco.product_features pf ON cpi.product_sk = pf.product_sk
GROUP BY cpi.customer_unique_id, pf.feature_name;

DROP TABLE #CustomerProductInterest;

-- ------------------------------------------------------------
-- Coverage: how many customers now have a preference profile?
-- ------------------------------------------------------------

SELECT
    COUNT(DISTINCT customer_unique_id) AS customers_with_a_profile,
    (SELECT COUNT(DISTINCT customer_unique_id) FROM dbo.Dim_Customer) AS total_customers_in_warehouse,
    (SELECT COUNT(DISTINCT customer_unique_id) FROM reco.interactions) AS customers_with_any_interaction
FROM reco.customer_preferences;

-- ------------------------------------------------------------
-- Profile richness — how many distinct features does each
-- customer's profile actually span? (a customer whose only
-- interaction was one product with a missing category feature,
-- say, would have a very sparse profile)
-- ------------------------------------------------------------

WITH ProfileRichness AS (
    SELECT customer_unique_id, COUNT(DISTINCT feature_name) AS feature_count
    FROM reco.customer_preferences
    GROUP BY customer_unique_id
)
SELECT
    CASE
        WHEN feature_count <= 2 THEN '1. Very sparse (<=2 features)'
        WHEN feature_count BETWEEN 3 AND 4 THEN '2. Sparse (3-4 features)'
        ELSE '3. Full profile (5+ features)'
    END AS richness_bucket,
    COUNT(*) AS customer_count
FROM ProfileRichness
GROUP BY
    CASE
        WHEN feature_count <= 2 THEN '1. Very sparse (<=2 features)'
        WHEN feature_count BETWEEN 3 AND 4 THEN '2. Sparse (3-4 features)'
        ELSE '3. Full profile (5+ features)'
    END
ORDER BY richness_bucket;

-- ------------------------------------------------------------
-- Example: top 5 category preferences for 3 sample customers
-- (human-readable illustration, matching the plan's bar-chart
-- example — highest preference_value = strongest inferred category)
-- ------------------------------------------------------------

WITH SampleCustomers AS (
    SELECT DISTINCT TOP 3 customer_unique_id
    FROM reco.customer_preferences
    WHERE feature_name LIKE 'cat_%'
    ORDER BY customer_unique_id
)
SELECT
    cp.customer_unique_id,
    cp.feature_name AS category,
    cp.preference_value,
    RANK() OVER (PARTITION BY cp.customer_unique_id ORDER BY cp.preference_value DESC) AS preference_rank
FROM reco.customer_preferences cp
JOIN SampleCustomers sc ON cp.customer_unique_id = sc.customer_unique_id
WHERE cp.feature_name LIKE 'cat_%'
ORDER BY cp.customer_unique_id, preference_rank;

/*
    BUSINESS INTERPRETATION — fill in after running:
    - What fraction of customers end up with a full 5-feature
      profile vs a sparse one?
    - Does profile richness roughly track the interaction-depth
      distribution already seen in Script 01?

    BUSINESS IMPLICATION — fill in after running:
    - Whether sparse-profile customers need a fallback
      recommendation strategy in Script 04 (e.g. popularity-based
      recommendations) rather than pure content similarity
*/
