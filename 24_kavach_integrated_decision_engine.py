"""
======================================================================
KAVACH PULSE — INTEGRATED DECISION ENGINE
======================================================================

Purpose
-------
Integrates the outputs of the Kavach prototype into one
end-to-end applicant assessment pipeline.

Pipeline
--------
Behavioral data
        ↓
Evidence depth
        ↓
Evidence quality
        ↓
Confidence
        ↓
Behavioral risk proxy
        ↓
Risk band
        ↓
Policy routing
        ↓
Explanation
        ↓
Governance / provenance
        ↓
Final assessment

IMPORTANT
---------
This is a TECHNICAL / CONCEPTUAL PROTOTYPE.

Behavioral data and risk proxies are synthetic.

The risk proxy is NOT a calibrated probability of default.

The policy thresholds are NOT lender-approved thresholds.

This engine must NOT be represented as a production
credit underwriting system.
"""

import os
import json
import uuid
from datetime import datetime

import numpy as np
import pandas as pd


# ======================================================================
# CONFIGURATION
# ======================================================================

BEHAVIORAL_FILE = "kavach_thin_file_behavioral_features.csv"
EVIDENCE_FILE = "kavach_evidence_depth_output.csv"
PD_POLICY_FILE = "kavach_pd_policy_output.csv"
EXPLAINABILITY_FILE = "kavach_explainability_output.csv"
CONTRIBUTION_FILE = "kavach_feature_contributions.csv"
CONSENT_FILE = "kavach_consent_records.csv"
PROVENANCE_FILE = "kavach_model_provenance_audit.json"

OUTPUT_FILE = "kavach_integrated_decision_output.csv"
AUDIT_FILE = "kavach_integrated_audit_log.csv"
SUMMARY_FILE = "kavach_integrated_summary.json"

MODEL_VERSION = "KAVACH-PROTOTYPE-v1"
POLICY_VERSION = "KAVACH-POLICY-PROTOTYPE-v1"
ENGINE_VERSION = "24.0"


# ======================================================================
# HELPER FUNCTIONS
# ======================================================================

def section(title):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def load_csv(path, required=True):
    """
    Load a CSV and provide a clear error if it is missing.
    """

    if not os.path.exists(path):

        if required:
            raise FileNotFoundError(
                f"\nRequired file not found:\n  {path}\n\n"
                f"Run the corresponding previous Kavach script first."
            )

        return pd.DataFrame()

    df = pd.read_csv(path)

    print(f"Loaded {path}: {df.shape}")

    return df


def normalize_id_column(df, name):
    """
    Make sure applicant_id exists and is integer-like.
    """

    if "applicant_id" not in df.columns:

        raise ValueError(
            f"{name} does not contain 'applicant_id'.\n"
            f"Available columns:\n{df.columns.tolist()}"
        )

    df["applicant_id"] = pd.to_numeric(
        df["applicant_id"],
        errors="coerce"
    )

    if df["applicant_id"].isna().any():

        raise ValueError(
            f"{name} contains invalid applicant_id values."
        )

    df["applicant_id"] = df["applicant_id"].astype(int)

    return df


def first_existing(df, candidates, default=np.nan):
    """
    Return the first available column from a list of candidates.
    """

    for column in candidates:

        if column in df.columns:
            return df[column]

    return pd.Series(
        default,
        index=df.index
    )


def clean_text(value, default="UNKNOWN"):
    """
    Safely convert a value into printable text.
    """

    if pd.isna(value):
        return default

    return str(value)


def safe_round(value, digits=3):

    if pd.isna(value):
        return np.nan

    return round(float(value), digits)


# ======================================================================
# START
# ======================================================================

section("KAVACH PULSE — INTEGRATED DECISION ENGINE")

print()
print("Engine version :", ENGINE_VERSION)
print("Model version  :", MODEL_VERSION)
print("Policy version :", POLICY_VERSION)

print()
print("IMPORTANT:")
print("This engine integrates prototype outputs.")
print("Synthetic behavioral data is NOT real borrower data.")
print("Risk proxy is NOT calibrated probability of default.")


# ======================================================================
# 1. LOAD DATA
# ======================================================================

