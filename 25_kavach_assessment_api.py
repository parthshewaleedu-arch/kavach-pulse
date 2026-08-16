"""
======================================================================
KAVACH PULSE — ASSESSMENT API
======================================================================

Purpose
-------
Expose the integrated Kavach prototype through a simple REST API.

IMPORTANT
---------
This is a technical prototype.

It does NOT provide real credit decisions.
Risk values are prototype risk proxies.
Synthetic behavioral data must not be represented as real borrower data.
======================================================================
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
import pandas as pd
import numpy as np
import uuid
from datetime import datetime, timezone
import os


# =====================================================================
# CONFIGURATION
# =====================================================================

OUTPUT_FILE = "kavach_integrated_decision_output.csv"

APP_TITLE = "Kavach Pulse Assessment API"
APP_VERSION = "25.0"


# =====================================================================
# LOAD INTEGRATED DATA
# =====================================================================

print("=" * 70)
print("KAVACH PULSE — ASSESSMENT API")
print("=" * 70)

print("\n[1] Loading integrated Kavach dataset...")

if not os.path.exists(OUTPUT_FILE):
    raise FileNotFoundError(
        f"{OUTPUT_FILE} not found.\n"
        "Run 24_kavach_integrated_decision_engine.py first."
    )

df = pd.read_csv(OUTPUT_FILE)

print(f"Dataset: {df.shape}")


# =====================================================================
# IDENTIFY IMPORTANT COLUMNS
# =====================================================================

def find_column(candidates):
    for column in candidates:
        if column in df.columns:
            return column
    return None


ID_COL = find_column([
    "applicant_id",
    "SK_ID_CURR",
    "id"
])

RISK_COL = find_column([
    "risk_proxy",
    "pd_proxy",
    "pd_estimate",
    "illustrative_risk_score"
])

RISK_BAND_COL = find_column([
    "risk_band",
    "final_risk_band"
])

CONFIDENCE_COL = find_column([
    "final_confidence",
    "confidence",
    "confidence_band",
    "depth_confidence_band"
])

EVIDENCE_COL = find_column([
    "final_evidence_quality",
    "depth_adjusted_evidence_score",
    "evidence_quality_score"
])

POLICY_COL = find_column([
    "final_policy_decision",
    "policy_decision"
])

HISTORY_COL = find_column([
    "final_history_depth",
    "history_depth_band"
])

STABILITY_COL = find_column([
    "behavioral_stability",
    "behavioral_stability_score"
])


print("\n[2] Identified columns")

print(f"Applicant ID       : {ID_COL}")
print(f"Risk                : {RISK_COL}")
print(f"Risk band           : {RISK_BAND_COL}")
print(f"Confidence          : {CONFIDENCE_COL}")
print(f"Evidence quality    : {EVIDENCE_COL}")
print(f"Policy              : {POLICY_COL}")
print(f"History depth       : {HISTORY_COL}")
print(f"Behavioral stability: {STABILITY_COL}")


# =====================================================================
# VALIDATION
# =====================================================================

required_columns = {
    "Applicant ID": ID_COL,
    "Risk": RISK_COL,
    "Risk Band": RISK_BAND_COL,
    "Confidence": CONFIDENCE_COL,
    "Evidence Quality": EVIDENCE_COL,
    "Policy": POLICY_COL,
    "History Depth": HISTORY_COL,
}

missing = [
    name
    for name, column in required_columns.items()
    if column is None
]

if missing:
    raise ValueError(
        "Missing required columns: "
        + ", ".join(missing)
    )


# =====================================================================
# NORMALIZE DATA
# =====================================================================

df[ID_COL] = pd.to_numeric(
    df[ID_COL],
    errors="coerce"
)

df = df.dropna(
    subset=[ID_COL]
).copy()

df[ID_COL] = df[ID_COL].astype(int)

df = df.drop_duplicates(
    subset=[ID_COL]
)


# Create fast applicant lookup

applicant_lookup = {
    int(row[ID_COL]): row
    for _, row in df.iterrows()
}


print(f"\n[3] Applicant records loaded: {len(applicant_lookup)}")


# =====================================================================
# EXPLANATION ENGINE
# =====================================================================

def safe_float(value, default=0.0):
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def generate_explanation(row):

    positive = []
    concerns = []
    limitations = []

    # ---------------------------------------------------------------
    # Payment consistency
    # ---------------------------------------------------------------

    if "payment_success_rate" in row.index:

        value = safe_float(
            row["payment_success_rate"]
        )

        if value >= 0.95:
            positive.append(
                "Strong payment consistency"
            )

        elif value < 0.80:
            concerns.append(
                "Payment consistency is relatively weak"
            )


    # ---------------------------------------------------------------
    # Income stability
    # ---------------------------------------------------------------

    if "income_cv" in row.index:

        value = safe_float(
            row["income_cv"]
        )

        if value < 0.20:
            positive.append(
                "Income volatility is relatively low"
            )

        elif value > 0.35:
            concerns.append(
                "Income volatility is relatively high"
            )


    # ---------------------------------------------------------------
    # Cash-flow stability
    # ---------------------------------------------------------------

    if "cashflow_cv" in row.index:

        value = safe_float(
            row["cashflow_cv"]
        )

        if value < 0.30:
            positive.append(
                "Cash-flow behaviour is relatively stable"
            )

        elif value > 0.50:
            concerns.append(
                "Cash-flow variability is relatively high"
            )


    # ---------------------------------------------------------------
    # Cash buffer
    # ---------------------------------------------------------------

    if "balance_min" in row.index:

        value = safe_float(
            row["balance_min"]
        )

        if value > 30000:
            positive.append(
                "Strong minimum cash buffer"
            )

        elif value < 10000:
            concerns.append(
                "Low minimum cash buffer"
            )


    # ---------------------------------------------------------------
    # Inflow / outflow coverage
    # ---------------------------------------------------------------

    if "inflow_to_outflow_ratio" in row.index:

        value = safe_float(
            row["inflow_to_outflow_ratio"]
        )

        if value >= 1.40:
            positive.append(
                "Healthy inflow-to-outflow coverage"
            )

        elif value < 1.15:
            concerns.append(
                "Limited inflow-to-outflow coverage"
            )


    # ---------------------------------------------------------------
    # Income trend
    # ---------------------------------------------------------------

    if "income_trend" in row.index:

        value = safe_float(
            row["income_trend"]
        )

        if value > 0.01:
            positive.append(
                "Positive income trend"
            )

        elif value < -0.01:
            concerns.append(
                "Negative income trend"
            )


    # ---------------------------------------------------------------
    # Evidence limitations
    # ---------------------------------------------------------------

    evidence = safe_float(
        row[EVIDENCE_COL]
    )

    confidence = str(
        row[CONFIDENCE_COL]
    )

    history = str(
        row[HISTORY_COL]
    )

    if confidence == "LOW":
        limitations.append(
            "Evidence confidence is low"
        )

    if history in ["VERY_THIN", "THIN"]:
        limitations.append(
            "Limited historical evidence"
        )

    if evidence < 70:
        limitations.append(
            "Evidence quality is relatively low"
        )


    if not positive:
        positive.append(
            "No major positive behavioral signal identified"
        )

    if not concerns:
        concerns.append(
            "No major adverse behavioral signal identified"
        )

    if not limitations:
        limitations.append(
            "No major evidence limitation identified"
        )


    return {
        "positive_factors": positive[:5],
        "risk_factors": concerns[:5],
        "evidence_limitations": limitations[:5],
    }


# =====================================================================
# API
# =====================================================================

app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description=(
        "Kavach Pulse technical prototype assessment API. "
        "Outputs are illustrative and not production credit decisions."
    )
)


# =====================================================================
# RESPONSE MODEL
# =====================================================================

class AssessmentResponse(BaseModel):

    assessment_id: str

    applicant_id: int

    risk_proxy: float

    risk_proxy_percent: float

    risk_band: str

    evidence_quality: float

    confidence: str

    history_depth: str

    behavioral_stability: Optional[float] = None

    policy_decision: str

    positive_factors: List[str]

    risk_factors: List[str]

    evidence_limitations: List[str]

    model_version: str

    policy_version: str

    generated_at: str


# =====================================================================
# ROOT ENDPOINT
# =====================================================================

@app.get("/")
def root():

    return {
        "service": "Kavach Pulse Assessment API",
        "version": APP_VERSION,
        "status": "operational",
        "prototype": True,
        "warning": (
            "Outputs are prototype risk assessments and "
            "must not be used as production lending decisions."
        )
    }


# =====================================================================
# HEALTH ENDPOINT
# =====================================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "records_loaded": len(applicant_lookup),
        "model_version": "KAVACH-PROTOTYPE-v1",
        "policy_version": "KAVACH-POLICY-PROTOTYPE-v1"
    }


# =====================================================================
# ASSESSMENT ENDPOINT
# =====================================================================

@app.get(
    "/assessment/{applicant_id}",
    response_model=AssessmentResponse
)
def get_assessment(applicant_id: int):

    if applicant_id not in applicant_lookup:

        raise HTTPException(
            status_code=404,
            detail=f"Applicant {applicant_id} not found."
        )

    row = applicant_lookup[applicant_id]

    risk = safe_float(
        row[RISK_COL]
    )

    evidence = safe_float(
        row[EVIDENCE_COL]
    )

    stability = None

    if STABILITY_COL is not None:

        stability = safe_float(
            row[STABILITY_COL]
        )

    explanation = generate_explanation(row)

    return AssessmentResponse(

        assessment_id=
        "KVC-" +
        uuid.uuid4().hex[:12].upper(),

        applicant_id=applicant_id,

        risk_proxy=round(
            risk,
            6
        ),

        risk_proxy_percent=round(
            risk * 100,
            2
        ),

        risk_band=str(
            row[RISK_BAND_COL]
        ),

        evidence_quality=round(
            evidence,
            2
        ),

        confidence=str(
            row[CONFIDENCE_COL]
        ),

        history_depth=str(
            row[HISTORY_COL]
        ),

        behavioral_stability=(
            round(stability, 2)
            if stability is not None
            else None
        ),

        policy_decision=str(
            row[POLICY_COL]
        ),

        positive_factors=
        explanation[
            "positive_factors"
        ],

        risk_factors=
        explanation[
            "risk_factors"
        ],

        evidence_limitations=
        explanation[
            "evidence_limitations"
        ],

        model_version=
        "KAVACH-PROTOTYPE-v1",

        policy_version=
        "KAVACH-POLICY-PROTOTYPE-v1",

        generated_at=
        datetime.now(
            timezone.utc
        ).isoformat()
    )


# =====================================================================
# SUMMARY ENDPOINT
# =====================================================================

@app.get("/summary")
def summary():

    return {

        "applicants": len(df),

        "risk_bands":
            df[RISK_BAND_COL]
            .value_counts()
            .to_dict(),

        "confidence":
            df[CONFIDENCE_COL]
            .value_counts()
            .to_dict(),

        "policy_decisions":
            df[POLICY_COL]
            .value_counts()
            .to_dict(),

        "history_depth":
            df[HISTORY_COL]
            .value_counts()
            .to_dict(),

        "mean_risk_proxy":
            round(
                safe_float(
                    df[RISK_COL].mean()
                ),
                6
            ),

        "mean_evidence_quality":
            round(
                safe_float(
                    df[EVIDENCE_COL].mean()
                ),
                2
            ),

        "prototype": True
    }


# =====================================================================
# BATCH ASSESSMENT
# =====================================================================

class BatchRequest(BaseModel):

    applicant_ids: List[int] = Field(
        ...,
        min_length=1,
        max_length=100
    )


@app.post("/batch")
def batch_assessment(
    request: BatchRequest
):

    results = []

    for applicant_id in request.applicant_ids:

        if applicant_id not in applicant_lookup:
            continue

        row = applicant_lookup[applicant_id]

        risk = safe_float(
            row[RISK_COL]
        )

        evidence = safe_float(
            row[EVIDENCE_COL]
        )

        explanation = generate_explanation(
            row
        )

        stability = None

        if STABILITY_COL is not None:
            stability = safe_float(
                row[STABILITY_COL]
            )

        results.append({

            "applicant_id":
                applicant_id,

            "risk_proxy":
                round(risk, 6),

            "risk_proxy_percent":
                round(risk * 100, 2),

            "risk_band":
                str(row[RISK_BAND_COL]),

            "evidence_quality":
                round(evidence, 2),

            "confidence":
                str(row[CONFIDENCE_COL]),

            "history_depth":
                str(row[HISTORY_COL]),

            "behavioral_stability":
                (
                    round(stability, 2)
                    if stability is not None
                    else None
                ),

            "policy_decision":
                str(row[POLICY_COL]),

            "positive_factors":
                explanation[
                    "positive_factors"
                ],

            "risk_factors":
                explanation[
                    "risk_factors"
                ],

            "evidence_limitations":
                explanation[
                    "evidence_limitations"
                ]
        })

    return {
        "count": len(results),
        "results": results
    }


# =====================================================================
# STARTUP MESSAGE
# =====================================================================

print("\n" + "=" * 70)
print("API READY")
print("=" * 70)

print(
    "\nRun with:"
)

print(
    "uvicorn 25_kavach_assessment_api:app "
    "--host 127.0.0.1 --port 8000 --reload"
)

print(
    "\nSwagger UI:"
)

print(
    "http://127.0.0.1:8000/docs"
)

print("\nPrototype warning:")
print(
    "This API exposes prototype risk outputs."
)
print(
    "It is NOT a production lending decision system."
)

print("=" * 70)


# =====================================================================
# DIRECT EXECUTION
# =====================================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000
    )
