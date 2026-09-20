# Phase 8 — Python Cross-Validation Results
## ORGEE — Omnichannel Retail & Growth Experimentation Engine

**Purpose:** Independently re-derive Phase 8's SQL-based A/B test statistics using Python's `scipy.stats`, as a cross-check of the T-SQL implementation — not a replacement for it. See the top-level README for why the original statistics were implemented in SQL rather than Python.

**Script:** `phase8_python_validation.py`

---

## Result: Exact Match

| Metric | SQL (Phase 8) | Python (`scipy.stats`) | Match? |
|---|---|---|---|
| Control Conversion Rate | 2.1592% | 2.1592% | ✅ |
| Treatment Conversion Rate | 2.0567% | 2.0567% | ✅ |
| Absolute Effect | -0.10 pp | -0.1026 pp | ✅ |
| P-value | 0.8126 | 0.8126 | ✅ Exact |
| 95% Confidence Interval | [-0.95pp, +0.75pp] | [-0.95pp, +0.75pp] | ✅ Exact |
| SRM Check | PASS | PASS (χ² = 0.00001, p = 0.997) | ✅ |
| Decision | DO NOT SHIP | DO NOT SHIP (confirmed) | ✅ |

Every figure matches to the reported precision. This confirms that the T-SQL implementation of the normal CDF (via the Abramowitz-Stegun polynomial approximation, used because SQL Server has no built-in normal CDF function) produced a statistically correct result — the hand-built approximation was not a source of error.

## What This Validates

- The **pooled standard error** used for the hypothesis test (assumes control and treatment share a true underlying rate under the null) was correctly implemented in SQL.
- The **unpooled standard error** used for the confidence interval (does not assume equal true rates) was correctly and separately implemented — the same pooled/unpooled distinction is reproduced explicitly in the Python script.
- The **SRM chi-square check** independently confirms the 49,720 / 49,721 assignment split is not different from a true 50/50 randomization (χ² = 0.00001, far below the 3.841 critical value).

## Conclusion

The Phase 8 A/B test's **DO NOT SHIP** decision is now confirmed by two independent statistical implementations, in two different languages, using two different normal-distribution calculation methods (SQL's hand-built polynomial approximation vs. Python's `scipy.stats.norm`). This is a stronger form of validation than re-running the same calculation twice in the same tool would provide.
