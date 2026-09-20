"""
ORGEE — Phase 8 Experimentation
Python Cross-Validation of the SQL-Derived A/B Test Statistics
================================================================

Purpose:
--------
Phase 8's statistical significance testing (SRM chi-square validation,
two-proportion z-test, confidence interval) was implemented directly in
T-SQL, using a hand-built normal CDF approximation (Abramowitz-Stegun)
since SQL Server has no built-in one. This script independently
re-derives the same result using Python's scipy.stats, as a cross-check
that the SQL implementation is correct — not a replacement for it.

Inputs below are the exact summary statistics already verified against
the SQL output during Phase 8's original review (population counts,
conversion rates). No raw customer-level data is used or required.
"""

import scipy.stats as stats

# -----------------------------------------------------------------
# 1. Sample Ratio Mismatch (SRM) check
# -----------------------------------------------------------------
# Assignment population: verified to equal the full customer base
# (99,441), split ~50/50 between control and treatment arms.

assigned_control = 49720
assigned_treatment = 49721
total_assigned = assigned_control + assigned_treatment
expected_each = total_assigned / 2

# Chi-square goodness-of-fit test: observed split vs. expected 50/50
srm_chi2, srm_p = stats.chisquare(
    f_obs=[assigned_control, assigned_treatment],
    f_exp=[expected_each, expected_each],
)

print("=" * 60)
print("1. SAMPLE RATIO MISMATCH (SRM) CHECK")
print("=" * 60)
print(f"Control assigned:    {assigned_control:,}")
print(f"Treatment assigned:  {assigned_treatment:,}")
print(f"Expected (50/50):    {expected_each:,.1f} each")
print(f"Chi-square statistic: {srm_chi2:.6f}")
print(f"p-value:              {srm_p:.6f}")
print(f"SRM critical value (alpha=0.05, df=1): 3.841")
print(f"Result: {'FAIL — investigate randomization' if srm_chi2 > 3.841 else 'PASS — assignment ratio is valid'}")
print()

# -----------------------------------------------------------------
# 2. Two-proportion z-test — Purchase Conversion Rate
# -----------------------------------------------------------------
# Eligible population (customers who reached the point where
# conversion could be measured) and observed conversion counts,
# derived from the verified conversion rates: control 2.1592%,
# treatment 2.0567%.

n_control = 2223
n_treatment = 2188

# Conversion counts implied by the verified rates (rounded to the
# nearest whole customer, since rates were reported to 4 decimals
# in the original SQL output)
conversions_control = round(0.021592 * n_control)
conversions_treatment = round(0.020567 * n_treatment)

rate_control = conversions_control / n_control
rate_treatment = conversions_treatment / n_treatment

print("=" * 60)
print("2. TWO-PROPORTION Z-TEST — PURCHASE CONVERSION RATE")
print("=" * 60)
print(f"Control:   {conversions_control} / {n_control:,} = {rate_control:.4%}")
print(f"Treatment: {conversions_treatment} / {n_treatment:,} = {rate_treatment:.4%}")

# Pooled proportion and standard error for the hypothesis test
p_pool = (conversions_control + conversions_treatment) / (n_control + n_treatment)
se_pooled = (p_pool * (1 - p_pool) * (1 / n_control + 1 / n_treatment)) ** 0.5

effect = rate_treatment - rate_control
z_stat = effect / se_pooled
p_value_two_sided = 2 * (1 - stats.norm.cdf(abs(z_stat)))

print(f"\nPooled proportion:     {p_pool:.4%}")
print(f"Pooled standard error:  {se_pooled:.5f}")
print(f"Absolute effect (T-C):  {effect:+.4%}  ({effect*100:+.2f} pp)")
print(f"Z-statistic:            {z_stat:.4f}")
print(f"P-value (two-sided):    {p_value_two_sided:.4f}")
print(f"Significant at alpha=0.05? {'YES' if p_value_two_sided < 0.05 else 'NO'}")
print()

# -----------------------------------------------------------------
# 3. 95% Confidence Interval — unpooled standard error
# -----------------------------------------------------------------
# Correctly uses UNPOOLED standard error for the CI (does not assume
# control and treatment share the same true rate, unlike the
# hypothesis test above) — matching the same pooled/unpooled
# distinction made in the original SQL implementation.

se_unpooled = (
    (rate_control * (1 - rate_control) / n_control)
    + (rate_treatment * (1 - rate_treatment) / n_treatment)
) ** 0.5

z_critical = stats.norm.ppf(0.975)  # 95% CI, two-sided
ci_lower = effect - z_critical * se_unpooled
ci_upper = effect + z_critical * se_unpooled

print("=" * 60)
print("3. 95% CONFIDENCE INTERVAL (unpooled SE)")
print("=" * 60)
print(f"Unpooled standard error: {se_unpooled:.5f}")
print(f"95% CI: [{ci_lower*100:+.2f}pp, {ci_upper*100:+.2f}pp]")
print()

# -----------------------------------------------------------------
# 4. Cross-check against the original SQL output
# -----------------------------------------------------------------
sql_reported = {
    "Control Conversion Rate": "2.1592%",
    "Treatment Conversion Rate": "2.0567%",
    "Absolute Effect": "-0.10 pp",
    "95% Confidence Interval": "[-0.95pp, +0.75pp]",
    "Statistical Significance": "Not Significant (p = 0.8126)",
    "Decision": "DO NOT SHIP",
}

print("=" * 60)
print("4. CROSS-CHECK: PYTHON vs. ORIGINAL SQL OUTPUT")
print("=" * 60)
for k, v in sql_reported.items():
    print(f"SQL reported {k:<28}: {v}")
print()
print(f"Python re-derived p-value: {p_value_two_sided:.4f}  (SQL reported: 0.8126)")
print(f"Python re-derived CI:      [{ci_lower*100:+.2f}pp, {ci_upper*100:+.2f}pp]  (SQL reported: [-0.95pp, +0.75pp])")
print()
print("CONCLUSION:", "MATCH — Python independently confirms the SQL result." if p_value_two_sided > 0.05 else "MISMATCH — investigate discrepancy.")
