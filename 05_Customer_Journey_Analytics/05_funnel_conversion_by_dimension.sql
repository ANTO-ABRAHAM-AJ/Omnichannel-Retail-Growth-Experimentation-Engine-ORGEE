/*
    ============================================================
    ORGEE — Phase 5: Customer Journey Analytics
    05_funnel_conversion_by_dimension.sql
    ============================================================

    BUSINESS QUESTION
    Does the funnel convert differently across device types? Do
    certain product categories see a stronger add-to-cart-to-
    purchase rate than others?

    TECHNIQUES USED
    CTE, CASE, aggregation, ranking.
    ============================================================
*/

-- ------------------------------------------------------------
-- Funnel by device_type
-- ------------------------------------------------------------

WITH StageSessions AS (
    SELECT
        fe.session_id,
        dd.device_type,
        MAX(CASE WHEN fe.event_type = 'session_start'          THEN 1 ELSE 0 END) AS visit,
        MAX(CASE WHEN fe.event_type = 'product_view'            THEN 1 ELSE 0 END) AS product_view,
        MAX(CASE WHEN fe.event_type = 'add_to_cart'               THEN 1 ELSE 0 END) AS add_to_cart,
        MAX(CASE WHEN fe.event_type = 'checkout_start'              THEN 1 ELSE 0 END) AS checkout,
        MAX(CASE WHEN fe.event_type = 'purchase_interaction'           THEN 1 ELSE 0 END) AS purchase
    FROM dbo.Fact_Events fe
    LEFT JOIN dbo.Dim_Device dd ON fe.device_sk = dd.device_sk
    GROUP BY fe.session_id, dd.device_type
)
SELECT
    device_type,
    SUM(visit) AS visits,
    SUM(product_view) AS product_views,
    SUM(add_to_cart) AS add_to_carts,
    SUM(checkout) AS checkouts,
    SUM(purchase) AS purchases,
    ROUND(100.0 * SUM(purchase) / NULLIF(SUM(visit), 0), 2) AS overall_conversion_rate_pct
FROM StageSessions
GROUP BY device_type
ORDER BY overall_conversion_rate_pct DESC;

-- ------------------------------------------------------------
-- Funnel by platform
-- ------------------------------------------------------------

WITH StageSessions AS (
    SELECT
        fe.session_id,
        dd.platform,
        MAX(CASE WHEN fe.event_type = 'session_start'          THEN 1 ELSE 0 END) AS visit,
        MAX(CASE WHEN fe.event_type = 'purchase_interaction'    THEN 1 ELSE 0 END) AS purchase
    FROM dbo.Fact_Events fe
    LEFT JOIN dbo.Dim_Device dd ON fe.device_sk = dd.device_sk
    GROUP BY fe.session_id, dd.platform
)
SELECT
    platform,
    SUM(visit) AS visits,
    SUM(purchase) AS purchases,
    ROUND(100.0 * SUM(purchase) / NULLIF(SUM(visit), 0), 2) AS conversion_rate_pct,
    RANK() OVER (ORDER BY 100.0 * SUM(purchase) / NULLIF(SUM(visit), 0) DESC) AS conversion_rank
FROM StageSessions
GROUP BY platform;

-- ------------------------------------------------------------
-- Add-to-cart-to-purchase rate by product category
-- (which categories convert cart adds into purchases best?)
--
-- NOTE: "purchased" means the session had a purchase_interaction
-- event anywhere in it — the synthetic event data doesn't tie
-- purchase_interaction to a specific product_sk. Treat this as a
-- session-level association, not a strict per-item conversion rate.
-- ------------------------------------------------------------

WITH CartAdds AS (
    SELECT DISTINCT
        fe.session_id,
        dp.product_category_name_english
    FROM dbo.Fact_Events fe
    JOIN dbo.Dim_Product dp ON fe.product_sk = dp.product_sk
    WHERE fe.event_type = 'add_to_cart'
),
PurchaseEvents AS (
    SELECT DISTINCT session_id
    FROM dbo.Fact_Events
    WHERE event_type = 'purchase_interaction'
)
SELECT TOP 15
    ca.product_category_name_english,
    COUNT(DISTINCT ca.session_id) AS cart_adds,
    COUNT(DISTINCT CASE WHEN pe.session_id IS NOT NULL THEN ca.session_id END) AS sessions_that_also_purchased,
    ROUND(
        100.0 * COUNT(DISTINCT CASE WHEN pe.session_id IS NOT NULL THEN ca.session_id END)
        / NULLIF(COUNT(DISTINCT ca.session_id), 0), 2
    ) AS cart_to_purchase_rate_pct
FROM CartAdds ca
LEFT JOIN PurchaseEvents pe ON ca.session_id = pe.session_id
GROUP BY ca.product_category_name_english
HAVING COUNT(DISTINCT ca.session_id) >= 30
ORDER BY cart_to_purchase_rate_pct DESC;



/*
    BUSINESS INTERPRETATION — fill in after running:
    - Does device/platform meaningfully change conversion, or is
      it roughly flat across the board?
    - Which categories convert cart interest into purchase best/worst?

    BUSINESS IMPLICATION — fill in after running:
    - Whether device-specific UX investment is justified by the
      data, or whether the funnel problem is universal
*/
