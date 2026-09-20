/*
    ============================================================
    ORGEE — Phase 8: Experimentation Framework
    06_experiment_readout.sql ⭐ SIGNATURE SCRIPT
    ============================================================

    BUSINESS QUESTION
    Bring every major finding from Scripts 01-05 into one
    consolidated, executive-readable readout.

    BUG FOUND AND FIXED: a first version of this script tried to
    consolidate the 4 metric calculations (already validated
    correctly, in isolation, in Script 04) into fewer combined
    CTEs. That consolidation introduced two real bugs: (1) joining
    the eligible population to BOTH a 1-row-per-customer table
    (converted customers) AND a many-rows-per-customer table
    (Fact_Recommendation_Events) in the same CTE caused the
    conversion flag to fan out and be counted once per EVENT
    instead of once per CUSTOMER (conversion rate came back ~4.7x
    too high); (2) computing revenue-per-user's denominator inside
    a query already filtered to conversion events restricted
    COUNT(DISTINCT customer_sk) to converting customers only,
    instead of the full eligible population (revenue-per-user
    collapsed to nearly equal AOV). Fixed by reverting to 4
    properly ISOLATED calculations, mirroring Script 04's
    already-confirmed-correct structure exactly, rather than
    merging them.

    DESIGN NOTE: the executive metric table below is RECOMPUTED
    via SQL against the live warehouse — not copy-pasted from
    earlier screenshots — so it stays self-validating. The
    statistical summary block (p-value, CI) intentionally
    REPORTS the already-validated figures from Script 05 rather
    than reimplementing the statistical approximation a second time —
    one source of truth for the actual hypothesis test, not two
    parallel implementations that could disagree.

    TECHNIQUES USED
    CTE, aggregation, isolated per-metric temp tables, UNION ALL.
    ============================================================
*/

DECLARE @Exp1Sk INT = (SELECT experiment_sk FROM dbo.Dim_Experiment WHERE experiment_id = 'exp_001');

IF OBJECT_ID('tempdb..#ConvertedCustomers') IS NOT NULL DROP TABLE #ConvertedCustomers;
SELECT DISTINCT customer_sk INTO #ConvertedCustomers
FROM dbo.Fact_Recommendation_Events WHERE experiment_sk = @Exp1Sk AND event_type = 'recommendation_conversion';

IF OBJECT_ID('tempdb..#ProductAvgPrice') IS NOT NULL DROP TABLE #ProductAvgPrice;
SELECT product_sk, AVG(price) AS avg_price INTO #ProductAvgPrice
FROM dbo.Fact_Order_Items WHERE order_status = 'delivered' GROUP BY product_sk;

-- ------------------------------------------------------------
-- Metric 1: Purchase Conversion Rate (ISOLATED — ep joined only
-- to the 1-row-per-customer converted-customers table)
-- ------------------------------------------------------------

IF OBJECT_ID('tempdb..#M1_Conversion') IS NOT NULL DROP TABLE #M1_Conversion;
SELECT
    ep.variant,
    COUNT(*) AS eligible_n,
    SUM(CASE WHEN cc.customer_sk IS NOT NULL THEN 1 ELSE 0 END) AS converting_n,
    ROUND(100.0 * SUM(CASE WHEN cc.customer_sk IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 4) AS conversion_rate_pct
INTO #M1_Conversion
FROM expt.experiment_population ep
LEFT JOIN #ConvertedCustomers cc ON cc.customer_sk = ep.customer_sk
WHERE ep.is_eligible = 1
GROUP BY ep.variant;

-- ------------------------------------------------------------
-- Metric 2: Recommendation CTR (ISOLATED — ep joined only to
-- Fact_Recommendation_Events, no other table in this query)
-- ------------------------------------------------------------

IF OBJECT_ID('tempdb..#M2_CTR') IS NOT NULL DROP TABLE #M2_CTR;
SELECT
    ep.variant,
    SUM(CASE WHEN fre.event_type = 'recommendation_impression' THEN 1 ELSE 0 END) AS impressions,
    SUM(CASE WHEN fre.event_type = 'recommendation_click' THEN 1 ELSE 0 END) AS clicks,
    ROUND(100.0 * SUM(CASE WHEN fre.event_type = 'recommendation_click' THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN fre.event_type = 'recommendation_impression' THEN 1 ELSE 0 END), 0), 4) AS ctr_pct
