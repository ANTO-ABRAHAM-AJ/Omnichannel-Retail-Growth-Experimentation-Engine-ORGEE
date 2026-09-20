/*
    ============================================================
    ORGEE — Phase 8: Experimentation Framework
    04_experiment_metrics.sql ⭐ SIGNATURE SCRIPT
    ============================================================

    BUSINESS QUESTION
    How did Control and Treatment actually perform, across the
    primary metric and the locked secondary metrics?

    METRIC DEFINITIONS (locked, explicit):
    - Purchase Conversion Rate (PRIMARY): eligible customers with
      >=1 'recommendation_conversion' event, divided by eligible
      customers. Binary per-customer — did they convert at all.
    - Recommendation CTR: recommendation_click events divided by
      recommendation_impression events.
    - Purchase Rate (distinct from the primary metric): total
      recommendation_conversion EVENTS divided by eligible
      customers — captures repeat-conversion behavior (a customer
      converting twice counts twice here, unlike the primary
      metric's binary "did they convert at all").
    - AOV / Revenue per User: Fact_Recommendation_Events has NO
      price/revenue column — recommendation_conversion is a
      self-contained synthetic signal never tied to real
      Fact_Order_Items amounts (established in Script 01's design
      notes). Both metrics use a PROXY: each conversion's
      recommended product's average observed catalog price (from
      real delivered transactions) — clearly labeled as a proxy,
      NOT actual revenue collected, exactly the same approach used
      for the identical gap in Phase 7 Script 01.

    All metrics computed on the ELIGIBLE population only (2,223
    control / 2,188 treatment, confirmed SRM-clean in Script 03).

    TECHNIQUES USED
    CTE, aggregation, proxy-value join.
    ============================================================
*/

DECLARE @Exp1Sk INT = (SELECT experiment_sk FROM dbo.Dim_Experiment WHERE experiment_id = 'exp_001');

IF OBJECT_ID('tempdb..#ProductAvgPrice') IS NOT NULL DROP TABLE #ProductAvgPrice;
SELECT product_sk, AVG(price) AS avg_price
INTO #ProductAvgPrice
FROM dbo.Fact_Order_Items
WHERE order_status = 'delivered'
GROUP BY product_sk;

-- ------------------------------------------------------------
-- Primary metric: Purchase Conversion Rate
-- ------------------------------------------------------------

;WITH ConvertedCustomers AS (
    SELECT DISTINCT customer_sk
    FROM dbo.Fact_Recommendation_Events
    WHERE experiment_sk = @Exp1Sk AND event_type = 'recommendation_conversion'
)
SELECT
    ep.variant,
    COUNT(*) AS eligible_participants,
    SUM(CASE WHEN cc.customer_sk IS NOT NULL THEN 1 ELSE 0 END) AS converting_participants,
    ROUND(100.0 * SUM(CASE WHEN cc.customer_sk IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 4) AS purchase_conversion_rate_pct
FROM expt.experiment_population ep
LEFT JOIN ConvertedCustomers cc ON cc.customer_sk = ep.customer_sk
WHERE ep.is_eligible = 1
GROUP BY ep.variant;

-- ------------------------------------------------------------
-- Secondary metric: Recommendation CTR
-- ------------------------------------------------------------

SELECT
    ep.variant,
    SUM(CASE WHEN fre.event_type = 'recommendation_impression' THEN 1 ELSE 0 END) AS impressions,
    SUM(CASE WHEN fre.event_type = 'recommendation_click' THEN 1 ELSE 0 END) AS clicks,
    ROUND(100.0 * SUM(CASE WHEN fre.event_type = 'recommendation_click' THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN fre.event_type = 'recommendation_impression' THEN 1 ELSE 0 END), 0), 4) AS ctr_pct
FROM expt.experiment_population ep
JOIN dbo.Fact_Recommendation_Events fre ON fre.customer_sk = ep.customer_sk AND fre.experiment_sk = @Exp1Sk
WHERE ep.is_eligible = 1
GROUP BY ep.variant;

-- ------------------------------------------------------------
-- Secondary metric: Purchase Rate (total conversion EVENTS per
-- eligible customer — distinct from the binary primary metric)
-- ------------------------------------------------------------

SELECT
    ep.variant,
    COUNT(DISTINCT ep.customer_sk) AS eligible_participants,
    SUM(CASE WHEN fre.event_type = 'recommendation_conversion' THEN 1 ELSE 0 END) AS total_conversion_events,
    ROUND(1.0 * SUM(CASE WHEN fre.event_type = 'recommendation_conversion' THEN 1 ELSE 0 END) / COUNT(DISTINCT ep.customer_sk), 4) AS purchase_rate
FROM expt.experiment_population ep
LEFT JOIN dbo.Fact_Recommendation_Events fre ON fre.customer_sk = ep.customer_sk AND fre.experiment_sk = @Exp1Sk
WHERE ep.is_eligible = 1
GROUP BY ep.variant;

-- ------------------------------------------------------------
-- Secondary metrics: AOV (proxy) and Revenue per User (proxy)
-- ------------------------------------------------------------

;WITH ConversionProxyValue AS (
    SELECT
        ep.variant,
        ep.customer_sk,
        pap.avg_price AS proxy_value
    FROM expt.experiment_population ep
    JOIN dbo.Fact_Recommendation_Events fre ON fre.customer_sk = ep.customer_sk AND fre.experiment_sk = @Exp1Sk
    JOIN #ProductAvgPrice pap ON pap.product_sk = fre.product_sk
    WHERE ep.is_eligible = 1 AND fre.event_type = 'recommendation_conversion'
)
SELECT
    ep.variant,
    COUNT(DISTINCT ep.customer_sk) AS eligible_participants,
    COUNT(cpv.proxy_value) AS conversions_with_proxy_value,
    ROUND(AVG(cpv.proxy_value), 2) AS aov_proxy,
    ROUND(SUM(ISNULL(cpv.proxy_value, 0)) / COUNT(DISTINCT ep.customer_sk), 2) AS revenue_per_user_proxy
FROM expt.experiment_population ep
LEFT JOIN ConversionProxyValue cpv ON cpv.customer_sk = ep.customer_sk AND cpv.variant = ep.variant
WHERE ep.is_eligible = 1
GROUP BY ep.variant;

DROP TABLE #ProductAvgPrice;

/*
    BUSINESS INTERPRETATION — fill in after running:
    - What are the actual Control vs Treatment numbers for each
      metric?
    - Does Treatment show higher, lower, or essentially identical
      conversion compared to Control?
    - Recall the design expectation set in Script 01: the
      generator applied identical click/conversion probabilities
      to both variants — so a near-identical result here would be
      the EXPECTED, honest outcome, not a sign something is wrong.

    BUSINESS IMPLICATION — fill in after running:
    - Feeds directly into Script 05's statistical significance test
      on the primary metric
*/
