import pandas as pd
import numpy as np

print("=" * 70)
print("KAVACH PULSE — EXPLAINABILITY ENGINE")
print("=" * 70)


# =========================================================
# 1. LOAD KAVACH OUTPUT
# =========================================================

df = pd.read_csv(
    "kavach_pd_policy_output.csv"
)

print(
    "\nApplicants:",
    len(df)
)


# =========================================================
# 2. FEATURE REFERENCE VALUES
# =========================================================
#
# We compare each applicant against the population median.
#
# This is a prototype explanation method.
#
# It is NOT SHAP and should not be described as SHAP.
#
# =========================================================

reference = {

    "income_cv":
        df["income_cv"].median(),

    "cashflow_cv":
        df["cashflow_cv"].median(),

    "payment_success_rate":
        df["payment_success_rate"].median(),

    "balance_min":
        df["balance_min"].median(),

    "inflow_to_outflow_ratio":
        df["inflow_to_outflow_ratio"].median(),

    "income_trend":
        df["income_trend"].median()
}


# =========================================================
# 3. EXPLANATION FUNCTION
# =========================================================

def explain_applicant(row):

    positive = []
    risk = []
    limitations = []

    # -----------------------------------------------------
    # Income stability
    # -----------------------------------------------------

    if (
        row["income_cv"]
        <= reference["income_cv"] * 0.80
    ):

        positive.append(
            "Income volatility is relatively low"
        )

    elif (
        row["income_cv"]
        >= reference["income_cv"] * 1.20
    ):

        risk.append(
            "Income volatility is relatively high"
        )


    # -----------------------------------------------------
    # Cash-flow stability
    # -----------------------------------------------------

    if (
        row["cashflow_cv"]
        <= reference["cashflow_cv"] * 0.80
    ):

        positive.append(
            "Cash-flow variability is relatively low"
        )

    elif (
        row["cashflow_cv"]
        >= reference["cashflow_cv"] * 1.20
    ):

        risk.append(
            "Cash-flow variability is relatively high"
        )


    # -----------------------------------------------------
    # Payment consistency
    # -----------------------------------------------------

    if (
        row["payment_success_rate"]
        >= 0.95
    ):

        positive.append(
            "Strong payment consistency"
        )

    elif (
        row["payment_success_rate"]
        < 0.85
    ):

        risk.append(
            "Payment consistency is relatively weak"
        )


    # -----------------------------------------------------
    # Minimum balance
    # -----------------------------------------------------

    if (
        row["balance_min"]
        >= reference["balance_min"] * 1.20
    ):

        positive.append(
            "Strong minimum cash buffer"
        )

    elif (
        row["balance_min"]
        <= reference["balance_min"] * 0.80
    ):

        risk.append(
            "Low minimum cash buffer"
        )


    # -----------------------------------------------------
    # Cash-flow coverage
    # -----------------------------------------------------

    if (
        row["inflow_to_outflow_ratio"]
        >= 1.40
    ):

        positive.append(
            "Healthy inflow-to-outflow coverage"
        )

    elif (
        row["inflow_to_outflow_ratio"]
        < 1.15
    ):

        risk.append(
            "Limited inflow-to-outflow coverage"
        )


    # -----------------------------------------------------
    # Income trend
    # -----------------------------------------------------

    if (
        row["income_trend"]
        > reference["income_trend"] + 0.01
    ):

        positive.append(
            "Positive income trend"
        )

    elif (
        row["income_trend"]
        < reference["income_trend"] - 0.01
    ):

        risk.append(
            "Negative income trend"
        )


    # -----------------------------------------------------
    # History limitation
    # -----------------------------------------------------

    if (
        row["history_months"] < 6
    ):

        limitations.append(
            "Limited behavioral history"
        )

    elif (
        row["history_months"] < 12
    ):

        limitations.append(
            "Less than 12 months of behavioral history"
        )


    # -----------------------------------------------------
    # Evidence quality
    # -----------------------------------------------------

    if (
        row["evidence_quality_score"] < 60
    ):

        limitations.append(
            "Evidence quality is insufficient"
        )

    elif (
        row["evidence_quality_score"] < 80
    ):

        limitations.append(
            "Evidence quality is moderate"
        )


    # -----------------------------------------------------
    # Avoid empty explanation sections
    # -----------------------------------------------------

    if not positive:

        positive.append(
            "No major positive behavioral signal identified"
        )

    if not risk:

        risk.append(
            "No major adverse behavioral signal identified"
        )

    if not limitations:

        limitations.append(
            "No major evidence limitation identified"
        )


    return {

        "positive_factors":
            positive,

        "risk_factors":
            risk,

        "evidence_limitations":
            limitations
    }


# =========================================================
# 4. GENERATE EXPLANATIONS
# =========================================================

print(
    "\nGenerating applicant explanations..."
)

explanations = []

for _, row in df.iterrows():

    explanation = explain_applicant(
        row
    )

    explanations.append({

        "applicant_id":
            row["applicant_id"],

        "positive_factors":
            " | ".join(
                explanation[
                    "positive_factors"
                ]
            ),

        "risk_factors":
            " | ".join(
                explanation[
                    "risk_factors"
                ]
            ),

        "evidence_limitations":
            " | ".join(
                explanation[
                    "evidence_limitations"
                ]
            )
    })


explanation_df = pd.DataFrame(
    explanations
)


# =========================================================
# 5. MERGE
# =========================================================

output = df.merge(
    explanation_df,
    on="applicant_id",
    how="left"
)


# =========================================================
# 6. HUMAN-READABLE ASSESSMENT
# =========================================================

def create_assessment(row):

    return f"""
Risk proxy: {row['pd_proxy']:.1%}

Risk band: {row['risk_band']}

Evidence quality:
{row['evidence_quality_score']:.0f}/100

Confidence:
{row['confidence_band']}

Positive factors:
• {row['positive_factors'].replace(' | ', chr(10) + '• ')}

Risk factors:
• {row['risk_factors'].replace(' | ', chr(10) + '• ')}

Evidence limitations:
• {row['evidence_limitations'].replace(' | ', chr(10) + '• ')}

Policy routing:
{row['policy_decision']}
""".strip()


output["human_assessment"] = (
    output.apply(
        create_assessment,
        axis=1
    )
)


# =========================================================
# 7. EXAMPLES
# =========================================================

print(
    "\nExample applicant assessments:"
)

for i in range(
    min(5, len(output))
):

    row = output.iloc[i]

    print(
        "\n" + "=" * 60
    )

    print(
        f"APPLICANT {int(row['applicant_id'])}"
    )

    print(
        "=" * 60
    )

    print(
        row["human_assessment"]
    )


# =========================================================
# 8. SAVE
# =========================================================

output.to_csv(
    "kavach_explainability_output.csv",
    index=False
)

print(
    "\nSaved:"
)

print(
    "  kavach_explainability_output.csv"
)


# =========================================================
# 9. METHODOLOGY
# =========================================================

print("\n")
print("=" * 70)

print(
    "METHODOLOGY NOTE"
)

print("=" * 70)

print(
    """
This explanation engine uses rule-based comparisons
against population reference values.

It is an interpretability prototype.

It is NOT SHAP, LIME, causal inference, or a validated
credit explanation methodology.

Production explanations should be validated for:

1. Accuracy
2. Stability
3. Consistency with the model
4. Actionability
5. Applicant comprehension
6. Regulatory requirements
"""
)

print("=" * 70)

print(
    "EXPLAINABILITY ENGINE COMPLETE"
)

print("=" * 70)
