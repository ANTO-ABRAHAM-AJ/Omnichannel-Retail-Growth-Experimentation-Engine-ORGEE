/*
    ============================================================
    ORGEE — Phase 7: Recommendation Intelligence
    01_recommendation_data_preparation.sql
    ============================================================

    BUSINESS QUESTION
    Do we have the right customer-product interaction data to
    build a content-based recommendation engine?

    LOCKED DESIGN DECISIONS (made before writing any SQL, per the
    review that preceded this script):

    1. PRIMARY SIGNAL = Purchases (Fact_Order_Items). Always
       identified (every row has a resolved customer_sk), covers
       all 93,358 purchasing customers. This is the backbone of
       every customer's preference profile.

    2. SECONDARY SIGNAL = Product Views / Add-to-Cart
       (Fact_Events). Only ~18% of Fact_Events rows ever resolve to
       a known customer_sk (the anonymous-until-login design from
       Phase 2/3) — the other 82% of behavioral activity has NO
       attached customer identity and CANNOT feed a per-customer
       profile. Filtered to customer_sk IS NOT NULL below. This
       means view/cart signal only enriches profiles for the
       identified subset of customers, not everyone.

    3. INTERACTION WEIGHTING (explicit, documented, not hidden):
           product_view    -> weight 1.0  (low signal)
           add_to_cart     -> weight 2.0  (medium signal)
           purchase        -> weight 3.0  (strong signal)
       A simple linear scale reflecting the ordinal strength
       relationship — not derived from any statistical fitting,
       stated plainly as a design choice.

    4. product price does not exist as a column on Dim_Product —
       it's a transaction attribute (Fact_Order_Items.price varies
       by order). Purchase-interaction rows carry the actual price
       paid; view/cart-interaction rows carry the product's average
       observed transaction price (computed once below), since no
       transaction price exists for a view or cart action.

    OUTPUT
    dbo.reco (schema) . interactions table:
        customer_unique_id, product_id, product_sk,
        interaction_type, interaction_weight, interaction_date,
        product_category_name_english, price

    TECHNIQUES USED
    Schema creation, CTE, UNION ALL, aggregation.
    ============================================================
*/

IF SCHEMA_ID('reco') IS NULL
    EXEC('CREATE SCHEMA reco');
GO

IF OBJECT_ID('reco.interactions', 'U') IS NOT NULL DROP TABLE reco.interactions;

CREATE TABLE reco.interactions (
    interaction_sk                  BIGINT IDENTITY(1,1) NOT NULL,
    customer_unique_id              VARCHAR(32)          NOT NULL,
    product_id                      VARCHAR(32)          NOT NULL,
    product_sk                      INT                  NOT NULL,
    interaction_type                VARCHAR(20)          NOT NULL,  -- product_view, add_to_cart, purchase
    interaction_weight               DECIMAL(3,1)         NOT NULL,
    interaction_date                DATE                 NULL,
    product_category_name_english   VARCHAR(60)          NULL,
    price                           DECIMAL(10,2)        NULL,

    CONSTRAINT PK_reco_interactions PRIMARY KEY CLUSTERED (interaction_sk)
);
GO

-- ------------------------------------------------------------
-- Average observed transaction price per product — used to give
-- view/cart interaction rows a price value (they have no
-- transaction price of their own)
-- ------------------------------------------------------------

IF OBJECT_ID('tempdb..#AvgProductPrice') IS NOT NULL DROP TABLE #AvgProductPrice;

SELECT
    product_sk,
    AVG(price) AS avg_price
INTO #AvgProductPrice
FROM dbo.Fact_Order_Items
WHERE order_status = 'delivered'
GROUP BY product_sk;

-- ------------------------------------------------------------
-- PRIMARY SIGNAL: Purchases (always identified)
-- ------------------------------------------------------------

INSERT INTO reco.interactions (
    customer_unique_id, product_id, product_sk, interaction_type,
    interaction_weight, interaction_date, product_category_name_english, price
)
SELECT
    dc.customer_unique_id,
    dp.product_id,
    foi.product_sk,
    'purchase',
    3.0,
    d.full_date,
    dp.product_category_name_english,
    foi.price
FROM dbo.Fact_Order_Items foi
JOIN dbo.Dim_Customer dc ON foi.customer_sk = dc.customer_sk
JOIN dbo.Dim_Product dp ON foi.product_sk = dp.product_sk
JOIN dbo.Dim_Date d ON foi.order_purchase_date_sk = d.date_sk
WHERE foi.order_status = 'delivered';