INTO #M2_CTR
FROM expt.experiment_population ep
JOIN dbo.Fact_Recommendation_Events fre ON fre.customer_sk = ep.customer_sk AND fre.experiment_sk = @Exp1Sk
WHERE ep.is_eligible = 1
GROUP BY ep.variant;

-- ------------------------------------------------------------
-- Metric 3: Purchase Rate (ISOLATED — same structure as Script
-- 04's already-fixed version: COUNT(DISTINCT ep.customer_sk),
-- not COUNT(*), for the denominator)
-- ------------------------------------------------------------

IF OBJECT_ID('tempdb..#M3_PurchaseRate') IS NOT NULL DROP TABLE #M3_PurchaseRate;
SELECT
    ep.variant,
    COUNT(DISTINCT ep.customer_sk) AS eligible_n,
    SUM(CASE WHEN fre.event_type = 'recommendation_conversion' THEN 1 ELSE 0 END) AS total_conversion_events,
    ROUND(1.0 * SUM(CASE WHEN fre.event_type = 'recommendation_conversion' THEN 1 ELSE 0 END) / COUNT(DISTINCT ep.customer_sk), 4) AS purchase_rate
INTO #M3_PurchaseRate
FROM expt.experiment_population ep
LEFT JOIN dbo.Fact_Recommendation_Events fre ON fre.customer_sk = ep.customer_sk AND fre.experiment_sk = @Exp1Sk
WHERE ep.is_eligible = 1
GROUP BY ep.variant;

-- ------------------------------------------------------------
-- Metric 4: AOV / Revenue per User proxy (ISOLATED — mirrors
-- Script 04's correct LEFT JOIN structure: the FULL eligible
-- population stays in the FROM clause; the conversion-only
-- filter lives inside a separately-joined subquery, so it can
-- never restrict the population used for the denominator)
-- ------------------------------------------------------------

IF OBJECT_ID('tempdb..#M4_Revenue') IS NOT NULL DROP TABLE #M4_Revenue;
;WITH ConversionProxyValue AS (
    SELECT ep.variant, ep.customer_sk, pap.avg_price AS proxy_value
    FROM expt.experiment_population ep
    JOIN dbo.Fact_Recommendation_Events fre ON fre.customer_sk = ep.customer_sk AND fre.experiment_sk = @Exp1Sk
    JOIN #ProductAvgPrice pap ON pap.product_sk = fre.product_sk
    WHERE ep.is_eligible = 1 AND fre.event_type = 'recommendation_conversion'
)
SELECT
    ep.variant,
    COUNT(DISTINCT ep.customer_sk) AS eligible_n,
    ROUND(AVG(cpv.proxy_value), 2) AS aov_proxy,
    ROUND(SUM(ISNULL(cpv.proxy_value, 0)) / COUNT(DISTINCT ep.customer_sk), 2) AS revenue_per_user_proxy
INTO #M4_Revenue
FROM expt.experiment_population ep
LEFT JOIN ConversionProxyValue cpv ON cpv.customer_sk = ep.customer_sk AND cpv.variant = ep.variant
WHERE ep.is_eligible = 1
GROUP BY ep.variant;

-- ------------------------------------------------------------
-- Combine the 4 already-isolated, already-correct results
-- ------------------------------------------------------------

SELECT
    m1.variant, m1.eligible_n, m1.conversion_rate_pct,
    m2.ctr_pct, m4.aov_proxy, m4.revenue_per_user_proxy, m3.purchase_rate
FROM #M1_Conversion m1
JOIN #M2_CTR m2 ON m2.variant = m1.variant
JOIN #M3_PurchaseRate m3 ON m3.variant = m1.variant
JOIN #M4_Revenue m4 ON m4.variant = m1.variant
ORDER BY m1.variant;

