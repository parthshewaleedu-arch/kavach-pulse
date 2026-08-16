import pandas as pd
import numpy as np

print("=" * 70)
print("KAVACH PULSE — FEATURE CONTRIBUTION ENGINE")
print("=" * 70)


# =========================================================
# 1. LOAD DATA
# =========================================================

df = pd.read_csv(
    "kavach_behavioral_features.csv"
)

print(
    "\nApplicants:",
    len(df)
)


# =========================================================
# 2. PERCENTILE NORMALIZATION
# =========================================================

def percentile_score(series):

    return series.rank(
        pct=True
    )


# =========================================================
# 3. CREATE COMPONENT SCORES
# =========================================================

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

payment_strength = (
    df["payment_success_rate"]
)

balance_strength = (
    percentile_score(
        df["balance_min"]
    )
)

coverage_strength = (
    percentile_score(
        df["inflow_to_outflow_ratio"]
    )
)

trend_strength = (
    percentile_score(
        df["income_trend"]
    )
)


# =========================================================
# 4. COMPONENT WEIGHTS
# =========================================================

weights = {

    "income_stability": 0.25,

    "cashflow_stability": 0.20,

    "payment_strength": 0.20,

    "balance_strength": 0.15,

    "coverage_strength": 0.10,

    "trend_strength": 0.10
}


# =========================================================
# 5. CONTRIBUTIONS TO STABILITY SCORE
# =========================================================

df["contrib_income_stability"] = (
    weights["income_stability"]
    *
    income_stability
    *
    100
)

df["contrib_cashflow_stability"] = (
    weights["cashflow_stability"]
    *
    cashflow_stability
    *
    100
)

df["contrib_payment_strength"] = (
    weights["payment_strength"]
    *
    payment_strength
    *
    100
)

df["contrib_balance_strength"] = (
    weights["balance_strength"]
    *
    balance_strength
    *
    100
)

df["contrib_coverage_strength"] = (
    weights["coverage_strength"]
    *
    coverage_strength
    *
    100
)

df["contrib_trend_strength"] = (
    weights["trend_strength"]
    *
    trend_strength
    *
    100
)


# =========================================================
# 6. VERIFY SCORE
# =========================================================

calculated_score = (

    df["contrib_income_stability"]

    + df["contrib_cashflow_stability"]

    + df["contrib_payment_strength"]

    + df["contrib_balance_strength"]

    + df["contrib_coverage_strength"]

    + df["contrib_trend_strength"]
)


difference = (
    calculated_score
    -
    df["behavioral_stability_score"]
    if "behavioral_stability_score" in df.columns
    else 0
)


print(
    "\nContribution score generated."
)


# =========================================================
# 7. BUILD RISK CONTRIBUTIONS
# =========================================================
#
# Higher stability contribution reduces risk.
#
# We therefore represent positive stability as a
# risk-reducing contribution.
#
# =========================================================

component_names = {

    "income_stability":
        "Income stability",

    "cashflow_stability":
        "Cash-flow stability",

    "payment_strength":
        "Payment consistency",

    "balance_strength":
        "Minimum cash buffer",

    "coverage_strength":
        "Inflow-to-outflow coverage",

    "trend_strength":
        "Income trend"
}


component_scores = {

    "Income stability":
        df["contrib_income_stability"],

    "Cash-flow stability":
        df["contrib_cashflow_stability"],

    "Payment consistency":
        df["contrib_payment_strength"],

    "Minimum cash buffer":
        df["contrib_balance_strength"],

    "Inflow-to-outflow coverage":
        df["contrib_coverage_strength"],

    "Income trend":
        df["contrib_trend_strength"]
}


# =========================================================
# 8. APPLICANT EXPLANATION
# =========================================================

def generate_contributions(row):

    contributions = []

    for name, series in component_scores.items():

        value = series.loc[
            row.name
        ]

        contributions.append({

            "feature":
                name,

            "stability_contribution":
                value
        })


    # -----------------------------------------------------
    # Population mean contribution
    # -----------------------------------------------------

    for item in contributions:

        feature = item[
            "feature"
        ]

        population_mean = (
            component_scores[
                feature
            ].mean()
        )

        item[
            "relative_contribution"
        ] = (
            item[
                "stability_contribution"
            ]
            -
            population_mean
        )


    return contributions


