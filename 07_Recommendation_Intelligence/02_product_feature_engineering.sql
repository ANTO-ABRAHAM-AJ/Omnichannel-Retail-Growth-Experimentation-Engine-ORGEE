/*
    ============================================================
    ORGEE — Phase 7: Recommendation Intelligence
    02_product_feature_engineering.sql
    ============================================================

    BUSINESS QUESTION
    How do we represent products so that similar products can be
    identified mathematically?

    FEATURE SET (explicit, documented — not a sophisticated model,
    just a sensible, honest definition of product similarity):

        1. Category           — one-hot flag (cat_<category>), the
                                 dominant signal. ~1.9% of products
                                 (623, known Olist source gap — see
                                 Phase 3/6) have no category at all
                                 and simply get no category feature.
        2. Average price       — min-max normalized. Computed from
                                 actual delivered transactions
                                 (Dim_Product has no price column —
                                 price is a transaction attribute).
                                 ~735 products with zero purchase
                                 history get NO price feature at all
                                 — we do not fabricate a price for
                                 them; their similarity relies on
                                 category + physical attributes only.
        3. Weight              — min-max normalized product_weight_g.
        4. Volume              — length_cm x height_cm x width_cm,
                                 min-max normalized. Combined into
                                 one "physical size" feature rather
                                 than 3 separate dimension features,
                                 to avoid over-weighting size vs
                                 category in the similarity math.
        5. Photo count          — min-max normalized product_photos_qty.

    REPRESENTATION: a long/tall table (product_sk, feature_name,
    feature_value) rather than a wide 70+-column table. This is the
    standard SQL pattern for cosine similarity — a missing feature
    for a product simply means that row doesn't exist, and
    contributes 0 to any dot product naturally (no need to store
    explicit zeros for 72 non-matching categories per product).

    NO HIDDEN WEIGHTING: category is stored as a flat 1.0 flag,
    equal footing with each individual normalized numeric feature.
    This means, structurally, two products sharing a category
    contribute more to a raw dot product than any single numeric
    feature agreement — an intentional, stated design choice (category
    is normally the dominant signal in retail recommendation), not
    an accident of scaling.

    TECHNIQUES USED
    Long-format feature table, min-max normalization, CTE.
    ============================================================
*/

IF OBJECT_ID('reco.product_features', 'U') IS NOT NULL DROP TABLE reco.product_features;

CREATE TABLE reco.product_features (
    feature_sk      BIGINT IDENTITY(1,1) NOT NULL,
    product_sk      INT                  NOT NULL,
    feature_name    VARCHAR(80)          NOT NULL,
    feature_value   DECIMAL(10,6)        NOT NULL,

    CONSTRAINT PK_reco_product_features PRIMARY KEY CLUSTERED (feature_sk)
);
GO

-- ------------------------------------------------------------
-- Feature 1: Category (one-hot flag, category-having products only)
-- ------------------------------------------------------------

INSERT INTO reco.product_features (product_sk, feature_name, feature_value)
SELECT
    product_sk,
    CONCAT('cat_', product_category_name_english),
    1.0
FROM dbo.Dim_Product
WHERE product_category_name_english IS NOT NULL;

-- ------------------------------------------------------------
-- Feature 2: Average price (min-max normalized) — products with
-- delivered purchase history only
-- ------------------------------------------------------------

IF OBJECT_ID('tempdb..#ProductAvgPrice') IS NOT NULL DROP TABLE #ProductAvgPrice;

SELECT product_sk, AVG(price) AS avg_price
INTO #ProductAvgPrice
FROM dbo.Fact_Order_Items
WHERE order_status = 'delivered'
GROUP BY product_sk;

