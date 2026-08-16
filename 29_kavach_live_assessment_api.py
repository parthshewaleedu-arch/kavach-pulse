"""
======================================================================
KAVACH PULSE — LIVE ASSESSMENT API
======================================================================

Version: 29.0

Purpose
-------
Accept applicant evidence directly and generate a live Kavach
prototype assessment.

FLOW:

Applicant Input
      ↓
Evidence Quality
      ↓
Behavioral Stability
      ↓
Illustrative Risk Proxy
      ↓
Risk Band
      ↓
Risk × Confidence Policy
      ↓
Explanation
      ↓
Assessment Response

IMPORTANT
---------
This is a technical prototype.

The risk proxy is NOT a calibrated probability of default.
The thresholds are NOT production lending thresholds.
The inputs are demonstration values.
======================================================================
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime, timezone
import math
import uuid
import os

# =====================================================================
# APP
# =====================================================================

app = FastAPI(
    title="Kavach Pulse — Live Assessment API",
    description="Prototype evidence-aware credit assessment API",
    version="29.0"
)


MODEL_VERSION = "KAVACH-PROTOTYPE-v2"

POLICY_VERSION = "KAVACH-POLICY-PROTOTYPE-v2"


# =====================================================================
# REQUEST SCHEMA
# =====================================================================

class AssessmentRequest(BaseModel):

    applicant_id: int = Field(
        ge=0,
        description="Synthetic prototype applicant ID"
    )

    history_months: int = Field(
        ge=1,
        le=12
    )

    available_months: int = Field(
        ge=1,
        le=12
    )

    source_count: int = Field(
        ge=1,
        le=3
    )

    payment_success_rate: float = Field(
        ge=0.0,
        le=1.0
    )

    income_cv: float = Field(
        ge=0.0,
        le=1.0
    )

    cashflow_cv: float = Field(
        ge=0.0,
        le=2.0
    )

    balance_min: float = Field(
        ge=0.0
    )

    inflow_to_outflow_ratio: float = Field(
        ge=0.0,
        le=5.0
    )

    income_trend: float = Field(
        ge=-1.0,
        le=1.0
    )

    consent_granted: bool


# =====================================================================
# RESPONSE SCHEMA
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

    behavioral_stability: float

    policy_decision: str

    positive_factors: List[str]

    risk_factors: List[str]

    evidence_limitations: List[str]

    model_version: str

    policy_version: str

    generated_at: str


# =====================================================================
# UTILITY
# =====================================================================

def clip(
    value: float,
    minimum: float,
    maximum: float
) -> float:

    return max(
        minimum,
        min(
            maximum,
            value
        )
    )


# =====================================================================
# HISTORY DEPTH
# =====================================================================

def calculate_history_depth(
    history_months: int,
    available_months: int
) -> str:

    completeness = (
        available_months
        / history_months
    )

    if history_months <= 2:

        return "VERY_THIN"

    if history_months <= 4:

        return "THIN"

    if history_months <= 8:

        return "DEVELOPING"

    if history_months <= 11:

        return "STRONG"

    return "ESTABLISHED"


# =====================================================================
# EVIDENCE QUALITY
# =====================================================================

def calculate_evidence_quality(
    history_months: int,
    available_months: int,
    source_count: int
) -> float:

    completeness = (
        available_months
        /
        history_months
    )

    history_score = (
        history_months
        /
        12
    )

    source_score = (
        source_count
        /
        3
    )

    score = (
        45
        * completeness
        +
        30
        * history_score
        +
        25
        * source_score
    )

    return round(
        clip(
            score,
            0,
            100
        ),
        2
    )


# =====================================================================
# CONFIDENCE
# =====================================================================

def calculate_confidence(
    evidence_quality: float,
    history_months: int,
    available_months: int
) -> str:

    completeness = (
        available_months
        /
        history_months
    )

    if (
        evidence_quality < 70
        or
        history_months <= 2
        or
        completeness < 0.60
    ):

        return "LOW"

    if (
        evidence_quality >= 82
        and
        history_months >= 6
        and
        completeness >= 0.80
    ):

        return "HIGH"

    return "MEDIUM"


# =====================================================================
# BEHAVIOURAL STABILITY
# =====================================================================

def calculate_behavioral_stability(
    payment_success_rate: float,
    income_cv: float,
    cashflow_cv: float,
    balance_min: float,
    inflow_to_outflow_ratio: float,
    income_trend: float
) -> float:

    payment_component = (
        payment_success_rate
        * 30
    )

    income_stability = (
        1
        -
        clip(
            income_cv,
            0,
            0.60
        )
        /
        0.60
    )

    income_component = (
        income_stability
        * 15
    )

    cashflow_stability = (
        1
        -
        clip(
            cashflow_cv,
            0,
            1.00
        )
    )

    cashflow_component = (
        cashflow_stability
        * 15
    )

    balance_component = (
        clip(
            balance_min
            /
            50000,
            0,
            1
        )
        * 15
    )

    coverage_component = (
        clip(
            (
                inflow_to_outflow_ratio
                -
                0.8
            )
            /
            1.2,
            0,
            1
        )
        * 15
    )

    trend_component = (
        clip(
            (
                income_trend
                +
                0.20
            )
            /
            0.40,
            0,
            1
        )
        * 10
    )

    score = (
        payment_component
        +
        income_component
        +
        cashflow_component
        +
        balance_component
        +
        coverage_component
        +
        trend_component
    )

    return round(
        clip(
            score,
            0,
            100
        ),
        2
    )


# =====================================================================
# RISK PROXY
# =====================================================================

def calculate_risk_proxy(
    behavioral_stability: float
) -> float:

    """
    Illustrative monotonic transformation.

    This is NOT PD calibration.
    """

    normalized = (
        behavioral_stability
        /
        100
    )

    risk = (
        0.20
        -
        (
            normalized
            *
            0.17
        )
    )

    return round(
        clip(
            risk,
            0.02,
            0.20
        ),
        6
    )


# =====================================================================
# RISK BAND
# =====================================================================

def calculate_risk_band(
    risk_proxy: float
) -> str:

    if risk_proxy >= 0.17:

        return "HIGH"

    if risk_proxy >= 0.11:

        return "ELEVATED"

    if risk_proxy >= 0.07:

        return "MODERATE"

    return "LOW"


# =====================================================================
# POLICY ENGINE
# =====================================================================

def calculate_policy(
    risk_band: str,
    confidence: str
) -> str:

    # Insufficient evidence always wins.

    if confidence == "LOW":

        return "INSUFFICIENT_EVIDENCE"


    if risk_band == "HIGH":

        return "DECLINE_OR_REVIEW"


    if risk_band == "ELEVATED":

        return "MANUAL_REVIEW"


    if risk_band == "MODERATE":

        return "PASS_TO_LENDER_POLICY"


    if risk_band == "LOW":

        return "PASS_TO_LENDER_POLICY"


    return "MANUAL_REVIEW"


# =====================================================================
# EXPLANATION ENGINE
# =====================================================================

def generate_explanation(
    payment_success_rate: float,
    income_cv: float,
    cashflow_cv: float,
    balance_min: float,
    inflow_to_outflow_ratio: float,
    income_trend: float,
    history_months: int,
    available_months: int,
    source_count: int
):

    positive = []

    risks = []

    limitations = []


    # ---------------------------------------------------------------
    # PAYMENT
    # ---------------------------------------------------------------

    if payment_success_rate >= 0.95:

        positive.append(
            "Strong payment consistency"
        )

    elif payment_success_rate < 0.80:

        risks.append(
            "Payment consistency is relatively weak"
        )


    # ---------------------------------------------------------------
    # INCOME STABILITY
    # ---------------------------------------------------------------

    if income_cv <= 0.15:

        positive.append(
            "Income volatility is relatively low"
        )

    elif income_cv >= 0.30:

        risks.append(
            "Income volatility is relatively high"
        )


    # ---------------------------------------------------------------
    # CASH FLOW
    # ---------------------------------------------------------------

    if cashflow_cv <= 0.25:

        positive.append(
            "Cash-flow behaviour is relatively stable"
        )

    elif cashflow_cv >= 0.50:

        risks.append(
            "Cash-flow variability is relatively high"
        )


    # ---------------------------------------------------------------
    # BALANCE
    # ---------------------------------------------------------------

    if balance_min >= 30000:

        positive.append(
            "Strong minimum cash buffer"
        )

    elif balance_min < 10000:

        risks.append(
            "Low minimum cash buffer"
        )


    # ---------------------------------------------------------------
    # COVERAGE
    # ---------------------------------------------------------------

    if inflow_to_outflow_ratio >= 1.40:

        positive.append(
            "Healthy inflow-to-outflow coverage"
        )

    elif inflow_to_outflow_ratio < 1.10:

        risks.append(
            "Limited inflow-to-outflow coverage"
        )


    # ---------------------------------------------------------------
    # TREND
    # ---------------------------------------------------------------

    if income_trend >= 0.03:

        positive.append(
            "Positive income trend"
        )

    elif income_trend <= -0.03:

        risks.append(
            "Negative income trend"
        )


    # ---------------------------------------------------------------
    # EVIDENCE
    # ---------------------------------------------------------------

    completeness = (
        available_months
        /
        history_months
    )

    if history_months <= 2:

        limitations.append(
            "Very limited financial history"
        )

    elif history_months <= 4:

        limitations.append(
            "Limited financial history"
        )


    if completeness < 0.80:

        limitations.append(
            "Some requested history is unavailable"
        )


    if source_count < 3:

        limitations.append(
            "Not all requested data sources are available"
        )


    if not positive:

        positive.append(
            "No major positive behavioural signal identified"
        )


    if not risks:

        risks.append(
            "No major adverse behavioural signal identified"
        )


    if not limitations:

        limitations.append(
            "No major evidence limitation identified"
        )


    return (
        positive,
        risks,
        limitations
    )


# =====================================================================
# HEALTH
# =====================================================================

@app.get("/health")
def health():

    return {

        "status": "healthy",

        "engine_version": "29.0",

        "model_version":
            MODEL_VERSION,

        "policy_version":
            POLICY_VERSION,

        "mode":
            "LIVE_PROTOTYPE"
    }


# =====================================================================
# ASSESSMENT
# =====================================================================

@app.post(
    "/assess",
    response_model=AssessmentResponse
)
def assess(
    request: AssessmentRequest
):

    # ---------------------------------------------------------------
    # CONSENT
    # ---------------------------------------------------------------

    if not request.consent_granted:

        raise HTTPException(
            status_code=403,
            detail={
                "error":
                    "CONSENT_REQUIRED",

                "message":
                    "Assessment cannot continue without consent."
            }
        )


    # ---------------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------------

    if (
        request.available_months
        >
        request.history_months
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "available_months cannot exceed "
                "history_months"
            )
        )


    # ---------------------------------------------------------------
    # EVIDENCE
    # ---------------------------------------------------------------

    evidence_quality = calculate_evidence_quality(
        request.history_months,
        request.available_months,
        request.source_count
    )


    confidence = calculate_confidence(
        evidence_quality,
        request.history_months,
        request.available_months
    )


    history_depth = calculate_history_depth(
        request.history_months,
        request.available_months
    )


    # ---------------------------------------------------------------
    # BEHAVIOURAL STABILITY
    # ---------------------------------------------------------------

    behavioral_stability = (
        calculate_behavioral_stability(
            request.payment_success_rate,
            request.income_cv,
            request.cashflow_cv,
            request.balance_min,
            request.inflow_to_outflow_ratio,
            request.income_trend
        )
    )


    # ---------------------------------------------------------------
    # RISK
    # ---------------------------------------------------------------

    risk_proxy = calculate_risk_proxy(
        behavioral_stability
    )


    risk_band = calculate_risk_band(
        risk_proxy
    )


    # ---------------------------------------------------------------
    # POLICY
    # ---------------------------------------------------------------

    policy_decision = calculate_policy(
        risk_band,
        confidence
    )


    # ---------------------------------------------------------------
    # EXPLANATION
    # ---------------------------------------------------------------

    (
        positive_factors,
        risk_factors,
        evidence_limitations
    ) = generate_explanation(

        request.payment_success_rate,

        request.income_cv,

        request.cashflow_cv,

        request.balance_min,

        request.inflow_to_outflow_ratio,

        request.income_trend,

        request.history_months,

        request.available_months,

        request.source_count
    )


    # ---------------------------------------------------------------
    # RESPONSE
    # ---------------------------------------------------------------

    assessment_id = (
        "KVC-"
        +
        uuid.uuid4()
        .hex[:12]
        .upper()
    )


    generated_at = (
        datetime.now(
            timezone.utc
        )
        .isoformat()
    )


    return AssessmentResponse(

        assessment_id=assessment_id,

        applicant_id=
            request.applicant_id,

        risk_proxy=
            risk_proxy,

        risk_proxy_percent=
            round(
                risk_proxy * 100,
                2
            ),

        risk_band=
            risk_band,

        evidence_quality=
            evidence_quality,

        confidence=
            confidence,

        history_depth=
            history_depth,

        behavioral_stability=
            behavioral_stability,

        policy_decision=
            policy_decision,

        positive_factors=
            positive_factors,

        risk_factors=
            risk_factors,

        evidence_limitations=
            evidence_limitations,

        model_version=
            MODEL_VERSION,

        policy_version=
            POLICY_VERSION,

        generated_at=
            generated_at
    )


# =====================================================================
# ROOT
# =====================================================================

@app.get("/")
def root():

    return {

        "name":
            "Kavach Pulse",

        "engine":
            "Live Assessment API",

        "version":
            "29.0",

        "status":
            "prototype",

        "warning":
            "Risk proxy is not calibrated PD."
    }
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=False
    )
