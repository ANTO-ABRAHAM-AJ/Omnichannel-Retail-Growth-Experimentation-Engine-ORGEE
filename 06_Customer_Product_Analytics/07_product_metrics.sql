/*
    ============================================================
    ORGEE — Phase 6: Customer & Product Analytics
    07_product_metrics.sql
    ============================================================

    BUSINESS QUESTION
    Beyond what Phase 4 (revenue/category performance) and Phase 5
    (funnel/drop-off) already established, which specific PRODUCTS
    have a large gap between demand (views) and conversion (adds
    to cart) — the most actionable, product-level version of the
    Phase 5 category-level drop-off finding?

    This deliberately does NOT repeat Phase 4's revenue ranking or
    Phase 5's category cart-to-purchase rate — it goes one level
    more granular (product, not category) and pairs interest with
    outcome, which neither prior phase did.

    TECHNIQUES USED
    CTE, CASE, aggregation, ranking.
    ============================================================
*/

-- ------------------------------------------------------------
-- Product-level view-to-cart gap: products with high view volume
-- but low add-to-cart conversion — the biggest per-product
-- opportunity, since Phase 5 already established Product View to
-- Add to Cart is the single largest funnel drop-off (62.76%)
-- ------------------------------------------------------------

WITH ProductFunnel AS (
    SELECT
        fe.product_sk,
        dp.product_id,
        dp.product_category_name_english,
        COUNT(DISTINCT CASE WHEN fe.event_type = 'product_view' THEN fe.session_id END) AS view_sessions,
        COUNT(DISTINCT CASE WHEN fe.event_type = 'add_to_cart' THEN fe.session_id END) AS cart_sessions
    FROM dbo.Fact_Events fe
    JOIN dbo.Dim_Product dp ON fe.product_sk = dp.product_sk
    WHERE fe.product_sk IS NOT NULL
    GROUP BY fe.product_sk, dp.product_id, dp.product_category_name_english
)
SELECT TOP 20
    product_id, product_category_name_english,
    view_sessions, cart_sessions,
    ROUND(100.0 * cart_sessions / NULLIF(view_sessions, 0), 2) AS view_to_cart_rate_pct,
    view_sessions - cart_sessions AS views_not_converted
FROM ProductFunnel
WHERE view_sessions >= 20
ORDER BY views_not_converted DESC;

-- ------------------------------------------------------------
-- Category demand-vs-revenue-rank matrix: compares each category's
-- revenue rank against its cart-activity VOLUME rank (not a
-- conversion rate) to flag categories where the two rankings
-- diverge — worth investigating further, not a conversion measure
-- on its own (see the rank_gap note in the interpretation block below)
-- ------------------------------------------------------------

WITH CategoryRevenue AS (
    SELECT
        dp.product_category_name_english,
        SUM(foi.price) AS total_revenue,
        RANK() OVER (ORDER BY SUM(foi.price) DESC) AS revenue_rank
    FROM dbo.Fact_Order_Items foi
    JOIN dbo.Dim_Product dp ON foi.product_sk = dp.product_sk
    WHERE foi.order_status = 'delivered' AND dp.product_category_name_english IS NOT NULL
    GROUP BY dp.product_category_name_english
),
CategoryCartConversion AS (
    SELECT
        dp.product_category_name_english,
        COUNT(DISTINCT fe.session_id) AS cart_sessions,
        RANK() OVER (ORDER BY COUNT(DISTINCT fe.session_id) DESC) AS cart_volume_rank
    FROM dbo.Fact_Events fe
    JOIN dbo.Dim_Product dp ON fe.product_sk = dp.product_sk
    WHERE fe.event_type = 'add_to_cart' AND dp.product_category_name_english IS NOT NULL
    GROUP BY dp.product_category_name_english
)
SELECT TOP 15
    cr.product_category_name_english,
    cr.revenue_rank,
    ccc.cart_volume_rank,
    cr.total_revenue,
    ccc.cart_sessions,
    (cr.revenue_rank - ccc.cart_volume_rank) AS rank_gap
FROM CategoryRevenue cr
JOIN CategoryCartConversion ccc ON cr.product_category_name_english = ccc.product_category_name_english
ORDER BY cr.revenue_rank;

/*
    BUSINESS INTERPRETATION — fill in after running:
    - Which specific products have the largest raw count of
      "interested but didn't cart" sessions — these are concrete,
      actionable product-page candidates, not abstract categories.
      This product-level view-to-cart gap (Result Set 1) is the
      stronger, more direct evidence of a conversion problem.
    - NOTE ON rank_gap (Result Set 2): rank_gap = revenue_rank minus
      cart_volume_rank. This measures whether a category's revenue
      ranking sits higher or lower than its cart-activity ranking —
      it is a relative-ranking comparison, NOT a direct conversion
      rate, and should not be read as "this category converts
      poorly." A positive gap means the category generates more
      cart interest than its revenue rank alone would suggest (revenue
      rank is numerically worse/higher than cart-volume rank); a
      negative gap means the reverse. Either direction could reflect
      price point, AOV, or product mix just as easily as conversion
      efficiency — treat rank_gap as a prioritization signal to
      investigate further, not a conclusion in itself.
      specific to that category, not a demand problem

    BUSINESS IMPLICATION — fill in after running:
    - Feeds directly into 08_feature_prioritization.sql as the
      product-level evidence base
*/