# =========================================================
# 9. GENERATE HUMAN-READABLE EXPLANATIONS
# =========================================================

explanation_rows = []


for index, row in df.iterrows():

    contributions = (
        generate_contributions(
            row
        )
    )


    # -----------------------------------------------------
    # Sort relative contribution
    # -----------------------------------------------------

    contributions_sorted = sorted(
        contributions,
        key=lambda x:
            x["relative_contribution"],
        reverse=True
    )


    positive = []
    risk = []


    # -----------------------------------------------------
    # Strongest positive factors
    # -----------------------------------------------------

    for item in contributions_sorted:

        if (
            item[
                "relative_contribution"
            ] > 1.0
        ):

            positive.append(
                item["feature"]
            )


    # -----------------------------------------------------
    # Strongest negative factors
    # -----------------------------------------------------

    for item in reversed(
        contributions_sorted
    ):

        if (
            item[
                "relative_contribution"
            ] < -1.0
        ):

            risk.append(
                item["feature"]
            )


    # -----------------------------------------------------
    # Limit explanation length
    # -----------------------------------------------------

    positive = positive[:3]

    risk = risk[:3]


    if not positive:

        positive = [
            "No major above-average stability factor"
        ]


    if not risk:

        risk = [
            "No major below-average stability factor"
        ]


    # -----------------------------------------------------
    # Contribution values
    # -----------------------------------------------------

    contribution_text = []

    for item in contributions_sorted:

        contribution_text.append(
            (
                item["feature"],
                round(
                    item[
                        "relative_contribution"
                    ],
                    2
                )
            )
        )


    explanation_rows.append({

        "applicant_id":
            row["applicant_id"],

        "positive_factors":
            " | ".join(
                positive
            ),

        "risk_factors":
            " | ".join(
                risk
            ),

        "feature_contributions":
            str(
                contribution_text
            )
    })


explanation_df = pd.DataFrame(
    explanation_rows
)


# =========================================================
# 10. MERGE WITH EXISTING OUTPUT
# =========================================================

policy = pd.read_csv(
    "kavach_pd_policy_output.csv"
)


output = policy.merge(
    explanation_df,
    on="applicant_id",
    how="left"
)


# =========================================================
# 11. HUMAN-READABLE ASSESSMENT
# =========================================================

def assessment(row):

    return f"""
Risk proxy:
{row['pd_proxy']:.1%}

Risk band:
{row['risk_band']}

Evidence quality:
{row['evidence_quality_score']:.0f}/100

Confidence:
{row['confidence_band']}

What supports lower risk:
• {row['positive_factors'].replace(' | ', chr(10) + '• ')}

What increases concern:
• {row['risk_factors'].replace(' | ', chr(10) + '• ')}

Policy routing:
{row['policy_decision']}
""".strip()


output[
    "human_assessment"
] = (
    output.apply(
        assessment,
        axis=1
    )
)


# =========================================================
# 12. EXAMPLE OUTPUT
# =========================================================

print(
    "\nExample assessments:"
)

for i in range(
    min(10, len(output))
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

    print(
        "\nFeature contributions:"
    )

    print(
        row[
            "feature_contributions"
        ]
    )


# =========================================================
# 13. SAVE
# =========================================================

output.to_csv(
    "kavach_feature_contributions.csv",
    index=False
)


print(
    "\nSaved:"
)

print(
    "  kavach_feature_contributions.csv"
)


# =========================================================
# 14. METHODOLOGY NOTE
# =========================================================

print("\n")
print("=" * 70)

print(
    "METHODOLOGY NOTE"
)

print("=" * 70)

print(
    """
Feature contributions are derived from the prototype
behavioral stability scoring function.

They are NOT model-attribution values from SHAP/LIME.

They should be interpreted as contribution to the
prototype stability score, not causal effects on default.

Production implementation should use validated model
attribution methods and verify explanation fidelity.
"""
)

print("=" * 70)

print(
    "FEATURE CONTRIBUTION ENGINE COMPLETE"
)

print("=" * 70)