-- ------------------------------------------------------------
-- SECONDARY SIGNAL: Product views / cart adds — IDENTIFIED
-- sessions only (customer_sk IS NOT NULL)
-- ------------------------------------------------------------

INSERT INTO reco.interactions (
    customer_unique_id, product_id, product_sk, interaction_type,
    interaction_weight, interaction_date, product_category_name_english, price
)
SELECT
    dc.customer_unique_id,
    dp.product_id,
    fe.product_sk,
    fe.event_type,
    CASE fe.event_type WHEN 'product_view' THEN 1.0 WHEN 'add_to_cart' THEN 2.0 END,
    CAST(fe.event_timestamp AS DATE),
    dp.product_category_name_english,
    app.avg_price
FROM dbo.Fact_Events fe
JOIN dbo.Dim_Customer dc ON fe.customer_sk = dc.customer_sk
JOIN dbo.Dim_Product dp ON fe.product_sk = dp.product_sk
LEFT JOIN #AvgProductPrice app ON fe.product_sk = app.product_sk
WHERE fe.event_type IN ('product_view', 'add_to_cart')
  AND fe.customer_sk IS NOT NULL
  AND fe.product_sk IS NOT NULL;

DROP TABLE #AvgProductPrice;

-- ------------------------------------------------------------
-- Data sufficiency summary — does this dataset support building
-- a recommendation engine?
-- ------------------------------------------------------------

SELECT
    interaction_type,
    COUNT(*) AS interaction_count,
    COUNT(DISTINCT customer_unique_id) AS distinct_customers,
    COUNT(DISTINCT product_id) AS distinct_products
FROM reco.interactions
GROUP BY interaction_type
ORDER BY interaction_type;

SELECT
    COUNT(*) AS total_interactions,
    COUNT(DISTINCT customer_unique_id) AS total_customers_with_any_interaction,
    COUNT(DISTINCT product_id) AS total_products_with_any_interaction,
    (SELECT COUNT(DISTINCT customer_unique_id) FROM dbo.Dim_Customer) AS total_customers_in_warehouse,
    -- ^ FIX: was COUNT(*) FROM Dim_Customer (99,441 — customer_id
    -- grain, one row per order). That mismatched the grain of every
    -- other column in this row (customer_unique_id). Corrected to
    -- COUNT(DISTINCT customer_unique_id) — the real person count
    -- (96,096) — for an apples-to-apples coverage percentage.
    (SELECT COUNT(*) FROM dbo.Dim_Product) AS total_products_in_warehouse
FROM reco.interactions;

-- ------------------------------------------------------------
-- Interaction depth per customer — how many customers have
-- ENOUGH interaction history for a meaningful preference profile
-- (a customer with exactly 1 purchase and nothing else has a
-- valid but very thin profile — worth knowing the distribution)
-- ------------------------------------------------------------

WITH CustomerInteractionCounts AS (
    SELECT customer_unique_id, COUNT(*) AS interaction_count
    FROM reco.interactions
    GROUP BY customer_unique_id
)
SELECT
    CASE
        WHEN interaction_count = 1 THEN '1. Single interaction'
        WHEN interaction_count BETWEEN 2 AND 3 THEN '2. 2-3 interactions'
        WHEN interaction_count BETWEEN 4 AND 10 THEN '3. 4-10 interactions'
        ELSE '4. 11+ interactions'
    END AS interaction_depth_bucket,
    COUNT(*) AS customer_count
FROM CustomerInteractionCounts
GROUP BY
    CASE
        WHEN interaction_count = 1 THEN '1. Single interaction'
        WHEN interaction_count BETWEEN 2 AND 3 THEN '2. 2-3 interactions'
        WHEN interaction_count BETWEEN 4 AND 10 THEN '3. 4-10 interactions'
        ELSE '4. 11+ interactions'
    END
ORDER BY interaction_depth_bucket;

/*
    BUSINESS INTERPRETATION — fill in after running:
    - How much of the total behavioral data is actually usable
      (identified) vs lost to the anonymous-until-login design?
    - What fraction of customers have only a single interaction
      (thin profile — recommendations for these customers will
      lean almost entirely on their one purchase's category/price)

    BUSINESS IMPLICATION — fill in after running:
    - Whether the identified-only view/cart signal adds meaningful
      enrichment, or whether purchases alone will carry most of
      the profile-building work in Script 03
*/
