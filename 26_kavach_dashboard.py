"""
======================================================================
KAVACH PULSE — CREDIT ASSESSMENT DASHBOARD
======================================================================

Version: 26.0

This dashboard consumes the Kavach Assessment API.

IMPORTANT:
This is a technical/conceptual prototype.
Risk proxy is NOT a calibrated probability of default.
Synthetic behavioral data is NOT real borrower data.
======================================================================
"""

import streamlit as st
import requests
import pandas as pd
import numpy as np


# =====================================================================
# CONFIG
# =====================================================================

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Kavach Pulse",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =====================================================================
# CUSTOM CSS
# =====================================================================

st.markdown(
    """
    <style>

    .main {
        background-color: #f7f8fa;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .kavach-title {
        font-size: 42px;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 0;
    }

    .kavach-subtitle {
        font-size: 17px;
        color: #6b7280;
        margin-top: 0;
    }

    .metric-card {
        background: white;
        padding: 22px;
        border-radius: 14px;
        border: 1px solid #e5e7eb;
        min-height: 130px;
    }

    .metric-label {
        color: #6b7280;
        font-size: 14px;
        font-weight: 600;
    }

    .metric-value {
        font-size: 30px;
        font-weight: 800;
        margin-top: 8px;
    }

    .section-title {
        font-size: 22px;
        font-weight: 750;
        margin-top: 25px;
        margin-bottom: 12px;
    }

    .risk-box {
        padding: 20px;
        border-radius: 14px;
        background: white;
        border: 1px solid #e5e7eb;
        text-align: center;
    }

    .warning-box {
        padding: 16px;
        border-radius: 12px;
        background: #fff7ed;
        border: 1px solid #fed7aa;
    }

    .success-box {
        padding: 16px;
        border-radius: 12px;
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
    }

    .info-box {
        padding: 16px;
        border-radius: 12px;
        background: #eff6ff;
        border: 1px solid #bfdbfe;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =====================================================================
# HEADER
# =====================================================================

st.markdown(
    '<div class="kavach-title">🛡️ KAVACH PULSE</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="kavach-subtitle">'
    'Evidence-aware alternative credit assessment prototype'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# =====================================================================
# API HEALTH CHECK
# =====================================================================

try:

    health_response = requests.get(
        f"{API_URL}/health",
        timeout=3
    )

    api_online = health_response.status_code == 200

except Exception:

    api_online = False


if api_online:

    st.success(
        "● Kavach Assessment API is online"
    )

else:

    st.error(
        "● Kavach Assessment API is offline. "
        "Start Script 25 first."
    )

    st.code(
        "python 25_kavach_assessment_api.py"
    )

    st.stop()


# =====================================================================
# SIDEBAR
# =====================================================================

st.sidebar.title("KAVACH")

st.sidebar.markdown(
    "### Applicant Assessment"
)

applicant_id = st.sidebar.number_input(
    "Applicant ID",
    min_value=0,
    max_value=4999,
    value=0,
    step=1
)

assess_button = st.sidebar.button(
    "🔍 Assess Applicant",
    use_container_width=True
)

st.sidebar.divider()

st.sidebar.markdown(
    "### System"
)

st.sidebar.write(
    "Model: KAVACH-PROTOTYPE-v1"
)

st.sidebar.write(
    "Policy: KAVACH-POLICY-PROTOTYPE-v1"
)

st.sidebar.divider()

st.sidebar.warning(
    "Prototype only. "
    "Do not use this output for real lending decisions."
)


# =====================================================================
# LOAD SUMMARY
# =====================================================================

try:

    summary_response = requests.get(
        f"{API_URL}/summary",
        timeout=5
    )

    summary = summary_response.json()

except Exception as e:

    st.error(
        f"Unable to load Kavach summary: {e}"
    )

    st.stop()


# =====================================================================
# TOP SYSTEM METRICS
# =====================================================================

st.markdown(
    '<div class="section-title">System Overview</div>',
    unsafe_allow_html=True
)

c1, c2, c3, c4 = st.columns(4)

with c1:

    st.metric(
        "Applicants",
        f"{summary['applicants']:,}"
    )

with c2:

    st.metric(
        "Mean Risk Proxy",
        f"{summary['mean_risk_proxy'] * 100:.2f}%"
    )

with c3:

    st.metric(
        "Mean Evidence Quality",
        f"{summary['mean_evidence_quality']:.1f}/100"
    )

with c4:

    st.metric(
        "API Status",
        "ONLINE"
    )


# =====================================================================
# APPLICANT ASSESSMENT
# =====================================================================

st.markdown(
    '<div class="section-title">Applicant Assessment</div>',
    unsafe_allow_html=True
)


# Automatically assess applicant 0 on first load

if (
    assess_button
    or "assessment" not in st.session_state
):

    try:

        response = requests.get(
            f"{API_URL}/assessment/{applicant_id}",
            timeout=5
        )

        if response.status_code != 200:

            st.error(
                f"Assessment failed: {response.text}"
            )

            st.stop()

        st.session_state.assessment = response.json()

    except Exception as e:

        st.error(
            f"Unable to contact assessment API: {e}"
        )

        st.stop()


assessment = st.session_state.assessment


# =====================================================================
# BASIC DATA
# =====================================================================

risk = assessment["risk_proxy"]

risk_percent = assessment[
    "risk_proxy_percent"
]

risk_band = assessment[
    "risk_band"
]

evidence = assessment[
    "evidence_quality"
]

confidence = assessment[
    "confidence"
]

history_depth = assessment[
    "history_depth"
]

stability = assessment[
    "behavioral_stability"
]

policy = assessment[
    "policy_decision"
]


# =====================================================================
# RISK COLOR / STATUS
# =====================================================================

if risk_band == "LOW":

    risk_status = "LOW"

elif risk_band == "MODERATE":

    risk_status = "MODERATE"

elif risk_band == "ELEVATED":

    risk_status = "ELEVATED"

else:

    risk_status = "HIGH"


# =====================================================================
# MAIN RISK CARDS
# =====================================================================

c1, c2, c3, c4 = st.columns(4)


with c1:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">RISK PROXY</div>
            <div class="metric-value">{risk_percent:.1f}%</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with c2:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">RISK BAND</div>
            <div class="metric-value">{risk_status}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with c3:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">EVIDENCE QUALITY</div>
            <div class="metric-value">{evidence:.1f}/100</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with c4:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">CONFIDENCE</div>
            <div class="metric-value">{confidence}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =====================================================================
# SECONDARY METRICS
# =====================================================================

st.markdown(
    '<div class="section-title">Evidence & Behaviour</div>',
    unsafe_allow_html=True
)

c1, c2, c3 = st.columns(3)


with c1:

    st.metric(
        "History Depth",
        history_depth
    )


with c2:

    if stability is not None:

        st.metric(
            "Behavioral Stability",
            f"{stability:.1f}/100"
        )

    else:

        st.metric(
            "Behavioral Stability",
            "N/A"
        )


with c3:

    st.metric(
        "Applicant ID",
        assessment["applicant_id"]
    )


# =====================================================================
# POLICY DECISION
# =====================================================================

st.markdown(
    '<div class="section-title">Policy Routing</div>',
    unsafe_allow_html=True
)


if policy == "PASS_TO_LENDER_POLICY":

    st.success(
        f"✓ {policy}"
    )

elif policy == "MANUAL_REVIEW":

    st.warning(
        f"⚠ {policy}"
    )

elif policy == "INSUFFICIENT_EVIDENCE":

    st.error(
        f"⚠ {policy}"
    )

else:

    st.warning(
        policy
    )


# =====================================================================
# EXPLANATION
# =====================================================================

st.markdown(
    '<div class="section-title">Why this assessment?</div>',
    unsafe_allow_html=True
)

left, right = st.columns(2)


with left:

    st.markdown("### Factors supporting stability")

    positive = assessment[
        "positive_factors"
    ]

    for item in positive:

        st.markdown(
            f"✓ {item}"
        )


    st.markdown("### Factors increasing concern")

    concerns = assessment[
        "risk_factors"
    ]

    for item in concerns:

        st.markdown(
            f"⚠ {item}"
        )


with right:

    st.markdown("### Evidence limitations")

    limitations = assessment[
        "evidence_limitations"
    ]

    for item in limitations:

        st.markdown(
            f"ℹ {item}"
        )


# =====================================================================
# RISK / EVIDENCE VISUALIZATION
# =====================================================================

st.markdown(
    '<div class="section-title">Assessment Profile</div>',
    unsafe_allow_html=True
)

chart_data = pd.DataFrame(
    {
        "Metric": [
            "Risk Proxy",
            "Evidence Quality",
            "Behavioral Stability"
        ],
        "Score": [
            risk * 100,
            evidence,
            stability if stability is not None else 0
        ]
    }
)

st.bar_chart(
    chart_data.set_index("Metric")
)


# =====================================================================
# RAW API RESPONSE
# =====================================================================

with st.expander(
    "View complete assessment record"
):

    st.json(
        assessment
    )


# =====================================================================
# METHODOLOGY WARNING
# =====================================================================

st.divider()

st.markdown(
    """
    ### ⚠️ Methodology Notice

    **Kavach Pulse is currently a technical prototype.**

    The displayed risk proxy is not a calibrated probability
    of default. Behavioral histories used in the prototype are
    synthetic. The policy thresholds are demonstration
    assumptions.

    The dashboard demonstrates the architecture:

    **Evidence → Confidence → Risk → Policy → Explanation → Governance**

    It must not be used to make real lending decisions.
    """
)