section("[1] Loading Kavach outputs")

behavioral = load_csv(BEHAVIORAL_FILE)
evidence = load_csv(EVIDENCE_FILE)
pd_policy = load_csv(PD_POLICY_FILE)
explainability = load_csv(
    EXPLAINABILITY_FILE,
    required=False
)
contributions = load_csv(
    CONTRIBUTION_FILE,
    required=False
)
consent = load_csv(
    CONSENT_FILE,
    required=False
)


# ======================================================================
# 2. NORMALIZE IDENTIFIERS
# ======================================================================

section("[2] Normalizing applicant identifiers")

behavioral = normalize_id_column(
    behavioral,
    "Behavioral dataset"
)

evidence = normalize_id_column(
    evidence,
    "Evidence dataset"
)

pd_policy = normalize_id_column(
    pd_policy,
    "PD policy dataset"
)

if not explainability.empty:

    explainability = normalize_id_column(
        explainability,
        "Explainability dataset"
    )

if not contributions.empty:

    contributions = normalize_id_column(
        contributions,
        "Contribution dataset"
    )


print("Behavioral applicants :", behavioral["applicant_id"].nunique())
print("Evidence applicants   :", evidence["applicant_id"].nunique())
print("Policy applicants     :", pd_policy["applicant_id"].nunique())


# ======================================================================
# 3. CHECK DUPLICATES
# ======================================================================

section("[3] Checking applicant uniqueness")

for name, df in [
    ("Behavioral", behavioral),
    ("Evidence", evidence),
    ("PD / Policy", pd_policy),
]:

    duplicates = df["applicant_id"].duplicated().sum()

    print(
        f"{name:15s}: "
        f"{duplicates} duplicate applicant IDs"
    )

    if duplicates > 0:

        raise ValueError(
            f"{name} dataset contains duplicate applicant_id values."
        )


# ======================================================================
# 4. MERGE CORE DATASETS
# ======================================================================

section("[4] Building integrated applicant dataset")

integrated = behavioral.copy()

integrated = integrated.merge(
    evidence,
    on="applicant_id",
    how="left",
    suffixes=("", "_evidence")
)

integrated = integrated.merge(
    pd_policy,
    on="applicant_id",
    how="left",
    suffixes=("", "_policy")
)


print(
    "Integrated core dataset:",
    integrated.shape
)


# ======================================================================
# 5. CHECK MERGE COMPLETENESS
# ======================================================================

section("[5] Checking integration completeness")

critical_columns = [
    "applicant_id"
]

for column in critical_columns:

    if column not in integrated.columns:

        raise ValueError(
            f"Critical column missing after integration: {column}"
        )


evidence_match_rate = (
    integrated["evidence_quality_score"]
    .notna()
    .mean()
    if "evidence_quality_score" in integrated.columns
    else 0
)


policy_match_candidates = [
    "pd_proxy",
    "pd_estimate",
    "risk_proxy",
    "illustrative_risk_score"
]

policy_column_found = None

for column in policy_match_candidates:

    if column in integrated.columns:

        policy_column_found = column
        break


if policy_column_found is None:

    raise ValueError(
        "Could not find a risk column in the policy output.\n"
        f"Expected one of: {policy_match_candidates}\n"
        f"Available columns:\n{integrated.columns.tolist()}"
    )


policy_match_rate = (
    integrated[policy_column_found]
    .notna()
    .mean()
)


print(
    f"Evidence match rate: {evidence_match_rate:.4f}"
)

print(
    f"Risk/policy match rate: {policy_match_rate:.4f}"
)


if evidence_match_rate < 0.99:

    raise ValueError(
        "Evidence integration failed."
    )


if policy_match_rate < 0.99:

    raise ValueError(
        "Risk/policy integration failed."
    )


# ======================================================================
# 6. STANDARDIZE RISK VARIABLE
# ======================================================================

section("[6] Standardizing risk output")

integrated["risk_proxy"] = pd.to_numeric(
    integrated[policy_column_found],
    errors="coerce"
)


# Convert percentage-like risk values to decimal
# if necessary.

if integrated["risk_proxy"].median() > 1:

    integrated["risk_proxy"] = (
        integrated["risk_proxy"] / 100.0
    )


