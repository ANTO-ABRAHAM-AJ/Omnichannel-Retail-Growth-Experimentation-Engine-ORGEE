/*
    ============================================================
    ORGEE — Phase 7: Recommendation Intelligence
    06_recommendation_business_impact.sql
    ============================================================

    BUSINESS QUESTION
    Given what the engine actually demonstrated (not what we hoped
    it would), what is the honest business opportunity — and what
    is explicitly NOT being claimed at this stage?

    WHAT WE ARE NOT CLAIMING (per the plan's own rule): no causal
    uplift from this engine. Script 05 measured correlation with
    historical holdout purchases, not a controlled experiment.
    Actual causal validation belongs to Phase 8.

    WHAT WE ARE NOT CLAIMING, PART 2: that this engine is ready to
    predict a customer's next purchase weeks or months out. Script
    05 showed it does not (0.07% Hit Rate@5 vs a 1.07% popularity
    baseline). That specific claim is not supported by the evidence
    and will not be made here.

    WHAT THE EVIDENCE DOES SUPPORT: the engine produces coherent,
    interpretable, same-category recommendations (Script 04 — every
    example recommendation matched the customer's actual top
    preference category, with a tight, sensible similarity
    distribution). That is a real, demonstrated capability — just
    not the same claim as "predicts future purchases."

    TECHNIQUES USED
    Aggregation, structured business-impact table.
    ============================================================
*/

-- ------------------------------------------------------------
-- What the engine demonstrably does well: same-category
-- coherence (a real, positive, measured capability)
-- ------------------------------------------------------------

SELECT
    COUNT(*) AS total_recommendations,
    COUNT(DISTINCT customer_unique_id) AS customers_served,
    ROUND(AVG(CAST(similarity_score AS FLOAT)), 4) AS avg_similarity_score,
    ROUND(MIN(CAST(similarity_score AS FLOAT)), 4) AS min_similarity_score
FROM reco.recommendations;

-- ------------------------------------------------------------
-- Scale of the underlying opportunity this engine touches — the
-- product-view-to-cart gap (Phase 5/6) is the same population this
-- engine is generating candidates for
-- ------------------------------------------------------------

SELECT
    (SELECT COUNT(*) FROM reco.recommendations) AS total_recommendations_generated,
    (SELECT COUNT(DISTINCT customer_unique_id) FROM reco.recommendations) AS customers_with_recommendations,
    (SELECT COUNT(DISTINCT customer_unique_id) FROM dbo.Dim_Customer) AS total_customer_base;

-- ------------------------------------------------------------
-- Structured business impact table — honest framing throughout
-- ------------------------------------------------------------

SELECT * FROM (VALUES

    ('Recommendation Quality',
     'Content-based recommendations are internally coherent — every example inspected in Script 04 matched the customer''s actual top-preference category, with similarity scores in a tight, sensible 0.68-1.00 range (not scattered/arbitrary).'),

    ('Recommendation Quality — Limitation',
     'The same engine does NOT predict genuinely new future purchases better than simply recommending best-sellers (Script 05: 0.07% vs 1.07% Hit Rate@5, evaluated on the identical customer population, with leakage-free product features, confirmed reproducible). This is a real, measured limitation, not a caveat added after the fact.'),

    ('Coverage',
     '99.53% of customers with any interaction history (94,691 of 95,137) receive Top-5 recommendations — coverage itself is not the constraint.'),

    ('Most Defensible Use Case Given the Evidence',
     'Same-session or near-term "similar item" cross-sell / discovery (e.g. "customers who liked this also viewed...") — NOT a long-horizon "we know what you''ll buy next month" personalization claim, which the evaluation does not support.'),

    ('What Would Be Needed to Improve It',
     'Collaborative signal (what similar CUSTOMERS purchase, not just similar PRODUCT attributes) is the most likely missing ingredient, given a wider candidate pool made results worse, not better — ruling out coverage as the bottleneck. This is explicitly out of scope for the current locked, single-content-based-engine design (see Phase 7 plan section 15).'),

    ('Relationship to Phase 8',
     'Phase 8''s existing experimentation framework (built independently in Phase 2) is not literally testing this specific engine''s specific picks — that pipeline was never wired that way, and rewiring it now would be new architecture. Phase 8 remains valuable for demonstrating rigorous A/B testing methodology on its own terms.')

) AS BusinessImpact(topic, assessment);

/*
    BUSINESS INTERPRETATION:
    The honest headline is a split result: the engine is
    demonstrably COHERENT (recommends genuinely similar products,
    interpretable, high similarity scores) but NOT demonstrably
    PREDICTIVE of future purchases beyond what a naive popularity
    baseline already achieves. Both halves of that statement are
    supported by actual measurements from this phase, not asserted.

    BUSINESS IMPLICATION:
    Recommend deploying this engine, if at all, for a narrower,
    evidence-supported use case (same-session cross-sell) rather
    than the broader "personalized future recommendations" framing
    the original plan envisioned — a scope adjustment driven by
    what the leakage-safe evaluation actually showed, not a
    predetermined conclusion.
*/
