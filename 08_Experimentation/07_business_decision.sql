/*
    ============================================================
    ORGEE — Phase 8: Experimentation Framework
    07_business_decision.sql ⭐ SIGNATURE SCRIPT
    ============================================================

    BUSINESS QUESTION
    Given everything established in Scripts 01-06, what is the
    one defensible decision: SHIP, DO NOT SHIP, or CONTINUE TESTING?

    THE EVIDENCE, ASSEMBLED:
        SRM               PASS (chi-sq 0.00001, well below all
                          three standard critical thresholds)
        Primary metric    Treatment 2.06% vs Control 2.16% — a
                          SMALL, NEGATIVE point estimate (Treatment
                          slightly worse, not better)
        Statistical test  NOT SIGNIFICANT (p=0.8126, z=-0.24)
        95% CI            [-0.95pp, +0.75pp] — spans zero, but is
                          CENTERED close to zero on the negative
                          side, not skewed toward a promising
                          positive direction
        Secondary metrics CTR and Purchase Rate both near-identical
                          between variants; AOV/Revenue-per-user
                          proxies show a large apparent gap but are
                          explicitly flagged as likely small-sample
                          noise (~46 conversions/variant), not a
                          real signal, and do not override the
                          primary metric regardless

    WHY "DO NOT SHIP" RATHER THAN "CONTINUE TESTING":
    The plan's own distinction is: CONTINUE TESTING is for a result
    that is inconclusive with a DIRECTION POTENTIALLY POSITIVE, but
    too much uncertainty to call it yet. That is NOT what happened
    here. The point estimate itself is negative (Treatment
    performed slightly worse), not positive-but-uncertain. With
    4,411 total eligible customers and a precisely-estimated null
    result (z close to 0, not a wide, ambiguous interval driven by
    a tiny sample), this is a reasonably informative test that
    shows no evidence of improvement — not an underpowered test
    that merely needs more data to reveal a hidden positive effect.
    "DO NOT SHIP" is the plan's own definition for exactly this
    case: "the treatment does not demonstrate sufficient evidence
    of improvement, or produces an unfavorable result."

    NO ARTIFICIAL LINKAGE TO PHASE 7: this decision is about
    exp_001's synthetic experiment data only. It says nothing about
    whether Phase 7's actual content-based recommendation engine
    would perform well or poorly in a real deployment — that
    pipeline was never connected to this experiment's data, a
    distinction maintained consistently since Phase 7 itself.

    TECHNIQUES USED
    Structured decision table, VALUES-based summary.
    ============================================================
*/

SELECT * FROM (VALUES

    ('SRM Check', 'PASS — chi-square 0.00001, comfortably below all three standard critical thresholds (3.841/6.635/10.828). The allocation mechanism itself is trustworthy.'),

    ('Primary Metric Result', 'Treatment Purchase Conversion Rate (2.0567%) is NOT statistically distinguishable from Control (2.1592%) — absolute effect -0.10 percentage points, relative lift -4.75%, p=0.8126.'),

    ('Statistical Credibility', 'The 95% confidence interval [-0.95pp, +0.75pp] spans zero and is centered on the negative side, not a promising-but-uncertain positive direction. This is a precisely-estimated null result, not an underpowered/ambiguous one.'),

    ('Secondary Metrics', 'CTR (12.17% vs 12.55%) and Purchase Rate (0.0216 vs 0.0210) are both near-identical between variants, consistent with the primary metric. AOV/Revenue-per-user proxies show a large apparent gap but are explicitly flagged as likely small-sample noise (~46 conversions/variant) and do not override the primary metric.'),

    ('Business Interpretation', 'Personalized content-based recommendations did not improve purchase conversion relative to a top-sellers control experience, in this experiment. The result is a real, honest null finding — consistent with the design expectation set in Script 01 (the underlying synthetic data applied identical click/conversion probabilities to both variants, so no true effect was ever built in).'),

    ('Final Decision', 'DO NOT SHIP — the evidence does not support rolling out personalized recommendations over the top-sellers control, based on this experiment (exp_001).'),

    ('Scope Boundary', 'This decision concerns exp_001''s synthetic experiment data only. It is not a verdict on Phase 7''s actual recommendation engine, which was never connected to this experiment''s outcome data — a distinction maintained since Phase 7 to protect this project''s credibility.')

) AS BusinessDecision(topic, assessment);

/*
    SIGNATURE INSIGHT:
    Personalized recommendations changed Purchase Conversion Rate
    by -0.10 percentage points (-4.75% relative lift), with a 95%
    confidence interval of [-0.95pp, +0.75pp], leading to a
    DO NOT SHIP decision.
*/