-- ------------------------------------------------------------
-- Executive metric table (Control vs Treatment vs Effect)
-- ------------------------------------------------------------

SELECT
    'Purchase Conversion Rate' AS metric,
    MAX(CASE WHEN variant='control' THEN conversion_rate_pct END) AS control_value,
    MAX(CASE WHEN variant='treatment' THEN conversion_rate_pct END) AS treatment_value,
    ROUND(MAX(CASE WHEN variant='treatment' THEN conversion_rate_pct END) - MAX(CASE WHEN variant='control' THEN conversion_rate_pct END), 4) AS effect,
    'NOT SIGNIFICANT (p=0.8126)' AS significance,
    'PRIMARY' AS decision_relevance
FROM #M1_Conversion

UNION ALL

SELECT 'Recommendation CTR',
    MAX(CASE WHEN variant='control' THEN ctr_pct END), MAX(CASE WHEN variant='treatment' THEN ctr_pct END),
    ROUND(MAX(CASE WHEN variant='treatment' THEN ctr_pct END) - MAX(CASE WHEN variant='control' THEN ctr_pct END), 4),
    'Supporting', 'SECONDARY'
FROM #M2_CTR

UNION ALL

SELECT 'AOV (proxy — catalog price, not real revenue)',
    MAX(CASE WHEN variant='control' THEN aov_proxy END), MAX(CASE WHEN variant='treatment' THEN aov_proxy END),
    ROUND(MAX(CASE WHEN variant='treatment' THEN aov_proxy END) - MAX(CASE WHEN variant='control' THEN aov_proxy END), 2),
    'Supporting — CAUTION: small sample (~46/variant), likely noise, see Script 04 note', 'SECONDARY'
FROM #M4_Revenue

UNION ALL

SELECT 'Revenue per User (proxy)',
    MAX(CASE WHEN variant='control' THEN revenue_per_user_proxy END), MAX(CASE WHEN variant='treatment' THEN revenue_per_user_proxy END),
    ROUND(MAX(CASE WHEN variant='treatment' THEN revenue_per_user_proxy END) - MAX(CASE WHEN variant='control' THEN revenue_per_user_proxy END), 2),
    'Supporting — same small-sample caution as AOV proxy above', 'SECONDARY'
FROM #M4_Revenue

UNION ALL

SELECT 'Purchase Rate (events per customer)',
    MAX(CASE WHEN variant='control' THEN purchase_rate END), MAX(CASE WHEN variant='treatment' THEN purchase_rate END),
    ROUND(MAX(CASE WHEN variant='treatment' THEN purchase_rate END) - MAX(CASE WHEN variant='control' THEN purchase_rate END), 4),
    'Supporting', 'SECONDARY'
FROM #M3_PurchaseRate;

-- ------------------------------------------------------------
-- Statistical summary block (references Script 05's z-test
-- output directly — rerun Script 05 to re-verify these figures)
-- ------------------------------------------------------------

SELECT
    'PASS' AS srm_status,
    (SELECT eligible_n FROM #M1_Conversion WHERE variant = 'control') AS control_size,
    (SELECT eligible_n FROM #M1_Conversion WHERE variant = 'treatment') AS treatment_size,
    'Purchase Conversion Rate' AS primary_metric,
    '-0.1026 pp' AS absolute_effect,
    '-4.75%' AS relative_lift,
    '0.8126' AS p_value,
    '[-0.9504 pp, 0.7452 pp]' AS confidence_interval_95,
    'Small, not statistically distinguishable from zero' AS effect_size;

DROP TABLE #M1_Conversion;
DROP TABLE #M2_CTR;
DROP TABLE #M3_PurchaseRate;
DROP TABLE #M4_Revenue;
DROP TABLE #ConvertedCustomers;
DROP TABLE #ProductAvgPrice;

/*
    BUSINESS INTERPRETATION — fill in after running:
    - Confirm the first result set now exactly matches Script 04's
      confirmed numbers (2.1592%/2.0567% conversion, not 10%+).

    BUSINESS IMPLICATION:
    This readout is the direct input to Script 07's SHIP / DO NOT
    SHIP / CONTINUE TESTING decision.
*/