integrated["risk_proxy"] = integrated[
    "risk_proxy"
].clip(
    0,
    1
)


print(
    "Risk source:",
    policy_column_found
)

print()
print(
    integrated["risk_proxy"].describe()
)


# ======================================================================
# 7. STANDARDIZE RISK BAND
# ======================================================================

section("[7] Standardizing risk band")

if "risk_band" not in integrated.columns:

    def assign_risk_band(pd_value):

        if pd.isna(pd_value):
            return "UNKNOWN"

        if pd_value < 0.08:
            return "LOW"

        elif pd_value < 0.15:
            return "MODERATE"

        elif pd_value < 0.25:
            return "ELEVATED"

        else:
            return "HIGH"

    integrated["risk_band"] = (
        integrated["risk_proxy"]
        .apply(assign_risk_band)
    )


integrated["risk_band"] = (
    integrated["risk_band"]
    .fillna("UNKNOWN")
    .astype(str)
)


print(
    integrated["risk_band"]
    .value_counts()
)


# ======================================================================
# 8. EVIDENCE QUALITY
# ======================================================================

section("[8] Evidence quality and confidence")

if "depth_adjusted_evidence_score" in integrated.columns:

    integrated["final_evidence_quality"] = pd.to_numeric(
        integrated["depth_adjusted_evidence_score"],
        errors="coerce"
    )

elif "evidence_quality_score" in integrated.columns:

    integrated["final_evidence_quality"] = pd.to_numeric(
        integrated["evidence_quality_score"],
        errors="coerce"
    )

else:

    integrated["final_evidence_quality"] = np.nan


integrated["final_evidence_quality"] = (
    integrated["final_evidence_quality"]
    .clip(0, 100)
)


if "depth_confidence_band" in integrated.columns:

    integrated["final_confidence"] = (
        integrated["depth_confidence_band"]
        .fillna("UNKNOWN")
        .astype(str)
    )

elif "confidence_band" in integrated.columns:

    integrated["final_confidence"] = (
        integrated["confidence_band"]
        .fillna("UNKNOWN")
        .astype(str)
    )

elif "confidence" in integrated.columns:

    integrated["final_confidence"] = (
        integrated["confidence"]
        .fillna("UNKNOWN")
        .astype(str)
    )

else:

    def confidence_from_score(score):

        if pd.isna(score):
            return "UNKNOWN"

        if score >= 85:
            return "HIGH"

        if score >= 70:
            return "MEDIUM"

        return "LOW"

    integrated["final_confidence"] = (
        integrated["final_evidence_quality"]
        .apply(confidence_from_score)
    )


print(
    integrated["final_confidence"]
    .value_counts()
)


# ======================================================================
# 9. HISTORY DEPTH
# ======================================================================

section("[9] History depth")

if "history_depth_band" in integrated.columns:

    integrated["final_history_depth"] = (
        integrated["history_depth_band"]
        .fillna("UNKNOWN")
        .astype(str)
    )

else:

    def depth_from_history(months):

        if pd.isna(months):
            return "UNKNOWN"

        months = float(months)

        if months <= 2:
            return "VERY_THIN"

        elif months <= 5:
            return "THIN"

        elif months <= 8:
            return "DEVELOPING"

        elif months <= 11:
            return "STRONG"

        return "ESTABLISHED"

    history_source = first_existing(
        integrated,
        [
            "history_months",
            "available_months"
        ]
    )

    integrated["final_history_depth"] = (
        history_source
        .apply(depth_from_history)
    )


# ======================================================================
# 10. COMPLETENESS
# ======================================================================

if "history_completeness" in integrated.columns:

    integrated["final_completeness"] = pd.to_numeric(
        integrated["history_completeness"],
        errors="coerce"
    )

else:

    available = first_existing(
        integrated,
        ["available_months"]
    )

    history = first_existing(
        integrated,
        ["history_months"]
    )

    integrated["final_completeness"] = (
        available / history.replace(0, np.nan)
    )


integrated["final_completeness"] = (
    integrated["final_completeness"]
    .clip(0, 1)
)


