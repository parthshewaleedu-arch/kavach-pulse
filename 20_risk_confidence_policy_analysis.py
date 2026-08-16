import numpy as np
import pandas as pd

print("=" * 70)
print("KAVACH PULSE — RISK + CONFIDENCE POLICY ANALYSIS")
print("=" * 70)


# =========================================================
# 1. LOAD KAVACH EVIDENCE DATA
# =========================================================

print("\n[1] Loading evidence data...")

df = pd.read_csv(
    "kavach_evidence_depth_output.csv"
)

print(
    "Dataset:",
    df.shape
)


# =========================================================
# 2. CREATE ILLUSTRATIVE RISK SCORE
# =========================================================
#
# IMPORTANT:
#
# This is NOT a calibrated probability of default.
#
# The purpose is to create a controlled demonstration
# distribution so that every Kavach policy branch can
# be tested.
#
# =========================================================

print(
    "\n[2] Creating illustrative risk score..."
)

rng = np.random.default_rng(42)

stability = (
    df["behavioral_stability_score"]
    .clip(0, 100)
)

# Convert behavioral stability into a normalized
# risk tendency.
#
# Higher stability -> lower risk tendency.

risk_tendency = (
    1
    -
    stability / 100
)

# Add controlled applicant-level variation.

risk_tendency += rng.normal(
    0,
    0.06,
    len(df)
)

risk_tendency = np.clip(
    risk_tendency,
    0,
    1
)

# Map the tendency into an illustrative
# 2% - 35% risk range.
#
# THIS IS NOT PD.

df[
    "illustrative_risk_score"
] = (
    0.02
    +
    risk_tendency
    * 0.33
)

df[
    "illustrative_risk_score"
] = np.clip(
    df[
        "illustrative_risk_score"
    ],
    0.02,
    0.35
)

print(
    df[
        "illustrative_risk_score"
    ].describe()
)
# =========================================================
# 3. RISK BANDS
# =========================================================

print(
    "\n[3] Creating risk bands..."
)


def risk_band(score):

    if score < 0.08:

        return "LOW"

    elif score < 0.14:

        return "MODERATE"

    elif score < 0.22:

        return "ELEVATED"

    else:

        return "HIGH"

df[
    "risk_band"
] = df[
    "illustrative_risk_score"
].apply(
    risk_band
)


print(
    df[
        "risk_band"
    ].value_counts()
)


# =========================================================
# 4. CONFIDENCE MAPPING
# =========================================================

print(
    "\n[4] Mapping evidence confidence..."
)


# Rename for clarity.

df[
    "confidence"
] = df[
    "depth_confidence_band"
]


print(
    df[
        "confidence"
    ].value_counts()
)


# =========================================================
# 5. POLICY MATRIX
# =========================================================
#
# IMPORTANT:
#
# This is a PROTOTYPE POLICY MATRIX.
#
# It does not represent lender-approved thresholds.
#
# =========================================================

print(
    "\n[5] Applying risk-confidence policy matrix..."
)


def policy_decision(
    risk,
    confidence,
    evidence_route
):

    # ---------------------------------------------
    # Evidence first
    # ---------------------------------------------

    if evidence_route == "INSUFFICIENT_EVIDENCE":

        return "INSUFFICIENT_EVIDENCE"


    if evidence_route == "REQUEST_MORE_DATA":

        return "REQUEST_MORE_DATA"


    # ---------------------------------------------
    # Low confidence should prevent automated
    # action regardless of apparently low risk.
    # ---------------------------------------------

    if confidence == "LOW":

        return "MANUAL_REVIEW"


    # ---------------------------------------------
    # High confidence
    # ---------------------------------------------

    if confidence == "HIGH":

        if risk < 0.08:

            return "PASS_TO_LENDER_POLICY"

        elif risk < 0.15:

            return "PASS_TO_LENDER_POLICY"

        elif risk < 0.25:

            return "MANUAL_REVIEW"

        else:

            return "DECLINE_OR_REVIEW"


    # ---------------------------------------------
    # Medium confidence
    # ---------------------------------------------

    if confidence == "MEDIUM":

        if risk < 0.08:

            return "MANUAL_REVIEW"

        elif risk < 0.15:

            return "MANUAL_REVIEW"

        elif risk < 0.25:

            return "MANUAL_REVIEW"

        else:

            return "DECLINE_OR_REVIEW"


    return "MANUAL_REVIEW"


