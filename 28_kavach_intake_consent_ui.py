"""
======================================================================
KAVACH PULSE — LIVE APPLICANT INTAKE + CONSENT UI
======================================================================

Version: 30.0

Workflow
--------
Applicant
    ↓
Consent
    ↓
Data Sources
    ↓
Evidence Availability
    ↓
Behavioural Inputs
    ↓
LIVE KAVACH API
    ↓
Risk + Evidence + Confidence
    ↓
Policy
    ↓
Explanation

IMPORTANT
---------
This is a technical/conceptual prototype.

No real lending decision is made.
Behavioural values are demonstration inputs.
"""

import streamlit as st
import requests
import uuid
from datetime import datetime, timedelta, timezone


# ======================================================================
# CONFIGURATION
# ======================================================================

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Kavach Pulse",
    page_icon="🛡️",
    layout="wide"
)


# ======================================================================
# CSS
# ======================================================================

st.markdown(
    """
    <style>

    .main {
        background-color: #f7f8fa;
    }

    .title {
        font-size: 42px;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 17px;
        color: #6b7280;
        margin-bottom: 20px;
    }

    .card {
        background: white;
        padding: 22px;
        border-radius: 14px;
        border: 1px solid #e5e7eb;
        margin-bottom: 15px;
    }

    .consent-box {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        padding: 20px;
        border-radius: 14px;
    }

    .success-box {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        padding: 18px;
        border-radius: 14px;
    }

    .warning-box {
        background: #fff7ed;
        border: 1px solid #fed7aa;
        padding: 18px;
        border-radius: 14px;
    }

    .danger-box {
        background: #fef2f2;
        border: 1px solid #fecaca;
        padding: 18px;
        border-radius: 14px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ======================================================================
# SESSION STATE
# ======================================================================

defaults = {
    "consent_granted": False,
    "consent_id": None,
    "consent_expiry": None,
    "withdrawn": False,
    "assessment": None
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ======================================================================
# HEADER
# ======================================================================

st.markdown(
    '<div class="title">🛡️ KAVACH PULSE</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Evidence-aware alternative credit assessment prototype'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# ======================================================================
# API HEALTH
# ======================================================================

try:

    health_response = requests.get(
        f"{API_URL}/health",
        timeout=3
    )

    api_online = health_response.status_code == 200

    if api_online:

        health = health_response.json()

        st.success(
            "● Kavach Live Assessment API is online"
        )

        with st.expander("API status"):

            st.json(health)

    else:

        st.error(
            "Kavach API returned an error."
        )

except Exception as e:

    api_online = False

    st.error(
        "Kavach API is offline."
    )

    st.code(
        "python 29_kavach_live_assessment_api.py"
    )

    st.stop()


# ======================================================================
# WORKFLOW
# ======================================================================

st.markdown(
    "**1 Applicant → 2 Consent → 3 Data → "
    "4 Evidence → 5 Behaviour → 6 Assessment**"
)

st.divider()


# ======================================================================
# 1. APPLICANT
# ======================================================================

st.header("1. Applicant Information")

col1, col2 = st.columns(2)

with col1:

    applicant_id = st.number_input(
        "Prototype Applicant ID",
        min_value=0,
        max_value=4999,
        value=0,
        step=1
    )

with col2:

    purpose = st.selectbox(
        "Assessment purpose",
        [
            "Credit eligibility assessment",
            "Pre-approved offer assessment",
            "Financial eligibility review"
        ]
    )

st.info(
    "Prototype only: applicant IDs and behavioural values "
    "are demonstration inputs."
)


# ======================================================================
# 2. CONSENT
# ======================================================================

st.header("2. Applicant Consent")

st.markdown(
    """
    <div class="consent-box">

    <b>Why is this information requested?</b>

    Kavach uses consented financial and behavioural information
    to assess income stability, cash-flow behaviour and
    repayment capacity.

    </div>
    """,
    unsafe_allow_html=True
)

st.subheader("Requested information")

bank_consent = st.checkbox(
    "Bank cash-flow history — last 12 months"
)

platform_consent = st.checkbox(
    "Platform income history — last 12 months"
)

payment_consent = st.checkbox(
    "Repayment history — last 12 months"
)

st.subheader("Consent conditions")

consent_terms = st.checkbox(
    "I understand what information is being requested "
    "and why it is being used."
)

withdrawal_understanding = st.checkbox(
    "I understand that consent can be withdrawn."
)

all_sources_selected = (
    bank_consent
    and platform_consent
    and payment_consent
)

consent_valid = (
    all_sources_selected
    and consent_terms
    and withdrawal_understanding
)


# ======================================================================
# GRANT CONSENT
# ======================================================================

if st.button(
    "✓ Grant Consent",
    disabled=(
        not consent_valid
        or st.session_state.consent_granted
    ),
    use_container_width=True
):

    st.session_state.consent_id = (
        "KVC-"
        + uuid.uuid4().hex[:12].upper()
    )

    st.session_state.consent_expiry = (
        datetime.now(timezone.utc)
        + timedelta(days=30)
    )

    st.session_state.consent_granted = True
    st.session_state.withdrawn = False

    st.success(
        "Consent successfully recorded."
    )


# ======================================================================
# CONSENT STATUS
# ======================================================================

if st.session_state.consent_granted:

    st.markdown(
        f"""
        <div class="success-box">

        <b>CONSENT STATUS: VALID</b><br><br>

        Consent ID:
        <b>{st.session_state.consent_id}</b><br><br>

        Expires:
        <b>{st.session_state.consent_expiry.isoformat()}</b>

        </div>
        """,
        unsafe_allow_html=True
    )

else:

    st.warning(
        "Consent has not been granted."
    )


# ======================================================================
# WITHDRAWAL
# ======================================================================

if st.session_state.consent_granted:

    st.header("3. Consent Management")

    if st.button(
        "Withdraw Consent",
        use_container_width=True
    ):

        st.session_state.consent_granted = False
        st.session_state.withdrawn = True
        st.session_state.assessment = None

        st.warning(
            "Consent withdrawn. "
            "New assessment processing is blocked."
        )


if st.session_state.withdrawn:

    st.error(
        "CONSENT WITHDRAWN — assessment processing is disabled."
    )

    st.stop()


# ======================================================================
# EVERYTHING BELOW REQUIRES CONSENT
# ======================================================================

if st.session_state.consent_granted:

    # ================================================================
    # 4. DATA SOURCES
    # ================================================================

    st.header("4. Data Sources")

    source_col1, source_col2, source_col3 = st.columns(3)

    with source_col1:

        st.markdown(
            """
            ### Bank Data

            **Requested**

            Last 12 months

            Used for:

            - Cash-flow analysis
            - Income continuity
            - Inflow/outflow behaviour
            """
        )

    with source_col2:

        st.markdown(
            """
            ### Platform Data

            **Requested**

            Last 12 months

            Used for:

            - Income continuity
            - Income volatility
            - Platform activity
            """
        )

    with source_col3:

        st.markdown(
            """
            ### Repayment Data

            **Requested**

            Last 12 months

            Used for:

            - Payment consistency
            - Missed-payment behaviour
            - Repayment stability
            """
        )


    # ================================================================
    # 5. EVIDENCE
    # ================================================================

    st.header("5. Evidence Availability")

    history_months = st.slider(
        "Requested financial history",
        min_value=1,
        max_value=12,
        value=12
    )

    available_months = st.slider(
        "Actually available months",
        min_value=1,
        max_value=history_months,
        value=history_months
    )

    source_count = st.slider(
        "Available independent data sources",
        min_value=1,
        max_value=3,
        value=3
    )

    missing_periods = (
        history_months - available_months
    )

    completeness = (
        available_months / history_months
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "Requested",
            f"{history_months} months"
        )

    with c2:

        st.metric(
            "Available",
            f"{available_months} months"
        )

    with c3:

        st.metric(
            "Missing",
            missing_periods
        )

    with c4:

        st.metric(
            "Completeness",
            f"{completeness * 100:.0f}%"
        )

    if completeness >= 0.90:

        st.success(
            "Strong evidence coverage"
        )

    elif completeness >= 0.60:

        st.warning(
            "Partial evidence coverage"
        )

    else:

        st.error(
            "Very limited evidence coverage"
        )


    # ================================================================
    # 6. BEHAVIOURAL INPUTS
    # ================================================================

    st.header("6. Prototype Behavioural Inputs")

    st.warning(
        "These are synthetic demonstration inputs. "
        "They are NOT real financial information."
    )

    col1, col2 = st.columns(2)

    with col1:

        payment_success_rate = st.slider(
            "Payment success rate",
            min_value=0.50,
            max_value=1.00,
            value=0.92,
            step=0.01
        )

        income_cv = st.slider(
            "Income volatility",
            min_value=0.02,
            max_value=0.60,
            value=0.20,
            step=0.01
        )

        cashflow_cv = st.slider(
            "Cash-flow volatility",
            min_value=0.05,
            max_value=1.00,
            value=0.35,
            step=0.01
        )

    with col2:

        balance_min = st.number_input(
            "Minimum cash balance",
            min_value=0.0,
            max_value=500000.0,
            value=25000.0,
            step=1000.0
        )

        inflow_ratio = st.slider(
            "Inflow / outflow ratio",
            min_value=0.50,
            max_value=2.50,
            value=1.40,
            step=0.01
        )

        income_trend = st.slider(
            "Income trend",
            min_value=-0.20,
            max_value=0.20,
            value=0.00,
            step=0.01
        )


    # ================================================================
    # 7. ASSESSMENT
    # ================================================================
# =====================================================================
# ASSESSMENT
# =====================================================================

if st.session_state.consent_granted:

    st.markdown(
        "## 7. Request Assessment"
    )

    st.markdown(
        """
        Before requesting the assessment:

        ✓ Consent is valid

        ✓ Data sources are specified

        ✓ Evidence availability is known

        ✓ Prototype behavioural inputs are identified
        """
    )

    if st.button(
        "🛡️ Run Kavach Assessment",
        type="primary",
        use_container_width=True
    ):

        # -------------------------------------------------------------
        # Build assessment payload
        # -------------------------------------------------------------

        payload = {
            "applicant_id": int(applicant_id),

            "history_months": int(history_months),

            "available_months": int(available_months),

            "source_count": int(source_count),

            "payment_success_rate": float(
                payment_success_rate
            ),

            "income_cv": float(
                income_cv
            ),

            "cashflow_cv": float(
                cashflow_cv
            ),

            "balance_min": float(
                balance_min
            ),

            "inflow_to_outflow_ratio": float(
                inflow_ratio
            ),

            "income_trend": float(
                income_trend
            ),

            "consent_granted": True
        }

        # -------------------------------------------------------------
        # Show submitted information
        # -------------------------------------------------------------

        with st.expander(
            "View assessment input"
        ):

            st.json(payload)

        # -------------------------------------------------------------
        # Send LIVE request to FastAPI
        # -------------------------------------------------------------

        try:

            response = requests.post(
                f"{API_URL}/assess",
                json=payload,
                timeout=10
            )

            # ---------------------------------------------------------
            # Successful assessment
            # ---------------------------------------------------------

            if response.status_code == 200:

                assessment = response.json()

                st.session_state.assessment = assessment

                st.success(
                    "Kavach assessment completed successfully."
                )

            # ---------------------------------------------------------
            # API validation error
            # ---------------------------------------------------------

            elif response.status_code == 422:

                st.error(
                    "Assessment input validation failed."
                )

                st.code(
                    response.text,
                    language="json"
                )

            # ---------------------------------------------------------
            # Consent / policy rejection
            # ---------------------------------------------------------

            elif response.status_code in [400, 403]:

                st.error(
                    "Assessment was rejected by the Kavach API."
                )

                st.code(
                    response.text,
                    language="json"
                )

            # ---------------------------------------------------------
            # Other API error
            # ---------------------------------------------------------

            else:

                st.error(
                    f"Kavach API returned HTTP "
                    f"{response.status_code}"
                )

                st.code(
                    response.text,
                    language="json"
                )

        except requests.exceptions.ConnectionError:

            st.error(
                """
                Kavach API is offline.

                Start the API with:

                python3 29_kavach_live_assessment_api.py
                """
            )

        except requests.exceptions.Timeout:

            st.error(
                "Kavach API request timed out."
            )

        except Exception as e:

            st.error(
                f"Unexpected assessment error: {e}"
            )


# =====================================================================
# ASSESSMENT RESULT
# =====================================================================
# ======================================================================
# 8. ASSESSMENT RESULT
# ======================================================================

if st.session_state.assessment is not None:

    assessment = st.session_state.assessment

    st.divider()

    st.header("8. Kavach Assessment")

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "Risk Proxy",
            f"{assessment['risk_proxy_percent']:.2f}%"
        )

    with c2:

        st.metric(
            "Risk Band",
            assessment["risk_band"]
        )

    with c3:

        st.metric(
            "Evidence Quality",
            f"{assessment['evidence_quality']:.1f}/100"
        )

    with c4:

        st.metric(
            "Confidence",
            assessment["confidence"]
        )


    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "History Depth",
            assessment["history_depth"]
        )

    with c2:

        st.metric(
            "Behavioural Stability",
            f"{assessment['behavioral_stability']:.1f}"
        )

    with c3:

        st.metric(
            "Policy Decision",
            assessment["policy_decision"]
        )


    st.subheader("Policy Routing")

    decision = assessment["policy_decision"]

    if decision == "PASS_TO_LENDER_POLICY":

        st.success(
            f"✓ {decision}"
        )

    elif decision == "MANUAL_REVIEW":

        st.warning(
            f"⚠ {decision}"
        )

    else:

        st.error(
            f"✕ {decision}"
        )


    # ================================================================
    # EXPLANATION
    # ================================================================

    left, right = st.columns(2)

    with left:

        st.subheader("Positive Factors")

        factors = assessment.get(
            "positive_factors",
            []
        )

        for item in factors:

            st.write(
                f"✓ {item}"
            )


        st.subheader("Risk Factors")

        factors = assessment.get(
            "risk_factors",
            []
        )

        for item in factors:

            st.write(
                f"⚠ {item}"
            )


    with right:

        st.subheader("Evidence Limitations")

        limitations = assessment.get(
            "evidence_limitations",
            []
        )

        for item in limitations:

            st.write(
                f"• {item}"
            )


    # ================================================================
    # TECHNICAL DETAILS
    # ================================================================

    with st.expander("Technical assessment details"):

        st.json(assessment)


    st.caption(
        "Prototype only. Risk proxy is not a calibrated "
        "probability of default and must not be used as a "
        "production lending decision."
    )
