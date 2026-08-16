"""
======================================================================
KAVACH PULSE — RISK × CONFIDENCE POLICY MATRIX
======================================================================

Version: 27.0

Purpose
-------
Demonstrate the core Kavach decision principle:

        RISK != CONFIDENCE

A risk estimate should not be interpreted independently
of the quality and depth of supporting evidence.

IMPORTANT
---------
This is a prototype policy demonstration.

Risk proxy is NOT calibrated PD.
Policy thresholds are NOT lender-approved thresholds.
Synthetic behavioral data is NOT real borrower data.
======================================================================
"""

import streamlit as st
import requests
import pandas as pd


# =====================================================================
# CONFIG
# =====================================================================

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Kavach — Risk × Confidence",
    page_icon="🛡️",
    layout="wide"
)


# =====================================================================
# CSS
# =====================================================================

st.markdown(
    """
    <style>

    .title {
        font-size: 38px;
        font-weight: 800;
        margin-bottom: 0;
    }

    .subtitle {
        color: #6b7280;
        font-size: 16px;
        margin-bottom: 20px;
    }

    .matrix-cell {
        padding: 25px;
        border-radius: 12px;
        border: 1px solid #d1d5db;
        text-align: center;
        margin: 5px;
    }

    .high-risk {
        background: #fee2e2;
    }

    .medium-risk {
        background: #fef3c7;
    }

    .low-risk {
        background: #dcfce7;
    }

    .low-confidence {
        background: #f3f4f6;
    }

    .principle {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        padding: 20px;
        border-radius: 14px;
        font-size: 18px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =====================================================================
# HEADER
# =====================================================================

st.markdown(
    '<div class="title">🛡️ KAVACH PULSE</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Risk × Confidence Decision Framework'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# =====================================================================
# CORE PRINCIPLE
# =====================================================================

st.markdown(
    """
    <div class="principle">

    <b>Core Kavach Principle</b><br><br>

    Risk and confidence are separate dimensions.

    A low-risk estimate supported by weak evidence should
    not automatically receive the same treatment as a
    low-risk estimate supported by strong evidence.

    </div>
    """,
    unsafe_allow_html=True
)


# =====================================================================
# LOAD INTEGRATED DATA
# =====================================================================

try:

    data = pd.read_csv(
        "kavach_integrated_decision_output.csv"
    )

except Exception as e:

    st.error(
        f"Could not load integrated dataset: {e}"
    )

    st.stop()


# =====================================================================
# COLUMN DETECTION
# =====================================================================

def find_column(candidates):

    for column in candidates:

        if column in data.columns:
            return column

    return None


ID_COL = find_column([
    "applicant_id"
])

RISK_COL = find_column([
    "risk_proxy"
])

RISK_BAND_COL = find_column([
    "risk_band"
])

CONFIDENCE_COL = find_column([
    "final_confidence"
])

EVIDENCE_COL = find_column([
    "final_evidence_quality"
])

HISTORY_COL = find_column([
    "final_history_depth"
])

POLICY_COL = find_column([
    "final_policy_decision"
])


required = [
    ID_COL,
    RISK_COL,
    RISK_BAND_COL,
    CONFIDENCE_COL,
    EVIDENCE_COL,
    HISTORY_COL,
    POLICY_COL
]


if any(x is None for x in required):

    st.error(
        "Required columns are missing from the integrated dataset."
    )

    st.stop()


# =====================================================================
# APPLICANT SELECTOR
# =====================================================================

st.markdown(
    "## Applicant Analysis"
)

selected_id = st.number_input(
    "Applicant ID",
    min_value=int(data[ID_COL].min()),
    max_value=int(data[ID_COL].max()),
    value=0,
    step=1
)


applicant = data[
    data[ID_COL] == selected_id
]


if applicant.empty:

    st.error(
        "Applicant not found."
    )

    st.stop()


row = applicant.iloc[0]


risk = float(
    row[RISK_COL]
)

risk_band = str(
    row[RISK_BAND_COL]
)

confidence = str(
    row[CONFIDENCE_COL]
)

evidence = float(
    row[EVIDENCE_COL]
)

history = str(
    row[HISTORY_COL]
)

policy = str(
    row[POLICY_COL]
)


# =====================================================================
# APPLICANT METRICS
# =====================================================================

c1, c2, c3, c4 = st.columns(4)


with c1:

    st.metric(
        "Risk Proxy",
        f"{risk * 100:.1f}%"
    )


with c2:

    st.metric(
        "Risk Band",
        risk_band
    )


with c3:

    st.metric(
        "Confidence",
        confidence
    )


with c4:

    st.metric(
        "Evidence Quality",
        f"{evidence:.1f}/100"
    )


st.info(
    f"History depth: **{history}**"
)


# =====================================================================
# DECISION INTERPRETATION
# =====================================================================

st.markdown(
    "## Decision Interpretation"
)


if risk_band == "LOW":

    if confidence == "HIGH":

        interpretation = (
            "Low risk + strong evidence. "
            "The prototype has comparatively strong support "
            "for its assessment."
        )

    elif confidence == "MEDIUM":

        interpretation = (
            "Low risk + moderate evidence. "
            "The assessment should be interpreted with caution."
        )

    else:

        interpretation = (
            "Low risk + weak evidence. "
            "The low-risk result should NOT be treated as "
            "equivalent to a well-supported low-risk result."
        )


elif risk_band == "MODERATE":

    if confidence == "HIGH":

        interpretation = (
            "Moderate risk + strong evidence. "
            "The signal is relatively well supported."
        )

    else:

        interpretation = (
            "Moderate risk + limited evidence. "
            "Additional review may be appropriate."
        )


elif risk_band == "ELEVATED":

    if confidence == "HIGH":

        interpretation = (
            "Elevated risk + strong evidence. "
            "The risk signal is relatively well supported."
        )

    else:

        interpretation = (
            "Elevated risk + limited evidence. "
            "The system should distinguish risk uncertainty "
            "from the risk estimate itself."
        )


else:

    interpretation = (
        "High risk signal. "
        "Review the supporting evidence before interpreting "
        "the result."
    )


st.warning(
    interpretation
)


# =====================================================================
# MATRIX
# =====================================================================

st.markdown(
    "## Risk × Confidence Matrix"
)


matrix = pd.DataFrame(
    [
        ["LOW", "HIGH", "Strongly supported low-risk signal"],
        ["LOW", "MEDIUM", "Low risk with moderate evidence"],
        ["LOW", "LOW", "Low risk but insufficient support"],
        ["MODERATE", "HIGH", "Moderate risk with strong evidence"],
        ["MODERATE", "MEDIUM", "Moderate risk requiring caution"],
        ["MODERATE", "LOW", "Moderate risk with weak support"],
        ["ELEVATED", "HIGH", "Elevated risk strongly supported"],
        ["ELEVATED", "MEDIUM", "Elevated risk requiring review"],
        ["ELEVATED", "LOW", "Elevated risk with weak evidence"],
        ["HIGH", "HIGH", "High-risk signal strongly supported"],
        ["HIGH", "MEDIUM", "High-risk signal requiring review"],
        ["HIGH", "LOW", "High-risk signal with weak evidence"],
    ],
    columns=[
        "Risk",
        "Confidence",
        "Interpretation"
    ]
)


st.dataframe(
    matrix,
    use_container_width=True,
    hide_index=True
)


# =====================================================================
# CURRENT APPLICANT POSITION
# =====================================================================

st.markdown(
    "## Current Applicant Position"
)


current_matrix = pd.DataFrame(
    {
        "Dimension": [
            "Risk",
            "Confidence",
            "Evidence Quality",
            "History Depth",
            "Policy"
        ],
        "Value": [
            risk_band,
            confidence,
            f"{evidence:.1f}/100",
            history,
            policy
        ]
    }
)


st.dataframe(
    current_matrix,
    use_container_width=True,
    hide_index=True
)


# =====================================================================
# POPULATION DISTRIBUTION
# =====================================================================

st.markdown(
    "## Population Risk × Confidence Distribution"
)


distribution = (
    data
    .groupby(
        [
            RISK_BAND_COL,
            CONFIDENCE_COL
        ]
    )
    .size()
    .reset_index(
        name="Applicants"
    )
)


pivot = distribution.pivot(
    index=RISK_BAND_COL,
    columns=CONFIDENCE_COL,
    values="Applicants"
).fillna(0)


st.dataframe(
    pivot,
    use_container_width=True
)


# =====================================================================
# HISTORY DEPTH ANALYSIS
# =====================================================================

st.markdown(
    "## Evidence Depth vs Confidence"
)


depth_distribution = (
    data
    .groupby(
        [
            HISTORY_COL,
            CONFIDENCE_COL
        ]
    )
    .size()
    .reset_index(
        name="Applicants"
    )
)


st.dataframe(
    depth_distribution,
    use_container_width=True,
    hide_index=True
)


# =====================================================================
# POLICY DISTRIBUTION
# =====================================================================

st.markdown(
    "## Policy Routing Distribution"
)


policy_distribution = (
    data[POLICY_COL]
    .value_counts()
    .rename_axis("Policy Decision")
    .reset_index(
        name="Applicants"
    )
)


st.bar_chart(
    policy_distribution.set_index(
        "Policy Decision"
    )
)


# =====================================================================
# GOVERNANCE WARNING
# =====================================================================

st.divider()

st.markdown(
    """
    ### ⚠️ Governance Notice

    This matrix is a **prototype decision framework**.

    It does not establish:

    - a calibrated probability of default
    - lender-approved thresholds
    - regulatory requirements
    - legal compliance
    - production credit policy

    The key architectural distinction is:

    **RISK ≠ CONFIDENCE**

    Risk describes the estimated level of concern.

    Confidence describes how strongly the available evidence
    supports the assessment.

    These dimensions should be evaluated separately.
    """
)


st.caption(
    "Kavach Pulse — Prototype v27.0"
)