INSERT INTO reco.product_features (product_sk, feature_name, feature_value)
SELECT
    product_sk,
    'price_norm',
    CASE
        WHEN (SELECT MAX(avg_price) FROM #ProductAvgPrice) = (SELECT MIN(avg_price) FROM #ProductAvgPrice) THEN 0.5
        ELSE (avg_price - (SELECT MIN(avg_price) FROM #ProductAvgPrice))
             / ((SELECT MAX(avg_price) FROM #ProductAvgPrice) - (SELECT MIN(avg_price) FROM #ProductAvgPrice))
    END
FROM #ProductAvgPrice;

DROP TABLE #ProductAvgPrice;

-- ------------------------------------------------------------
-- Feature 3: Weight (min-max normalized)
-- ------------------------------------------------------------

INSERT INTO reco.product_features (product_sk, feature_name, feature_value)
SELECT
    product_sk,
    'weight_norm',
    (product_weight_g - MIN(product_weight_g) OVER ())
        / NULLIF(MAX(product_weight_g) OVER () - MIN(product_weight_g) OVER (), 0)
FROM dbo.Dim_Product
WHERE product_weight_g IS NOT NULL;

-- ------------------------------------------------------------
-- Feature 4: Volume = length x height x width (min-max normalized)
-- ------------------------------------------------------------

WITH ProductVolume AS (
    SELECT
        product_sk,
        product_length_cm * product_height_cm * product_width_cm AS volume_cm3
    FROM dbo.Dim_Product
    WHERE product_length_cm IS NOT NULL
      AND product_height_cm IS NOT NULL
      AND product_width_cm IS NOT NULL
)
INSERT INTO reco.product_features (product_sk, feature_name, feature_value)
SELECT
    product_sk,
    'volume_norm',
    (volume_cm3 - MIN(volume_cm3) OVER ())
        / NULLIF(MAX(volume_cm3) OVER () - MIN(volume_cm3) OVER (), 0)
FROM ProductVolume;

-- ------------------------------------------------------------
-- Feature 5: Photo count (min-max normalized)
-- ------------------------------------------------------------

INSERT INTO reco.product_features (product_sk, feature_name, feature_value)
SELECT
    product_sk,
    'photos_norm',
    (CAST(product_photos_qty AS DECIMAL(10,4)) - MIN(product_photos_qty) OVER ())
        / NULLIF(MAX(product_photos_qty) OVER () - MIN(product_photos_qty) OVER (), 0)
FROM dbo.Dim_Product
WHERE product_photos_qty IS NOT NULL;

-- ------------------------------------------------------------
-- Feature coverage summary — how many products have each feature?
-- ------------------------------------------------------------

SELECT
    CASE
        WHEN feature_name LIKE 'cat_%' THEN 'category (any)'
        ELSE feature_name
    END AS feature_group,
    COUNT(DISTINCT product_sk) AS products_with_this_feature
FROM reco.product_features
GROUP BY CASE WHEN feature_name LIKE 'cat_%' THEN 'category (any)' ELSE feature_name END
ORDER BY feature_group;

-- ------------------------------------------------------------
-- Products with ZERO features at all — these cannot be compared
-- to anything and will need explicit handling in Script 04
-- ------------------------------------------------------------

SELECT COUNT(*) AS products_with_no_features_at_all
FROM dbo.Dim_Product dp
WHERE NOT EXISTS (
    SELECT 1 FROM reco.product_features pf WHERE pf.product_sk = dp.product_sk
);

-- ------------------------------------------------------------
-- Distinct category count actually represented (sanity check
-- against the known 73-category catalog)
-- ------------------------------------------------------------

SELECT COUNT(DISTINCT feature_name) AS distinct_category_features
FROM reco.product_features
WHERE feature_name LIKE 'cat_%';

/*
    BUSINESS INTERPRETATION — fill in after running:
    - How many products, if any, have zero features (a real
      coverage gap for the engine)?
    - Does the category feature count match the known 73-category
      catalog?

    BUSINESS IMPLICATION — fill in after running:
    - Whether any product population is too sparse to recommend
      reliably, which shapes expectations for Script 04's coverage
*/