# ======================================================================
# 11. BEHAVIORAL STABILITY
# ======================================================================

section("[10] Behavioral stability")

if "behavioral_stability_score" in integrated.columns:

    integrated["behavioral_stability"] = pd.to_numeric(
        integrated["behavioral_stability_score"],
        errors="coerce"
    )

else:

    # Fallback prototype score.
    # This is deliberately simple and transparent.

    payment = first_existing(
        integrated,
        ["payment_success_rate"],
        default=0.5
    ).fillna(0.5)

    income_cv = first_existing(
        integrated,
        ["income_cv"],
        default=0.5
    ).fillna(0.5)

    cashflow_cv = first_existing(
        integrated,
        ["cashflow_cv"],
        default=0.5
    ).fillna(0.5)

    buffer = first_existing(
        integrated,
        ["balance_min"],
        default=0
    ).fillna(0)

    ratio = first_existing(
        integrated,
        ["inflow_to_outflow_ratio"],
        default=1
    ).fillna(1)

    # Normalize each component.

    payment_score = (
        payment.clip(0, 1) * 100
    )

    income_score = (
        1 - income_cv.clip(0, 1)
    ) * 100

    cashflow_score = (
        1 - cashflow_cv.clip(0, 1)
    ) * 100

    buffer_score = (
        buffer /
        max(buffer.quantile(0.95), 1)
    ).clip(0, 1) * 100

    ratio_score = (
        (ratio - 1) /
        1
    ).clip(0, 1) * 100

    integrated["behavioral_stability"] = (
        0.30 * payment_score
        + 0.20 * income_score
        + 0.20 * cashflow_score
        + 0.15 * buffer_score
        + 0.15 * ratio_score
    )


integrated["behavioral_stability"] = (
    integrated["behavioral_stability"]
    .clip(0, 100)
)


# ======================================================================
# 12. FINAL POLICY ROUTING
# ======================================================================

section("[11] Applying integrated risk-confidence policy")

def policy_router(row):

    risk = row["risk_proxy"]
    confidence = str(
        row["final_confidence"]
    ).upper()

    evidence = row["final_evidence_quality"]

    # --------------------------------------------------------------
    # Insufficient evidence
    # --------------------------------------------------------------

    if (
        confidence == "LOW"
        or (
            not pd.isna(evidence)
            and evidence < 70
        )
    ):

        return "INSUFFICIENT_EVIDENCE"

    # --------------------------------------------------------------
    # High confidence + low risk
    # --------------------------------------------------------------

    if (
        risk < 0.08
        and confidence == "HIGH"
    ):

        return "PASS_TO_LENDER_POLICY"

    # --------------------------------------------------------------
    # Moderate risk + high confidence
    # --------------------------------------------------------------

    if (
        risk < 0.15
        and confidence == "HIGH"
    ):

        return "PASS_TO_LENDER_POLICY"

    # --------------------------------------------------------------
    # High risk
    # --------------------------------------------------------------

    if risk >= 0.25:

        if confidence == "HIGH":

            return "DECLINE_OR_REVIEW"

        return "MANUAL_REVIEW"

    # --------------------------------------------------------------
    # Elevated risk
    # --------------------------------------------------------------

    if risk >= 0.15:

        return "MANUAL_REVIEW"

    # --------------------------------------------------------------
    # Moderate / low confidence
    # --------------------------------------------------------------

    return "MANUAL_REVIEW"


integrated["final_policy_decision"] = (
    integrated.apply(
        policy_router,
        axis=1
    )
)


print(
    integrated["final_policy_decision"]
    .value_counts()
)


# ======================================================================
# 13. EXPLANATION ENGINE
# ======================================================================

section("[12] Generating applicant explanations")


