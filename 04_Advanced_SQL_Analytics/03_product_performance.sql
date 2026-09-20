/*
    ============================================================
    ORGEE — Phase 4: Advanced SQL Analytics
    03_product_performance.sql
    ============================================================

    BUSINESS QUESTION
    Does price tier relate to customer satisfaction (review score)?
    Which categories have the best/worst average review scores, and
    does that correlate with return/cancellation behavior?

    TECHNIQUES USED
    CTE, CASE (price tiering), aggregation, subquery, ranking.
    ============================================================
*/

-- ------------------------------------------------------------
-- Review score by price tier
-- ------------------------------------------------------------

WITH PricedItems AS (
    SELECT
        foi.order_id,
        foi.price,
        CASE
            WHEN foi.price < 50  THEN '1. Under R$50'
            WHEN foi.price < 150 THEN '2. R$50-150'
            WHEN foi.price < 300 THEN '3. R$150-300'
            ELSE '4. R$300+'
        END AS price_tier
    FROM dbo.Fact_Order_Items foi
    WHERE foi.order_status = 'delivered'
)
SELECT
    pi.price_tier,
    COUNT(*) AS item_count,
    AVG(CAST(fr.review_score AS FLOAT)) AS avg_review_score,
    ROUND(AVG(pi.price), 2) AS avg_price
FROM PricedItems pi
JOIN dbo.Fact_Reviews fr ON pi.order_id = fr.order_id
GROUP BY pi.price_tier
ORDER BY pi.price_tier;

-- ------------------------------------------------------------
-- Category-level average review score, ranked best to worst
-- (categories with at least 30 reviewed items, to avoid noisy
-- rankings from tiny sample sizes)
-- ------------------------------------------------------------

WITH CategoryReviews AS (
    SELECT
        dp.product_category_name_english,
        COUNT(*) AS reviewed_item_count,
        AVG(CAST(fr.review_score AS FLOAT)) AS avg_review_score
    FROM dbo.Fact_Order_Items foi
    JOIN dbo.Dim_Product dp ON foi.product_sk = dp.product_sk
    JOIN dbo.Fact_Reviews fr ON foi.order_id = fr.order_id
    WHERE foi.order_status = 'delivered'
      AND dp.product_category_name_english IS NOT NULL
    GROUP BY dp.product_category_name_english
    HAVING COUNT(*) >= 30
)
SELECT
    product_category_name_english,
    reviewed_item_count,
    ROUND(avg_review_score, 2) AS avg_review_score,
    RANK() OVER (ORDER BY avg_review_score DESC) AS best_rank,
    RANK() OVER (ORDER BY avg_review_score ASC)  AS worst_rank
FROM CategoryReviews
ORDER BY avg_review_score DESC;

-- ------------------------------------------------------------
-- Cancellation rate by category (does a low review score category
-- also cancel more often?)
-- ------------------------------------------------------------

SELECT
    dp.product_category_name_english,
    COUNT(*) AS total_items,
    SUM(CASE WHEN foi.order_status = 'canceled' THEN 1 ELSE 0 END) AS canceled_items,
    ROUND(
        100.0 * SUM(CASE WHEN foi.order_status = 'canceled' THEN 1 ELSE 0 END) / COUNT(*), 2
    ) AS cancellation_rate_pct
FROM dbo.Fact_Order_Items foi
JOIN dbo.Dim_Product dp ON foi.product_sk = dp.product_sk
WHERE dp.product_category_name_english IS NOT NULL
GROUP BY dp.product_category_name_english
HAVING COUNT(*) >= 30
ORDER BY cancellation_rate_pct DESC;

/*
    BUSINESS INTERPRETATION — fill in after running:
    - Is there a meaningful price-tier / satisfaction relationship,
      or is review score roughly flat across price points?
    - Which categories are genuine outliers on review score or
      cancellation rate (not just noise from small sample size)?

    BUSINESS IMPLICATION — fill in after running:
    - Categories that need quality/fulfillment investigation
    - Whether premium pricing is currently justified by satisfaction
*/