df[
    "policy_decision"
] = df.apply(

    lambda row:
        policy_decision(

            row[
                "illustrative_risk_score"
            ],

            row[
                "confidence"
            ],

            row[
                "evidence_route"
            ]

        ),

    axis=1
)


# =========================================================
# 6. POLICY DISTRIBUTION
# =========================================================

print(
    "\n" + "=" * 70
)

print(
    "POLICY DECISION DISTRIBUTION"
)

print(
    "=" * 70
)

print(
    df[
        "policy_decision"
    ].value_counts()
)


# =========================================================
# 7. RISK × CONFIDENCE MATRIX
# =========================================================

print(
    "\n" + "=" * 70
)

print(
    "RISK × CONFIDENCE MATRIX"
)

print(
    "=" * 70
)


matrix = pd.crosstab(

    df[
        "risk_band"
    ],

    df[
        "confidence"
    ]

)


print(
    matrix
)


# =========================================================
# 8. POLICY MATRIX
# =========================================================

print(
    "\n" + "=" * 70
)

print(
    "POLICY BY RISK BAND AND CONFIDENCE"
)

print(
    "=" * 70
)


policy_matrix = pd.crosstab(

    [
        df[
            "risk_band"
        ],

        df[
            "confidence"
        ]

    ],

    df[
        "policy_decision"
    ]

)


print(
    policy_matrix
)


# =========================================================
# 9. KEY KAVACH PRINCIPLE TEST
# =========================================================
#
# Find applicants with apparently low risk
# but low confidence.
#
# =========================================================

print(
    "\n" + "=" * 70
)

print(
    "LOW-RISK / LOW-CONFIDENCE CASES"
)

print(
    "=" * 70
)


low_risk_low_confidence = df[
    (
        df[
            "risk_band"
        ]
        ==
        "LOW"
    )
    &
    (
        df[
            "confidence"
        ]
        ==
        "LOW"
    )
]


print(
    "Count:",
    len(
        low_risk_low_confidence
    )
)


if len(
    low_risk_low_confidence
) > 0:

    print(
        low_risk_low_confidence[
            [
                "applicant_id",
                "history_months",
                "available_months",
                "depth_adjusted_evidence_score",
                "illustrative_risk_score",
                "risk_band",
                "confidence",
                "policy_decision"
            ]
        ]
        .head(10)
        .to_string(
            index=False
        )
    )


# =========================================================
# 10. HIGH-RISK / HIGH-CONFIDENCE CASES
# =========================================================

print(
    "\n" + "=" * 70
)

print(
    "HIGH-RISK / HIGH-CONFIDENCE CASES"
)

print(
    "=" * 70
)


high_risk_high_confidence = df[
    (
        df[
            "risk_band"
        ]
        ==
        "HIGH"
    )
    &
    (
        df[
            "confidence"
        ]
        ==
        "HIGH"
    )
]


print(
    "Count:",
    len(
        high_risk_high_confidence
    )
)


# =========================================================
# 11. HISTORY DEPTH VS POLICY
# =========================================================

print(
    "\n" + "=" * 70
)

print(
    "POLICY BY HISTORY DEPTH"
)

print(
    "=" * 70
)


depth_policy = pd.crosstab(

    df[
        "history_depth_band"
    ],

    df[
        "policy_decision"
    ]

)


print(
    depth_policy
)


# =========================================================
# 12. SAVE
# =========================================================

df.to_csv(
    "kavach_risk_confidence_policy_output.csv",
    index=False
)

policy_matrix.to_csv(
    "kavach_risk_confidence_policy_matrix.csv"
)


print(
    "\nSaved:"
)

print(
    "  kavach_risk_confidence_policy_output.csv"
)

print(
    "  kavach_risk_confidence_policy_matrix.csv"
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
The illustrative risk score in this experiment
is NOT a probability of default.

The policy thresholds are NOT lender-approved
or regulatory thresholds.

This experiment demonstrates an architectural
principle:

RISK != CONFIDENCE

An apparently low-risk applicant with
insufficient evidence should not automatically
receive the same treatment as a low-risk
applicant supported by strong evidence.

Production implementation requires:

1. Real behavioral histories
2. Observed repayment outcomes
3. Calibrated PD modelling
4. Validated policy thresholds
5. Cost-sensitive threshold optimization
6. Fairness testing
7. Out-of-time validation
8. Lender policy integration
9. Regulatory/legal review
10. Human-review governance
"""
)

print(
    "=" * 70
)

print(
    "RISK + CONFIDENCE POLICY ANALYSIS COMPLETE"
)

print(
    "=" * 70
)