def generate_explanation(row):

    positive = []
    concerns = []
    limitations = []

    # --------------------------------------------------------------
    # Payment consistency
    # --------------------------------------------------------------

    payment = row.get(
        "payment_success_rate",
        np.nan
    )

    if not pd.isna(payment):

        if payment >= 0.90:

            positive.append(
                "Strong payment consistency"
            )

        elif payment < 0.80:

            concerns.append(
                "Payment consistency is relatively weak"
            )

    # --------------------------------------------------------------
    # Income stability
    # --------------------------------------------------------------

    income_cv = row.get(
        "income_cv",
        np.nan
    )

    if not pd.isna(income_cv):

        if income_cv < 0.20:

            positive.append(
                "Income stability"
            )

        elif income_cv > 0.35:

            concerns.append(
                "Income volatility is relatively high"
            )

    # --------------------------------------------------------------
    # Cash-flow stability
    # --------------------------------------------------------------

    cashflow_cv = row.get(
        "cashflow_cv",
        np.nan
    )

    if not pd.isna(cashflow_cv):

        if cashflow_cv < 0.30:

            positive.append(
                "Stable cash flow"
            )

        elif cashflow_cv > 0.50:

            concerns.append(
                "Cash-flow variability is relatively high"
            )

    # --------------------------------------------------------------
    # Cash buffer
    # --------------------------------------------------------------

    balance_min = row.get(
        "balance_min",
        np.nan
    )

    if not pd.isna(balance_min):

        if balance_min > 30000:

            positive.append(
                "Strong minimum cash buffer"
            )

        elif balance_min < 10000:

            concerns.append(
                "Low minimum cash buffer"
            )

    # --------------------------------------------------------------
    # Income trend
    # --------------------------------------------------------------

    trend = row.get(
        "income_trend",
        np.nan
    )

    if not pd.isna(trend):

        if trend > 0.02:

            positive.append(
                "Positive income trend"
            )

        elif trend < -0.02:

            concerns.append(
                "Negative income trend"
            )

    # --------------------------------------------------------------
    # Inflow / outflow
    # --------------------------------------------------------------

    ratio = row.get(
        "inflow_to_outflow_ratio",
        np.nan
    )

    if not pd.isna(ratio):

        if ratio >= 1.30:

            positive.append(
                "Healthy inflow-to-outflow coverage"
            )

        elif ratio < 1.10:

            concerns.append(
                "Limited inflow-to-outflow coverage"
            )

    # --------------------------------------------------------------
    # Evidence limitations
    # --------------------------------------------------------------

    if row["final_history_depth"] in [
        "VERY_THIN",
        "THIN"
    ]:

        limitations.append(
            "Limited behavioral history"
        )

    if row["final_completeness"] < 0.80:

        limitations.append(
            "Missing periods in available history"
        )

    if row["final_confidence"] == "LOW":

        limitations.append(
            "Low evidence confidence"
        )

    if not limitations:

        limitations.append(
            "No major evidence limitation identified"
        )

    if not positive:

        positive.append(
            "No major positive behavioral signal identified"
        )

    if not concerns:

        concerns.append(
            "No major adverse behavioral signal identified"
        )

    return (
        " | ".join(positive),
        " | ".join(concerns),
        " | ".join(limitations)
    )


explanations = integrated.apply(
    generate_explanation,
    axis=1,
    result_type="expand"
)

explanations.columns = [
    "positive_factors",
    "risk_factors",
    "evidence_limitations"
]

integrated = pd.concat(
    [
        integrated,
        explanations
    ],
    axis=1
)


# ======================================================================
# 14. CONSENT STATUS
# ======================================================================

section("[13] Consent governance")

if not consent.empty:

    print(
        "Consent records loaded:",
        len(consent)
    )

    # Try to identify status column.

    consent_status_column = None

    for candidate in [
        "status",
        "consent_status",
        "Status"
    ]:

        if candidate in consent.columns:

            consent_status_column = candidate
            break

    if consent_status_column:

        statuses = (
            consent[consent_status_column]
            .astype(str)
            .str.upper()
        )

        # Prototype dataset contains consent records,
        # rather than necessarily one record per applicant.

        if "WITHDRAWN" in statuses.values:

            print(
                "Consent withdrawal records detected."
            )

        integrated["consent_governance_status"] = (
            "CONSENT_WORKFLOW_DEMONSTRATED"
        )

    else:

        integrated["consent_governance_status"] = (
            "CONSENT_WORKFLOW_DEMONSTRATED"
        )

else:

    integrated["consent_governance_status"] = (
        "CONSENT_RECORD_NOT_LINKED"
    )


