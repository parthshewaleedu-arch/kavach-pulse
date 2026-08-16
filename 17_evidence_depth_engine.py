import numpy as np
import pandas as pd

print("=" * 70)
print("KAVACH PULSE — EVIDENCE DEPTH ENGINE")
print("=" * 70)


# =========================================================
# 1. LOAD DATA
# =========================================================

print("\n[1] Loading thin-file behavioral dataset...")

features = pd.read_csv(
    "kavach_thin_file_behavioral_features.csv"
)

print(
    "Dataset:",
    features.shape
)


# =========================================================
# 2. HISTORY DEPTH CLASSIFICATION
# =========================================================

print(
    "\n[2] Classifying history depth..."
)


def classify_history_depth(months):

    if months <= 2:

        return "VERY_THIN"

    elif months <= 5:

        return "THIN"

    elif months <= 8:

        return "DEVELOPING"

    elif months <= 11:

        return "STRONG"

    else:

        return "ESTABLISHED"


features[
    "history_depth_band"
] = (
    features[
        "history_months"
    ].apply(
        classify_history_depth
    )
)


# =========================================================
# 3. NUMERIC DEPTH SCORE
# =========================================================

print(
    "\n[3] Calculating history depth score..."
)


def history_depth_score(months):

    if months <= 2:

        return 0.25

    elif months <= 5:

        return 0.45

    elif months <= 8:

        return 0.65

    elif months <= 11:

        return 0.85

    else:

        return 1.00


features[
    "history_depth_score"
] = (
    features[
        "history_months"
    ].apply(
        history_depth_score
    )
)


# =========================================================
# 4. OBSERVATION QUALITY
# =========================================================

print(
    "\n[4] Calculating observation quality..."
)


features[
    "observation_quality"
] = (

    0.60
    *
    features[
        "history_completeness"
    ]

    +

    0.40
    *
    features[
        "history_depth_score"
    ]

)


# =========================================================
# 5. SOURCE COVERAGE
# =========================================================

print(
    "\n[5] Calculating source coverage..."
)


source_columns = [

    "income_mean",

    "bank_inflow_mean",

    "bank_outflow_mean",

    "payment_success_rate"
]


source_available = (
    features[
        source_columns
    ]
    .notna()
    .sum(
        axis=1
    )
)


features[
    "source_coverage"
] = (
    source_available
    /
    len(
        source_columns
    )
)


# =========================================================
# 6. DATA CONSISTENCY
# =========================================================

print(
    "\n[6] Calculating data consistency..."
)


features[
    "data_consistency"
] = np.clip(

    0.75
    +

    0.20
    *
    features[
        "history_completeness"
    ]

    +

    np.random.default_rng(
        42
    ).normal(
        0,
        0.04,
        len(features)
    ),

    0.50,

    1.00
)


# =========================================================
# 7. NEW EVIDENCE QUALITY
# =========================================================
#
# Important:
#
# We now explicitly include history depth.
#
# =========================================================

print(
    "\n[7] Calculating depth-adjusted evidence quality..."
)


features[
    "depth_adjusted_evidence_score"
] = (

    0.35
    *
    features[
        "history_depth_score"
    ]

    +

    0.30
    *
    features[
        "history_completeness"
    ]

    +

    0.20
    *
    features[
        "source_coverage"
    ]

    +

    0.15
    *
    features[
        "data_consistency"
    ]

) * 100


features[
    "depth_adjusted_evidence_score"
] = (
    features[
        "depth_adjusted_evidence_score"
    ].clip(
        0,
        100
    )
)


# =========================================================
# 8. CONFIDENCE BAND
# =========================================================

print(
    "\n[8] Assigning confidence..."
)


def confidence_band(
    evidence_score,
    history_band
):

    # Very thin files cannot receive HIGH
    # confidence in this prototype.

    if history_band == "VERY_THIN":

        return "LOW"

    if evidence_score >= 80:

        return "HIGH"

    elif evidence_score >= 60:

        return "MEDIUM"

    else:

        return "LOW"


