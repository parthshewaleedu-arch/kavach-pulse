import numpy as np
import pandas as pd

print("=" * 70)
print("KAVACH PULSE — FAIRNESS & BIAS AUDIT")
print("=" * 70)


# =========================================================
# 1. LOAD DATA
# =========================================================

print("\n[1] Loading Home Credit data...")

application = pd.read_csv(
    "application_train.csv"
)

print(
    "Dataset:",
    application.shape
)


# =========================================================
# 2. LOAD KAVACH EVIDENCE DATA
# =========================================================

print(
    "\n[2] Loading Kavach evidence outputs..."
)

evidence = pd.read_csv(
    "kavach_evidence_depth_output.csv"
)

print(
    "Evidence dataset:",
    evidence.shape
)


# =========================================================
# 3. ALIGN APPLICANTS
# =========================================================
#
# Script 16 uses applicant_id based on row order.
# Home Credit application_train.csv also preserves
# row-level correspondence with the generated simulation.
#
# We therefore create the same row identifier.
#
# =========================================================

print(
    "\n[3] Aligning applicant records..."
)

application = application.reset_index(
    drop=True
)

application[
    "applicant_id"
] = np.arange(
    len(application)
)


# The evidence simulation contains 5,000
# applicants. Use the corresponding first
# 5,000 benchmark rows for this audit.

application_sample = application.iloc[
    :len(evidence)
].copy()


audit = application_sample.merge(
    evidence,
    on="applicant_id",
    how="inner"
)

print(
    "Aligned dataset:",
    audit.shape
)


# =========================================================
# 4. DEMOGRAPHIC / AUDIT ATTRIBUTES
# =========================================================

print(
    "\n[4] Preparing audit groups..."
)


# Gender is used ONLY for auditing.
#
# It is not used as a predictive feature.

audit[
    "gender_group"
] = audit[
    "CODE_GENDER"
].astype(
    str
)


# Education is also treated as an
# audit attribute, not automatically
# as a model feature.

audit[
    "education_group"
] = audit[
    "NAME_EDUCATION_TYPE"
].astype(
    str
)


# Income groups are useful for checking
# whether the system behaves differently
# across economic segments.

audit[
    "income_group"
] = pd.qcut(
    audit[
        "AMT_INCOME_TOTAL"
    ],
    q=4,
    labels=[
        "LOW",
        "LOWER_MIDDLE",
        "UPPER_MIDDLE",
        "HIGH"
    ],
    duplicates="drop"
)


# =========================================================
# 5. PROTOTYPE POLICY OUTCOME
# =========================================================
#
# IMPORTANT:
# This is NOT a lender policy.
#
# We use the evidence engine's routing
# because it is already defined.
#
# =========================================================

audit[
    "policy_outcome"
] = np.where(

    audit[
        "evidence_route"
    ]
    ==
    "SUFFICIENT",

    "PASS_TO_POLICY",

    np.where(

        audit[
            "evidence_route"
        ]
        ==
        "INSUFFICIENT_EVIDENCE",

        "INSUFFICIENT_EVIDENCE",

        np.where(

            audit[
                "evidence_route"
            ]
            ==
            "REQUEST_MORE_DATA",

            "REQUEST_MORE_DATA",

            "MANUAL_REVIEW"
        )
    )
)


# =========================================================
# 6. METRICS FUNCTION
# =========================================================

def group_metrics(
    dataframe,
    group_column
):

    rows = []

    total = len(
        dataframe
    )

    for group, df in dataframe.groupby(
        group_column,
        observed=True
    ):

        n = len(df)

        pass_rate = (
            (
                df[
                    "policy_outcome"
                ]
                ==
                "PASS_TO_POLICY"
            ).mean()
        )

        review_rate = (
            (
                df[
                    "policy_outcome"
                ]
                ==
                "MANUAL_REVIEW"
            ).mean()
        )

        insufficient_rate = (
            (
                df[
                    "policy_outcome"
                ]
                ==
                "INSUFFICIENT_EVIDENCE"
            ).mean()
        )

        more_data_rate = (
            (
                df[
                    "policy_outcome"
                ]
                ==
                "REQUEST_MORE_DATA"
            ).mean()
        )

        high_confidence_rate = (
            (
                df[
                    "depth_confidence_band"
                ]
                ==
                "HIGH"
            ).mean()
        )

        rows.append({

            "group": group,

            "n": n,

            "population_share":
                n / total,

            "pass_rate":
                pass_rate,

            "manual_review_rate":
                review_rate,

            "insufficient_evidence_rate":
                insufficient_rate,

            "request_more_data_rate":
                more_data_rate,

            "high_confidence_rate":
                high_confidence_rate,

            "avg_evidence_score":
                df[
                    "depth_adjusted_evidence_score"
                ].mean(),

            "avg_risk_proxy":
                df[
                    "behavioral_stability_score"
                ].mean()

        })

    return pd.DataFrame(
        rows
    )


# =========================================================
# 7. RUN GROUP ANALYSIS
# =========================================================

print(
    "\n[5] Gender fairness analysis..."
)

gender_results = group_metrics(
    audit,
    "gender_group"
)

print(
    gender_results.to_string(
        index=False
    )
)


print(
    "\n[6] Education fairness analysis..."
)

education_results = group_metrics(
    audit,
    "education_group"
)

print(
    education_results.to_string(
        index=False
    )
)


print(
    "\n[7] Income-group analysis..."
)

income_results = group_metrics(
    audit,
    "income_group"
)

print(
    income_results.to_string(
        index=False
    )
)