# ======================================================================
# 15. PROVENANCE
# ======================================================================

section("[14] Model and data provenance")

provenance_status = (
    "PROTOTYPE"
)

if os.path.exists(PROVENANCE_FILE):

    try:

        with open(
            PROVENANCE_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            provenance = json.load(f)

        if isinstance(provenance, dict):

            provenance_status = (
                "PROVENANCE_REGISTERED"
            )

    except Exception as exc:

        print(
            "Warning: provenance file could not be parsed:",
            exc
        )

integrated["provenance_status"] = (
    provenance_status
)

integrated["model_version"] = MODEL_VERSION
integrated["policy_version"] = POLICY_VERSION
integrated["engine_version"] = ENGINE_VERSION


# ======================================================================
# 16. FINAL ASSESSMENT ID
# ======================================================================

section("[15] Creating assessment records")

integrated["assessment_id"] = [
    f"KVC-{uuid.uuid4().hex[:10].upper()}"
    for _ in range(len(integrated))
]

integrated["assessment_timestamp"] = (
    datetime.now().isoformat()
)


# ======================================================================
# 17. SELECT FINAL OUTPUT
# ======================================================================

final_columns = [
    "assessment_id",
    "applicant_id",

    # Evidence
    "history_months",
    "available_months",
    "final_completeness",
    "final_history_depth",
    "final_evidence_quality",
    "final_confidence",

    # Behavioral
    "behavioral_stability",

    # Risk
    "risk_proxy",
    "risk_band",

    # Policy
    "final_policy_decision",

    # Explanation
    "positive_factors",
    "risk_factors",
    "evidence_limitations",

    # Governance
    "consent_governance_status",
    "provenance_status",
    "model_version",
    "policy_version",
    "engine_version",
    "assessment_timestamp"
]


available_final_columns = [
    column
    for column in final_columns
    if column in integrated.columns
]

final_output = integrated[
    available_final_columns
].copy()


# ======================================================================
# 18. SANITY CHECKS
# ======================================================================

section("[16] Running final sanity checks")

print(
    "Final output shape:",
    final_output.shape
)


if final_output["applicant_id"].duplicated().any():

    raise ValueError(
        "Duplicate applicant IDs in final output."
    )


if final_output["risk_proxy"].isna().any():

    raise ValueError(
        "Missing risk proxy values."
    )


if final_output["final_evidence_quality"].isna().any():

    raise ValueError(
        "Missing evidence quality values."
    )


if final_output["final_confidence"].isna().any():

    raise ValueError(
        "Missing confidence values."
    )


if final_output["final_policy_decision"].isna().any():

    raise ValueError(
        "Missing policy decisions."
    )


print(
    "Duplicate applicant IDs: 0"
)

print(
    "Missing risk values: 0"
)

print(
    "Missing evidence values: 0"
)

print(
    "Missing confidence values: 0"
)

print(
    "Missing policy decisions: 0"
)


# ======================================================================
# 19. SUMMARY
# ======================================================================

section("[17] Integrated Kavach summary")

print()
print("Applicants:", len(final_output))

print()
print("Risk bands:")
print(
    final_output[
        "risk_band"
    ].value_counts()
)

print()
print("Confidence:")
print(
    final_output[
        "final_confidence"
    ].value_counts()
)

print()
print("Policy decisions:")
print(
    final_output[
        "final_policy_decision"
    ].value_counts()
)

print()
print("History depth:")
print(
    final_output[
        "final_history_depth"
    ].value_counts()
)


# ======================================================================
# 20. AUDIT LOG
# ======================================================================

audit_rows = []

for _, row in final_output.iterrows():

    audit_rows.append(
        {
            "assessment_id":
                row["assessment_id"],

            "applicant_id":
                row["applicant_id"],

            "event":
                "INTEGRATED_ASSESSMENT",

            "risk_proxy":
                row["risk_proxy"],

            "risk_band":
                row["risk_band"],

            "evidence_quality":
                row["final_evidence_quality"],

            "confidence":
                row["final_confidence"],

            "policy_decision":
                row["final_policy_decision"],

            "model_version":
                row["model_version"],

            "policy_version":
                row["policy_version"],

            "timestamp":
                row["assessment_timestamp"]
        }
    )


audit = pd.DataFrame(
    audit_rows
)


# ======================================================================
# 21. SAVE OUTPUTS
# ======================================================================

section("[18] Saving integrated outputs")

final_output.to_csv(
    OUTPUT_FILE,
    index=False
)

audit.to_csv(
    AUDIT_FILE,
    index=False
)


summary = {

    "engine": "Kavach Integrated Decision Engine",

    "engine_version":
        ENGINE_VERSION,

    "model_version":
        MODEL_VERSION,

    "policy_version":
        POLICY_VERSION,

    "applicants":
        int(len(final_output)),

    "risk_band_distribution":
        {
            str(k): int(v)
            for k, v in
            final_output[
                "risk_band"
            ].value_counts().items()
        },

    "confidence_distribution":
        {
            str(k): int(v)
            for k, v in
            final_output[
                "final_confidence"
            ].value_counts().items()
        },

    "policy_distribution":
        {
            str(k): int(v)
            for k, v in
            final_output[
                "final_policy_decision"
            ].value_counts().items()
        },

    "history_depth_distribution":
        {
            str(k): int(v)
            for k, v in
            final_output[
                "final_history_depth"
            ].value_counts().items()
        },

    "mean_risk_proxy":
        safe_round(
            final_output[
                "risk_proxy"
            ].mean(),
            6
        ),

    "mean_evidence_quality":
        safe_round(
            final_output[
                "final_evidence_quality"
            ].mean(),
            3
        ),

    "mean_behavioral_stability":
        safe_round(
            final_output[
                "behavioral_stability"
            ].mean(),
            3
        ),

    "prototype_warning":
        (
            "This output is a technical/conceptual "
            "prototype using synthetic behavioral "
            "data and illustrative risk proxies."
        )
}


with open(
    SUMMARY_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        summary,
        f,
        indent=2
    )


print()
print("Saved:")
print(f"  {OUTPUT_FILE}")
print(f"  {AUDIT_FILE}")
print(f"  {SUMMARY_FILE}")


# ======================================================================
# 22. SHOW EXAMPLES
# ======================================================================

section("[19] Example Kavach assessments")

display_columns = [
    "applicant_id",
    "final_history_depth",
    "final_evidence_quality",
    "final_confidence",
    "behavioral_stability",
    "risk_proxy",
    "risk_band",
    "final_policy_decision"
]

display_columns = [
    column
    for column in display_columns
    if column in final_output.columns
]

print(
    final_output[
        display_columns
    ]
    .head(10)
    .to_string(index=False)
)


# ======================================================================
# 23. METHODOLOGY STATEMENT
# ======================================================================

section("METHODOLOGY WARNING")

print(
"""
The integrated Kavach engine combines outputs from
previous prototype experiments.

The following limitations remain:

1. Behavioral histories are synthetic.

2. The risk proxy is NOT a calibrated probability
   of default.

3. Policy thresholds are prototype assumptions.

4. Evidence-quality thresholds are not validated
   credit-risk thresholds.

5. The system has not been validated on real
   target-population behavioral data.

6. No production lending decision should be made
   from this output.

7. The Home Credit benchmark is useful for
   methodological benchmarking but does not
   represent Kavach's intended target population.

8. Production implementation requires:

   - Real consented behavioral histories
   - Observed repayment outcomes
   - Out-of-time validation
   - Probability calibration
   - Population stability monitoring
   - Fairness testing
   - Cost-sensitive policy optimization
   - Human-review governance
   - Data governance
   - Model governance
   - Lender integration
   - Legal and regulatory review

The architectural principle demonstrated by this
engine is:

        EVIDENCE
            ↓
        CONFIDENCE
            ↓
          RISK
            ↓
         POLICY
            ↓
       EXPLANATION
            ↓
        GOVERNANCE

Importantly:

        RISK != CONFIDENCE

A risk estimate without sufficient evidence should
not automatically be treated as equivalent to the
same risk estimate supported by strong evidence.
"""
)

print()
print("=" * 70)
print("KAVACH INTEGRATED DECISION ENGINE COMPLETE")
print("=" * 70)