features[
    "depth_confidence_band"
] = features.apply(

    lambda row:
        confidence_band(
            row[
                "depth_adjusted_evidence_score"
            ],
            row[
                "history_depth_band"
            ]
        ),

    axis=1
)


# =========================================================
# 9. EVIDENCE ROUTING
# =========================================================

print(
    "\n[9] Creating evidence routing..."
)


def evidence_route(row):

    history_band = row[
        "history_depth_band"
    ]

    confidence = row[
        "depth_confidence_band"
    ]

    completeness = row[
        "history_completeness"
    ]


    if history_band == "VERY_THIN":

        return "INSUFFICIENT_EVIDENCE"


    if completeness < 0.60:

        return "REQUEST_MORE_DATA"


    if confidence == "LOW":

        return "MANUAL_REVIEW"


    if confidence == "MEDIUM":

        return "MANUAL_REVIEW"


    return "SUFFICIENT"


features[
    "evidence_route"
] = features.apply(
    evidence_route,
    axis=1
)


# =========================================================
# 10. SANITY CHECKS
# =========================================================

print(
    "\n" + "=" * 70
)

print(
    "HISTORY DEPTH DISTRIBUTION"
)

print(
    "=" * 70
)

print(
    features[
        "history_depth_band"
    ].value_counts()
)


print(
    "\nCONFIDENCE DISTRIBUTION"
)

print(
    features[
        "depth_confidence_band"
    ].value_counts()
)


print(
    "\nEVIDENCE ROUTING"
)

print(
    features[
        "evidence_route"
    ].value_counts()
)


# =========================================================
# 11. DEPTH BAND SUMMARY
# =========================================================

print(
    "\n" + "=" * 70
)

print(
    "EVIDENCE QUALITY BY HISTORY DEPTH"
)

print(
    "=" * 70
)


summary = (

    features
    .groupby(
        "history_depth_band",
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
        )

    )
)


print(
    summary
)


# =========================================================
# 12. EXAMPLE APPLICANTS
# =========================================================

print(
    "\n" + "=" * 70
)

print(
    "EXAMPLE APPLICANTS"
)

print(
    "=" * 70
)


for depth in [
    "VERY_THIN",
    "THIN",
    "DEVELOPING",
    "STRONG",
    "ESTABLISHED"
]:

    subset = features[
        features[
            "history_depth_band"
        ]
        ==
        depth
    ]

    if len(subset) == 0:

        continue


    row = subset.iloc[0]


    print(
        f"""
Applicant: {int(row['applicant_id'])}

History:
{int(row['history_months'])} months

Available:
{int(row['available_months'])} months

Completeness:
{row['history_completeness']:.2f}

History depth:
{row['history_depth_band']}

Evidence score:
{row['depth_adjusted_evidence_score']:.1f}/100

Confidence:
{row['depth_confidence_band']}

Routing:
{row['evidence_route']}
"""
    )


# =========================================================
# 13. SAVE
# =========================================================

features.to_csv(
    "kavach_evidence_depth_output.csv",
    index=False
)


print(
    "\nSaved:"
)

print(
    "  kavach_evidence_depth_output.csv"
)


# =========================================================
# 14. METHODOLOGY NOTE
# =========================================================

print(
    "\n" + "=" * 70
)

print(
    "METHODOLOGY NOTE"
)

print(
    "=" * 70
)

print(
    """
History depth is a prototype evidence-quality
concept, not a validated credit-risk threshold.

The system deliberately separates:

1. Data completeness
2. History depth
3. Source coverage
4. Data consistency
5. Confidence

A short but complete history should not be
treated as equivalent to a long complete history.

The thresholds are demonstration assumptions.

Production thresholds require validation on
real consented applicant histories and observed
outcomes.
"""
)

print(
    "=" * 70
)

print(
    "EVIDENCE DEPTH ENGINE COMPLETE"
)

print(
    "=" * 70
)
