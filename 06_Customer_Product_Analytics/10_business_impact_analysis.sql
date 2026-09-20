/*
    ============================================================
    ORGEE — Phase 6: Customer & Product Analytics
    10_business_impact_analysis.sql ⭐
    ============================================================

    BUSINESS QUESTION
    For each major recommendation, what specifically is the finding,
    the business problem it points to, the recommended action, the
    target, the expected impact, and the metric to monitor —
    structured as Finding -> Problem -> Action -> Target ->
    Expected Impact -> Success Metric.

    All quantities below reference the actual results produced by
    01-09 in this phase and Phases 4-5 — nothing here is invented.

    TECHNIQUES USED
    Structured UNION ALL table, referencing prior validated numbers.
    ============================================================
*/

SELECT * FROM (VALUES

    (
        2,
        'Finding',
        'Product View -> Add to Cart is the single largest funnel drop-off at 62.76% (254,621 of 405,699 sessions), larger than checkout or purchase-stage loss (Phase 5).'
    ),
    (
        2,
        'Problem',
        'The majority of product-viewing traffic never expresses purchase intent via a cart action — a product-page / engagement problem, not a checkout problem.'
    ),
    (
        2,
        'Action',
        'Redesign product-page cart-add experience (prominence, pricing clarity, urgency signals, cross-sell); prioritize highest-view/no-cart products identified in 07_product_metrics.sql.'
    ),
    (
        2,
        'Target',
        'All product-viewing sessions, prioritized by the specific SKUs surfaced in 07_product_metrics.sql''s view-to-cart gap ranking.'
    ),
    (
        2,
        'Expected Business Impact',
        'Even a modest lift in the 37.24% Product View -> Add to Cart rate compounds through the rest of the funnel (54.10% and 58.01% conversion at later stages) toward the 9.48% overall Visit-to-Purchase rate.'
    ),
    (
        2,
        'Success Metric',
        'Product View -> Add to Cart stage conversion rate (currently 37.24%, Phase 5 04_funnel_analysis.sql).'
    ),

    (
        3,
        'Finding',
        'The top 10% of customers generate 41.14% of total revenue (Phase 4); separately, the At-Risk RFM segment holds historical value while showing declining recency (Phase 6 02/04).'
    ),
    (
        3,
        'Problem',
        'Revenue is concentrated in a small customer base, and part of that base is showing early signs of disengagement — a retention risk to a disproportionate share of revenue.'
    ),
    (
        3,
        'Action',
        'Targeted win-back/retention campaign for the At-Risk segment specifically (not a broad campaign) — see 04_rfm_clv_combined.sql for the exact segment size and revenue at stake.'
    ),
    (
        3,
        'Target',
        'Customers in the At-Risk RFM segment (f_score >= 3 and r_score <= 2), using the same RFM segmentation logic as 04_rfm_clv_combined.sql — exact count and revenue from that script.'
    ),
    (
        3,
        'Expected Business Impact',
        'Creates an opportunity to protect historically realized revenue from existing customers rather than relying solely on new-customer acquisition, particularly given the 97% one-time-buyer base (Phase 4).'
    ),
    (
        3,
        'Success Metric',
        'At-Risk segment repeat-purchase rate and revenue retention, tracked month over month.'
    ),

    (
        1,
        'Finding',
        'Sessions that search convert at 11.21% vs. 5.60% for sessions that do not search — roughly double (Phase 5).'
    ),
    (
        1,
        'Problem',
        'Search is a strong conversion signal but may be underused or hard to discover for a large share of sessions.'
    ),
    (
        1,
        'Action',
        'Increase search bar prominence / prompt search earlier in the session (e.g. on landing).'
    ),
    (
        1,
        'Target',
        'Non-searching sessions — the majority of session volume per Phase 5''s search-behavior breakdown.'
    ),
    (
        1,
        'Expected Business Impact',
        'Converting a share of non-searching sessions into searching behavior could lift overall conversion, given the ~2x observed gap.'
    ),
    (
        1,
        'Success Metric',
        'Search-session share of total sessions, and the search-vs-no-search conversion gap (should narrow if the intervention instead just adds low-intent searches, or the search-session share should simply grow if it works as intended).'
    )

) AS BusinessImpact(finding_id, field, detail)
ORDER BY finding_id, CASE field
    WHEN 'Finding' THEN 1 WHEN 'Problem' THEN 2 WHEN 'Action' THEN 3
    WHEN 'Target' THEN 4 WHEN 'Expected Business Impact' THEN 5 WHEN 'Success Metric' THEN 6
END;

/*
    NOTE: this structure intentionally does not re-derive numbers —
    every figure cited traces back to a specific script (Phase 4,
    5, or 6) already run and validated. If 08_feature_prioritization.sql's
    actual priority_rank differs from the 1-2-3 ordering used here,
    reorder these findings to match before finalizing for
    documentation.
*/
