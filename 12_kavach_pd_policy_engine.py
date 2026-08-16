import pandas as pd
import numpy as np

print("=" * 70)
print("KAVACH PULSE — RISK + POLICY ENGINE v2")
print("=" * 70)


# =========================================================
# 1. LOAD BEHAVIORAL FEATURES
# =========================================================

df = pd.read_csv(
    "kavach_behavioral_features.csv"
)

print(
    "\nApplicants:",
    len(df)
)


# =========================================================
# 2. HELPER
# =========================================================

def percentile_score(series):

    return series.rank(
        pct=True
    )


# =========================================================
# 3. BEHAVIORAL COMPONENTS
# =========================================================

# Lower volatility = better

income_stability = (
    1 -
    percentile_score(
        df["income_cv"]
    )
)

cashflow_stability = (
    1 -
    percentile_score(
        df["cashflow_cv"]
    )
)


# Higher payment consistency = better

payment_strength = (
    df["payment_success_rate"]
)


# Higher minimum balance = better

balance_strength = (
    percentile_score(
        df["balance_min"]
    )
)


# Higher inflow/outflow coverage = better

coverage_strength = (
    percentile_score(
        df["inflow_to_outflow_ratio"]
    )
)


# Better income trend = better

trend_strength = (
    percentile_score(
        df["income_trend"]
    )
)


# =========================================================
# 4. BEHAVIORAL STABILITY SCORE
# =========================================================

df["behavioral_stability_score"] = (

    0.25 * income_stability

    + 0.20 * cashflow_stability

    + 0.20 * payment_strength

    + 0.15 * balance_strength

    + 0.10 * coverage_strength

    + 0.10 * trend_strength

) * 100


# =========================================================
# 5. EVIDENCE QUALITY
# =========================================================

history_score = np.clip(
    df["history_months"] / 12,
    0,
    1
)

payment_score = (
    df["payment_success_rate"]
)

stability_score = (
    income_stability
)

df["evidence_quality_score"] = (

    (
        0.40 * history_score
        +
        0.30 * payment_score
        +
        0.30 * stability_score
    )
    * 100
)


# =========================================================
# 6. CONFIDENCE BAND
# =========================================================

def confidence_band(score):

    if score >= 80:
        return "HIGH"

    elif score >= 60:
        return "MEDIUM"

    else:
        return "LOW"


df["confidence_band"] = (
    df["evidence_quality_score"]
    .apply(confidence_band)
)


# =========================================================
# 7. ILLUSTRATIVE PD PROXY
# =========================================================
#
# IMPORTANT:
#
# This is NOT a calibrated probability of default.
#
# We have no real Kavach repayment outcomes.
#
# It is only a prototype mapping from behavioral
# stability to an illustrative risk estimate.
#
# =========================================================

print(
    "\nCreating illustrative PD proxy..."
)

stability = (
    df["behavioral_stability_score"]
    / 100
)


# Map stability approximately:
#
# 0.00 → 25%
# 1.00 → 2%
#
# Higher stability = lower risk.

df["pd_proxy"] = (
    0.25
    -
    0.23 * stability
)


df["pd_proxy"] = np.clip(
    df["pd_proxy"],
    0.02,
    0.25
)


# =========================================================
# 8. RISK BANDS
# =========================================================

def risk_band(pd):

    if pd < 0.05:
        return "LOW"

    elif pd < 0.10:
        return "MODERATE"

    elif pd < 0.20:
        return "ELEVATED"

    else:
        return "HIGH"


df["risk_band"] = (
    df["pd_proxy"]
    .apply(risk_band)
)


# =========================================================
# 9. POLICY ENGINE
# =========================================================
#
# Demonstration routing only.
#
# These thresholds are NOT regulatory thresholds
# and are NOT lender-approved credit policy.
#
# =========================================================

def policy_decision(row):

    pd = row[
        "pd_proxy"
    ]

    confidence = row[
        "confidence_band"
    ]

    evidence = row[
        "evidence_quality_score"
    ]

    # -----------------------------------------------------
    # Insufficient evidence
    # -----------------------------------------------------

    if evidence < 60:

        return "INSUFFICIENT_EVIDENCE"

    # -----------------------------------------------------
    # High risk
    # -----------------------------------------------------

    if pd >= 0.20:

        return "DECLINE_OR_REVIEW"

    # -----------------------------------------------------
    # Elevated risk
    # -----------------------------------------------------

    if pd >= 0.10:

        return "MANUAL_REVIEW"

    # -----------------------------------------------------
    # Weak evidence
    # -----------------------------------------------------

    if confidence == "LOW":

        return "MANUAL_REVIEW"

    # -----------------------------------------------------
    # Medium evidence
    # -----------------------------------------------------

    if confidence == "MEDIUM":

        return "POLICY_REVIEW"

    # -----------------------------------------------------
    # Strong evidence + lower illustrative risk
    # -----------------------------------------------------

    return "PASS_TO_LENDER_POLICY"


df["policy_decision"] = (
    df.apply(
        policy_decision,
        axis=1
    )
)


# =========================================================
# 10. SUMMARY
# =========================================================

print(
    "\nBehavioral stability:"
)

print(
    df[
        "behavioral_stability_score"
    ]
    .describe()
    .round(2)
)


print(
    "\nIllustrative PD proxy:"
)

print(
    df[
        "pd_proxy"
    ]
    .describe()
    .round(4)
)


print(
    "\nRisk bands:"
)

print(
    df[
        "risk_band"
    ]
    .value_counts()
)


print(
    "\nConfidence bands:"
)

print(
    df[
        "confidence_band"
    ]
    .value_counts()
)


print(
    "\nPolicy decisions:"
)

print(
    df[
        "policy_decision"
    ]
    .value_counts()
)


# =========================================================
# 11. EXAMPLE ASSESSMENTS
# =========================================================

print(
    "\nExample Kavach assessments:"
)

columns = [

    "applicant_id",

    "behavioral_stability_score",

    "pd_proxy",

    "risk_band",

    "evidence_quality_score",

    "confidence_band",

    "policy_decision"
]

print(
    df[
        columns
    ]
    .head(20)
    .round(3)
    .to_string(
        index=False
    )
)


# =========================================================
# 12. SAVE
# =========================================================

df.to_csv(
    "kavach_pd_policy_output.csv",
    index=False
)

print(
    "\nSaved:"
)

print(
    "  kavach_pd_policy_output.csv"
)


# =========================================================
# 13. METHODOLOGY NOTICE
# =========================================================

print("\n")
print("=" * 70)

print(
    "IMPORTANT METHODOLOGY NOTE"
)

print("=" * 70)

print(
    """
The pd_proxy column is an ILLUSTRATIVE RISK PROXY.

It is NOT a calibrated probability of default.

The thresholds and mapping used here are prototype
demonstration assumptions.

They are NOT regulatory thresholds and must not be
represented as validated lender policy.

A production Kavach PD model requires:

1. Real behavioral histories
2. Observed repayment outcomes
3. Out-of-time validation
4. Probability calibration
5. Population stability monitoring
6. Fairness testing
7. Appropriate lender policy and regulatory review
"""
)

print("=" * 70)

print(
    "RISK + POLICY ENGINE v2 COMPLETE"
)

print("=" * 70)