# =========================================================
# 8. SELECTION RATE RATIO
# =========================================================
#
# A simple four-fifths / 80% style screening
# statistic can be used as an initial diagnostic.
#
# This is NOT a universal legal test.
#
# =========================================================

def selection_rate_ratio(
    results
):

    max_rate = results[
        "pass_rate"
    ].max()

    min_rate = results[
        "pass_rate"
    ].min()

    if max_rate == 0:

        return np.nan

    return (
        min_rate
        /
        max_rate
    )


gender_srr = selection_rate_ratio(
    gender_results
)

education_srr = selection_rate_ratio(
    education_results
)

income_srr = selection_rate_ratio(
    income_results
)


print(
    "\n" + "=" * 70
)

print(
    "SELECTION RATE DIAGNOSTICS"
)

print(
    "=" * 70
)

print(
    f"Gender selection-rate ratio:     "
    f"{gender_srr:.3f}"
)

print(
    f"Education selection-rate ratio:  "
    f"{education_srr:.3f}"
)

print(
    f"Income selection-rate ratio:     "
    f"{income_srr:.3f}"
)


# =========================================================
# 9. RISK DISTRIBUTION DIFFERENCE
# =========================================================

print(
    "\n[8] Risk distribution analysis..."
)


def risk_range(
    results
):

    return (
        results[
            "avg_risk_proxy"
        ].max()
        -
        results[
            "avg_risk_proxy"
        ].min()
    )


print(
    "Gender risk-score range:",
    round(
        risk_range(
            gender_results
        ),
        3
    )
)

print(
    "Education risk-score range:",
    round(
        risk_range(
            education_results
        ),
        3
    )
)

print(
    "Income risk-score range:",
    round(
        risk_range(
            income_results
        ),
        3
    )
)


# =========================================================
# 10. DATA QUALITY FAIRNESS
# =========================================================
#
# This is particularly important for Kavach.
#
# We don't only ask:
#
# "Does risk differ?"
#
# We ask:
#
# "Does evidence availability differ?"
#
# =========================================================

print(
    "\n[9] Evidence availability analysis..."
)


def evidence_metrics(
    dataframe,
    group_column
):

    return (

        dataframe
        .groupby(
            group_column,
            observed=True
        )
        .agg(

            applicants=(
                "applicant_id",
                "count"
            ),

            avg_history_months=(
                "history_months",
                "mean"
            ),

            avg_completeness=(
                "history_completeness",
                "mean"
            ),

            avg_evidence_score=(
                "depth_adjusted_evidence_score",
                "mean"
            ),

            low_confidence_rate=(
                "depth_confidence_band",
                lambda x:
                (
                    x == "LOW"
                ).mean()
            ),

            insufficient_rate=(
                "evidence_route",
                lambda x:
                (
                    x
                    ==
                    "INSUFFICIENT_EVIDENCE"
                ).mean()
            )

        )
    )


gender_evidence = evidence_metrics(
    audit,
    "gender_group"
)

print(
    "\nGender evidence availability:"
)

print(
    gender_evidence
)


income_evidence = evidence_metrics(
    audit,
    "income_group"
)

print(
    "\nIncome evidence availability:"
)

print(
    income_evidence
)


# =========================================================
# 11. AUTOMATED FLAGS
# =========================================================

print(
    "\n[10] Generating fairness flags..."
)


def flag_selection_ratio(
    ratio
):

    if pd.isna(
        ratio
    ):

        return "UNAVAILABLE"

    if ratio < 0.80:

        return "INVESTIGATE"

    return "NO_INITIAL_FLAG"


fairness_flags = {

    "gender_selection_rate":
        flag_selection_ratio(
            gender_srr
        ),

    "education_selection_rate":
        flag_selection_ratio(
            education_srr
        ),

    "income_selection_rate":
        flag_selection_ratio(
            income_srr
        )
}


for key, value in fairness_flags.items():

    print(
        f"{key}: {value}"
    )


# =========================================================
# 12. SAVE RESULTS
# =========================================================

gender_results.to_csv(
    "kavach_fairness_gender.csv",
    index=False
)

education_results.to_csv(
    "kavach_fairness_education.csv",
    index=False
)

income_results.to_csv(
    "kavach_fairness_income.csv",
    index=False
)

gender_evidence.to_csv(
    "kavach_fairness_gender_evidence.csv"
)

income_evidence.to_csv(
    "kavach_fairness_income_evidence.csv"
)


# =========================================================
# 13. METHODOLOGY WARNING
# =========================================================

print(
    "\n" + "=" * 70
)

print(
    "METHODOLOGY WARNING"
)

print(
    "=" * 70
)

print(
    """
This is a prototype fairness audit.

It does NOT establish legal compliance,
regulatory compliance, or absence of discrimination.

The analysis uses:

1. Public benchmark data
2. Synthetic behavioral histories
3. Prototype evidence rules
4. Prototype policy routing

The demographic variables are used for
AUDITING, not predictive modelling.

Production fairness validation requires:

- Representative target-population data
- Validated outcomes
- Appropriate protected attributes
- Legally reviewed fairness methodology
- Intersectional analysis
- Error-rate analysis
- Calibration analysis
- Human-review analysis
- Ongoing monitoring

A selection-rate ratio is an initial diagnostic,
not a universal legal standard.
"""
)

print(
    "\nSaved fairness analysis files."
)

print(
    "=" * 70
)

print(
    "FAIRNESS & BIAS AUDIT COMPLETE"
)

print(
    "=" * 70
)
