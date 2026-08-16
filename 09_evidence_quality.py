import pandas as pd
import numpy as np

print("=" * 70)
print("KAVACH PULSE — EVIDENCE QUALITY ENGINE")
print("=" * 70)


# =========================================================
# 1. SYNTHETIC CONSENTED-DATA PROFILE
# =========================================================
#
# This is a prototype representation of what Kavach would
# receive AFTER the applicant provides authorization.
#
# It is NOT real applicant data.
#
# =========================================================

rng = np.random.default_rng(42)

N = 10000

data = pd.DataFrame({

    "months_of_history":
        rng.integers(
            1,
            25,
            N
        ),

    "required_fields":
        12,

    "available_fields":
        rng.integers(
            5,
            13,
            N
        ),

    "days_since_latest_data":
        rng.integers(
            0,
            120,
            N
        ),

    "source_consistency":
        rng.uniform(
            0.50,
            1.00,
            N
        ),

    "missing_period_ratio":
        rng.uniform(
            0.00,
            0.30,
            N
        ),

    "duplicate_record_ratio":
        rng.uniform(
            0.00,
            0.03,
            N
        ),

    "invalid_record_ratio":
        rng.uniform(
            0.00,
            0.02,
            N
        )
})


# =========================================================
# 2. COMPLETENESS SCORE
# =========================================================

data["completeness_score"] = (
    data["available_fields"] /
    data["required_fields"]
)

data["completeness_score"] = np.clip(
    data["completeness_score"],
    0,
    1
)


# =========================================================
# 3. HISTORY DEPTH SCORE
# =========================================================
#
# We treat 12 months as the reference point.
#
# More than 12 months does not provide unlimited extra
# confidence, so we cap the score.
#
# =========================================================

data["history_score"] = (
    data["months_of_history"] /
    12
)

data["history_score"] = np.clip(
    data["history_score"],
    0,
    1
)


# =========================================================
# 4. RECENCY SCORE
# =========================================================
#
# Recent data receives higher confidence.
#
# 0 days old → 1.0
# 90+ days old → approximately 0
#
# =========================================================

data["recency_score"] = (
    1 -
    data["days_since_latest_data"] / 90
)

data["recency_score"] = np.clip(
    data["recency_score"],
    0,
    1
)


# =========================================================
# 5. CONSISTENCY SCORE
# =========================================================

data["consistency_score"] = (
    data["source_consistency"]
)


# =========================================================
# 6. DATA INTEGRITY SCORE
# =========================================================
#
# Penalize missing periods, duplicates and invalid records.
#
# =========================================================

data["integrity_score"] = (
    1
    - data["missing_period_ratio"]
    - data["duplicate_record_ratio"]
    - data["invalid_record_ratio"]
)

data["integrity_score"] = np.clip(
    data["integrity_score"],
    0,
    1
)


# =========================================================
# 7. EVIDENCE QUALITY SCORE
# =========================================================
#
# Weighted score.
#
# These weights are PROTOTYPE assumptions.
# They are not empirically validated production weights.
#
# =========================================================

WEIGHTS = {

    "completeness": 0.25,

    "history": 0.20,

    "recency": 0.15,

    "consistency": 0.20,

    "integrity": 0.20
}


data["evidence_quality_score"] = (

    WEIGHTS["completeness"]
    * data["completeness_score"]

    +

    WEIGHTS["history"]
    * data["history_score"]

    +

    WEIGHTS["recency"]
    * data["recency_score"]

    +

    WEIGHTS["consistency"]
    * data["consistency_score"]

    +

    WEIGHTS["integrity"]
    * data["integrity_score"]

) * 100


# =========================================================
# 8. CONFIDENCE BAND
# =========================================================

def confidence_band(score):

    if score >= 80:
        return "HIGH"

    elif score >= 60:
        return "MEDIUM"

    else:
        return "LOW"


data["confidence_band"] = (
    data["evidence_quality_score"]
    .apply(confidence_band)
)


# =========================================================
# 9. EVIDENCE RECOMMENDATION
# =========================================================

def recommendation(row):

    score = row[
        "evidence_quality_score"
    ]

    history = row[
        "months_of_history"
    ]

    completeness = row[
        "completeness_score"
    ]

    if (
        score >= 80
        and history >= 6
        and completeness >= 0.80
    ):
        return "SUFFICIENT"

    elif score >= 60:
        return "MANUAL_REVIEW"

    else:
        return "INSUFFICIENT"


data["evidence_recommendation"] = (
    data.apply(
        recommendation,
        axis=1
    )
)


# =========================================================
# 10. SUMMARY
# =========================================================

print("\nEvidence Quality Statistics")
print("-" * 50)

print(
    data[
        [
            "completeness_score",
            "history_score",
            "recency_score",
            "consistency_score",
            "integrity_score",
            "evidence_quality_score"
        ]
    ]
    .describe()
    .round(3)
)


# =========================================================
# 11. BAND DISTRIBUTION
# =========================================================

print("\nConfidence Bands")
print("-" * 50)

print(
    data[
        "confidence_band"
    ]
    .value_counts()
)


# =========================================================
# 12. RECOMMENDATION DISTRIBUTION
# =========================================================

print("\nEvidence Recommendations")
print("-" * 50)

print(
    data[
        "evidence_recommendation"
    ]
    .value_counts()
)


# =========================================================
# 13. EXAMPLE APPLICANTS
# =========================================================

print("\nExample Applicants")
print("-" * 50)

example_columns = [

    "months_of_history",

    "available_fields",

    "days_since_latest_data",

    "source_consistency",

    "missing_period_ratio",

    "evidence_quality_score",

    "confidence_band",

    "evidence_recommendation"
]

print(
    data[
        example_columns
    ]
    .head(10)
    .round(3)
    .to_string(
        index=False
    )
)


# =========================================================
# 14. SAVE
# =========================================================

data.to_csv(
    "kavach_evidence_quality_demo.csv",
    index=False
)

print("\nSaved:")
print(
    "  kavach_evidence_quality_demo.csv"
)

print("\nIMPORTANT:")
print(
    "The Evidence Quality Score is a prototype heuristic."
)

print(
    "It is NOT a calibrated probability."
)

print(
    "Production weights must be validated on real data."
)

print("=" * 70)
print("EVIDENCE QUALITY ENGINE COMPLETE")
print("=" * 70)
