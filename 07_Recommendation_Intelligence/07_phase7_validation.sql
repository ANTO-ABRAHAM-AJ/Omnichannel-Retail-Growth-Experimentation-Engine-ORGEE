/*
    ============================================================
    ORGEE — Phase 7: Recommendation Intelligence
    07_phase7_validation.sql
    ============================================================
    Validates data quality, recommendation logic, coverage, and
    evaluation validity across Scripts 01-06. Every check writes a
    PASS/FAIL/INFO row; ends with a summary — matches the Phase
    2-6 validation pattern.
    ============================================================
*/

IF OBJECT_ID('tempdb..#P7Results') IS NOT NULL DROP TABLE #P7Results;
CREATE TABLE #P7Results (check_area VARCHAR(30), check_name VARCHAR(150), status VARCHAR(4), detail VARCHAR(300));

-- ============================================================
-- 1. DATA QUALITY
-- ============================================================

INSERT INTO #P7Results
SELECT 'Data Quality', 'Every reco.interactions.customer_unique_id exists in Dim_Customer',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END, CONCAT('invalid=', COUNT(*))
FROM reco.interactions i
WHERE NOT EXISTS (SELECT 1 FROM dbo.Dim_Customer dc WHERE dc.customer_unique_id = i.customer_unique_id);

INSERT INTO #P7Results
SELECT 'Data Quality', 'Every reco.interactions.product_sk exists in Dim_Product',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END, CONCAT('invalid=', COUNT(*))
FROM reco.interactions i
WHERE NOT EXISTS (SELECT 1 FROM dbo.Dim_Product dp WHERE dp.product_sk = i.product_sk);

INSERT INTO #P7Results
SELECT 'Data Quality', 'Every reco.product_features.product_sk exists in Dim_Product',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END, CONCAT('invalid=', COUNT(*))
FROM reco.product_features pf
WHERE NOT EXISTS (SELECT 1 FROM dbo.Dim_Product dp WHERE dp.product_sk = pf.product_sk);

INSERT INTO #P7Results
SELECT 'Data Quality', 'No NULL feature_value in reco.product_features',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END, CONCAT('nulls=', COUNT(*))
FROM reco.product_features WHERE feature_value IS NULL;

INSERT INTO #P7Results
SELECT 'Data Quality', 'Category feature values are always exactly 1.0',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END, CONCAT('violations=', COUNT(*))
FROM reco.product_features WHERE feature_name LIKE 'cat_%' AND feature_value <> 1.0;

INSERT INTO #P7Results
SELECT 'Data Quality', 'Normalized numeric features are within [0,1]',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END, CONCAT('violations=', COUNT(*))
FROM reco.product_features
WHERE feature_name IN ('price_norm', 'weight_norm', 'volume_norm', 'photos_norm')
  AND (feature_value < 0 OR feature_value > 1);

-- ============================================================
-- 2. RECOMMENDATION LOGIC
-- ============================================================

INSERT INTO #P7Results
SELECT 'Recommendation Logic', 'Every recommended_product_id exists in Dim_Product',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END, CONCAT('invalid=', COUNT(*))
FROM reco.recommendations r
WHERE NOT EXISTS (SELECT 1 FROM dbo.Dim_Product dp WHERE dp.product_id = r.recommended_product_id);

INSERT INTO #P7Results
SELECT 'Recommendation Logic', 'recommendation_rank is always between 1 and 5 (Top-N respected)',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END, CONCAT('violations=', COUNT(*))
FROM reco.recommendations WHERE recommendation_rank NOT BETWEEN 1 AND 5;

INSERT INTO #P7Results
SELECT 'Recommendation Logic', 'No customer has more than 5 recommendations',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END, CONCAT('violations=', COUNT(*))
FROM (
    SELECT customer_unique_id FROM reco.recommendations
    GROUP BY customer_unique_id HAVING COUNT(*) > 5
) x;

INSERT INTO #P7Results
SELECT 'Recommendation Logic', 'No duplicate (customer, product) recommendation pairs',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END, CONCAT('duplicates=', COUNT(*))
FROM (
    SELECT customer_unique_id, recommended_product_id FROM reco.recommendations
    GROUP BY customer_unique_id, recommended_product_id HAVING COUNT(*) > 1
) x;

INSERT INTO #P7Results
SELECT 'Recommendation Logic', 'No duplicate recommendation_rank within a customer',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END, CONCAT('violations=', COUNT(*))
FROM (
    SELECT customer_unique_id, recommendation_rank FROM reco.recommendations
    GROUP BY customer_unique_id, recommendation_rank HAVING COUNT(*) > 1
) x;

INSERT INTO #P7Results
SELECT 'Recommendation Logic', 'similarity_score is within valid cosine bounds [0,1] (all features non-negative)',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END, CONCAT('violations=', COUNT(*))
FROM reco.recommendations WHERE similarity_score < 0 OR similarity_score > 1;

INSERT INTO #P7Results
SELECT 'Recommendation Logic', 'Excluded (already-purchased) products never appear in that customer''s recommendations',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END, CONCAT('violations=', COUNT(*))
FROM reco.recommendations r
JOIN dbo.Dim_Product dp ON dp.product_id = r.recommended_product_id
WHERE EXISTS (
    SELECT 1 FROM reco.interactions i
    WHERE i.customer_unique_id = r.customer_unique_id
      AND i.product_sk = dp.product_sk
      AND i.interaction_type = 'purchase'
);

-- ============================================================
-- 3. COVERAGE
-- ============================================================

INSERT INTO #P7Results
SELECT 'Coverage', 'Recommendation coverage % of profiled customers',
       'INFO',
       CONCAT(
           'eligible=', (SELECT COUNT(DISTINCT customer_unique_id) FROM reco.customer_preferences),
           ', served=', (SELECT COUNT(DISTINCT customer_unique_id) FROM reco.recommendations),
           ', coverage_pct=', ROUND(
               100.0 * (SELECT COUNT(DISTINCT customer_unique_id) FROM reco.recommendations)
               / (SELECT COUNT(DISTINCT customer_unique_id) FROM reco.customer_preferences), 2
           )
       );

-- ============================================================
-- 4. EVALUATION VALIDITY (leakage-safety check)
-- ============================================================

INSERT INTO #P7Results
SELECT 'Evaluation Validity', 'No reco.eval_interactions row falls on/after the cutoff date (2018-05-01)',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END, CONCAT('violations=', COUNT(*))
FROM reco.eval_interactions WHERE interaction_date >= '2018-05-01';

INSERT INTO #P7Results
SELECT 'Evaluation Validity', 'eval_preferences customer count is <= eval_interactions customer count (no phantom profiles)',
       CASE WHEN (SELECT COUNT(DISTINCT customer_unique_id) FROM reco.eval_preferences)
                 <= (SELECT COUNT(DISTINCT customer_unique_id) FROM reco.eval_interactions)
            THEN 'PASS' ELSE 'FAIL' END,
       CONCAT('eval_preferences=', (SELECT COUNT(DISTINCT customer_unique_id) FROM reco.eval_preferences),
              ', eval_interactions=', (SELECT COUNT(DISTINCT customer_unique_id) FROM reco.eval_interactions));

INSERT INTO #P7Results
SELECT 'Evaluation Validity', 'eval_recommendations respects the same 5-per-customer Top-N limit',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END, CONCAT('violations=', COUNT(*))
FROM (
    SELECT customer_unique_id FROM reco.eval_recommendations
    GROUP BY customer_unique_id HAVING COUNT(*) > 5
) x;

INSERT INTO #P7Results
SELECT 'Evaluation Validity', 'Content-based engine Hit Rate@5 vs naive popularity baseline (informational — not a pass/fail)',
       'INFO', 'engine=0.07%, baseline=1.07%, engine underperforms baseline (see Script 05/06 for full context)';

-- ============================================================
-- SUMMARY
-- ============================================================

SELECT * FROM #P7Results ORDER BY check_area, check_name;

SELECT status, COUNT(*) AS check_count FROM #P7Results GROUP BY status;

IF EXISTS (SELECT 1 FROM #P7Results WHERE status = 'FAIL')
    PRINT '*** PHASE 7 VALIDATION: FAIL — see FAIL rows above ***';
ELSE
    PRINT '*** PHASE 7 VALIDATION: PASS ***';

DROP TABLE #P7Results;
