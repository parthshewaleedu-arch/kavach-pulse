import json
from datetime import datetime
import pandas as pd
import requests
import streamlit as st
import os

# =====================================================================
# KAVACH PULSE — COMMAND CENTER
# =====================================================================

st.set_page_config(
    page_title="Kavach Pulse — Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =====================================================================
# CONFIGURATION
# =====================================================================

API_URL = "http://127.0.0.1:8000"


# =====================================================================
# CUSTOM CSS
# =====================================================================
# =====================================================================
# CUSTOM CSS
# =====================================================================

st.markdown(
    """
    <style>

    /* ================================================================
       GLOBAL
       ================================================================ */

    .stApp {
        background:
            radial-gradient(
                circle at 85% 5%,
                rgba(44, 95, 160, 0.10),
                transparent 28%
            ),
            #0b0f14;
    }

    .main .block-container {
        max-width: 1500px;
        padding-top: 2.5rem;
        padding-bottom: 4rem;
    }

    /* ================================================================
       SIDEBAR
       ================================================================ */

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #111722 0%,
                #0d121a 100%
            );

        border-right: 1px solid rgba(255,255,255,0.07);
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1.5rem;
    }

    section[data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.08);
        margin: 1.5rem 0;
    }
/* Sidebar refinement */

[data-testid="stSidebar"] {
    border-right: 1px solid rgba(255,255,255,0.06);
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.5rem;
}
    /* ================================================================
       BRAND
       ================================================================ */

    .kavach-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 4px;
    }

    .kavach-shield {
        width: 42px;
        height: 42px;
        border-radius: 12px;

        display: flex;
        align-items: center;
        justify-content: center;

        background:
            linear-gradient(
                145deg,
                #19314d,
                #101b29
            );

        border: 1px solid rgba(130,190,255,0.20);

        font-size: 23px;

        box-shadow:
            0 8px 25px rgba(0,0,0,0.30);
    }

    .kavach-brand-name {
        font-size: 22px;
        font-weight: 800;
        letter-spacing: -0.5px;
    }

    .kavach-brand-subtitle {
        font-size: 11px;
        color: #7f8b9a;
        margin-top: 2px;
        letter-spacing: 0.8px;
        text-transform: uppercase;
    }

    /* ================================================================
       MAIN HEADER
       ================================================================ */

    .kavach-header {
        display: flex;
        align-items: center;
        justify-content: space-between;

        padding: 6px 0 28px 0;

        border-bottom: 1px solid rgba(255,255,255,0.08);

        margin-bottom: 28px;
    }

    .kavach-header-left {
        display: flex;
        align-items: center;
        gap: 16px;
    }

    .kavach-header-icon {
        width: 58px;
        height: 58px;

        display: flex;
        align-items: center;
        justify-content: center;

        border-radius: 16px;

        background:
            linear-gradient(
                145deg,
                #193b5d,
                #101c2b
            );

        border: 1px solid rgba(120,190,255,0.22);

        font-size: 30px;

        box-shadow:
            0 10px 30px rgba(0,0,0,0.25);
    }

    .kavach-header-title {
        font-size: 34px;
        font-weight: 850;
        letter-spacing: -1.2px;
        line-height: 1.0;
    }

    .kavach-header-description {
        margin-top: 7px;
        color: #8c97a6;
        font-size: 14px;
    }

    .live-indicator {
        display: inline-flex;
        align-items: center;
        gap: 8px;

        padding: 8px 13px;

        border-radius: 999px;

        background: rgba(34,197,94,0.09);
        border: 1px solid rgba(34,197,94,0.20);

        color: #55d889;

        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }

    .live-dot {
        width: 7px;
        height: 7px;

        border-radius: 50%;

        background: #45d483;

        box-shadow:
            0 0 10px rgba(69,212,131,0.7);
    }

    /* ================================================================
       PAGE TITLES
       ================================================================ */

    .section-title {
        font-size: 30px;
        font-weight: 800;
        letter-spacing: -0.7px;
        margin-top: 8px;
        margin-bottom: 8px;
    }

    .section-subtitle {
        color: #8994a3;
        font-size: 14px;
        margin-bottom: 25px;
    }

    /* ================================================================
       INFORMATION CARDS
       ================================================================ */

    .kavach-info-card {
        background:
            linear-gradient(
                135deg,
                rgba(29,56,83,0.85),
                rgba(19,35,53,0.85)
            );

        border: 1px solid rgba(88,157,220,0.18);

        border-radius: 16px;

        padding: 22px 24px;

        margin: 14px 0 25px 0;
    }

    .kavach-info-title {
        font-size: 17px;
        font-weight: 750;
        color: #e8f3ff;
        margin-bottom: 10px;
    }

    .kavach-info-text {
        color: #a8bacd;
        font-size: 14px;
        line-height: 1.7;
    }

    /* ================================================================
       METRIC CARDS
       ================================================================ */

    .metric-card {
        background:
            linear-gradient(
                145deg,
                #121923,
                #0f151d
            );

        border: 1px solid rgba(255,255,255,0.08);

        border-radius: 16px;

        padding: 20px;

        min-height: 110px;

        box-shadow:
            0 8px 30px rgba(0,0,0,0.18);
    }

    .metric-label {
        color: #8490a0;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.7px;
        font-weight: 700;
    }

    .metric-value {
        margin-top: 10px;

        font-size: 29px;
        font-weight: 800;

        color: #f2f6fa;
    }

    .metric-description {
        margin-top: 5px;
        font-size: 11px;
        color: #697585;
    }

    /* ================================================================
       CONSENT CARDS
       ================================================================ */

    .consent-card {
        background:
            linear-gradient(
                145deg,
                #121923,
                #0f141c
            );

        border: 1px solid rgba(255,255,255,0.075);

        border-radius: 14px;

        padding: 18px 20px;

        margin-bottom: 12px;

        transition:
            border-color 0.2s ease,
            background 0.2s ease;
    }

    .consent-card:hover {
        border-color: rgba(80,170,240,0.25);

        background:
            linear-gradient(
                145deg,
                #151e29,
                #101720
            );
    }

    /* ================================================================
       STATUS CARDS
       ================================================================ */

    .status-card {
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 15px;

        border: 1px solid rgba(255,255,255,0.08);

        background: #111720;
    }

    .status-online {
        background: rgba(34,197,94,0.08);
        border-color: rgba(34,197,94,0.20);
    }

    .status-offline {
        background: rgba(239,68,68,0.08);
        border-color: rgba(239,68,68,0.20);
    }

    /* ================================================================
       BUTTONS
       ================================================================ */

    .stButton > button {
        border-radius: 11px;

        min-height: 46px;

        font-weight: 700;

        border: 1px solid rgba(255,255,255,0.10);

        transition:
            transform 0.15s ease,
            border-color 0.15s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);

        border-color: rgba(100,180,255,0.35);
    }

    /* ================================================================
       TABLES
       ================================================================ */

    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;

        border: 1px solid rgba(255,255,255,0.07);
    }

    /* ================================================================
       INPUTS
       ================================================================ */

    div[data-baseweb="select"] > div {
        border-radius: 10px;
    }

    div[data-testid="stNumberInput"] input {
        border-radius: 10px;
    }

    /* ================================================================
       EXPANDERS
       ================================================================ */

    div[data-testid="stExpander"] {
        border-radius: 12px;

        border: 1px solid rgba(255,255,255,0.07);

        background: rgba(17,23,32,0.65);
    }

    /* ================================================================
       FOOTER
       ================================================================ */

    .kavach-footer {
        margin-top: 50px;

        padding-top: 20px;

        border-top: 1px solid rgba(255,255,255,0.07);

        color: #626d7b;

        font-size: 11px;

        text-align: center;

        letter-spacing: 0.2px;
    }

    /* ================================================================
       SMALL TEXT
       ================================================================ */

    .small-text {
        font-size: 12px;
        color: #7c8796;
    }
/* ================================================================
   KAVACH PREMIUM HEADER
   ================================================================ */

.kavach-header {
    display: flex;
    align-items: center;
    gap: 18px;
    width: 100%;
    padding: 18px 0 24px 0;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 30px;
}

.kavach-header-icon {
    width: 54px;
    height: 54px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 14px;
    background: rgba(79, 195, 247, 0.10);
    border: 1px solid rgba(79, 195, 247, 0.20);
    font-size: 29px;
}

.kavach-header-content {
    display: flex;
    flex-direction: column;
    flex: 1;
}

.kavach-header-title {
    font-size: 32px;
    font-weight: 850;
    letter-spacing: 1.5px;
    line-height: 1.1;
}

.kavach-header-description {
    margin-top: 5px;
    font-size: 14px;
    color: rgba(255,255,255,0.55);
}

.live-indicator {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 13px;
    border-radius: 20px;
    background: rgba(34,197,94,0.08);
    border: 1px solid rgba(34,197,94,0.20);
    color: #55d889;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.8px;
    white-space: nowrap;
}

.live-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #55d889;
    display: inline-block;
}


/* ================================================================
   STATUS CARD
   ================================================================ */

.status-card {
    padding: 14px 16px;
    border-radius: 12px;
    margin: 10px 0 14px 0;
}

.status-online {
    background: rgba(34,197,94,0.08);
    border: 1px solid rgba(34,197,94,0.25);
}

.status-offline {
    background: rgba(239,68,68,0.08);
    border: 1px solid rgba(239,68,68,0.25);
}

.status-online-title {
    display: block;
    color: #55d889;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.7px;
}

.status-offline-title {
    display: block;
    color: #f87171;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.7px;
}

.status-description {
    display: block;
    margin-top: 6px;
    color: rgba(255,255,255,0.55);
    font-size: 11px;
}
    </style>
    """,
    unsafe_allow_html=True,
)

# =====================================================================
# SESSION STATE
# =====================================================================

defaults = {
    "consent_1": False,
    "consent_2": False,
    "consent_3": False,
    "consent_4": False,
    "consent_5": False,
    "consent_granted": False,
    "consent_timestamp": None,
    "consent_id": None,
    "assessment": None,
    "withdrawn": False,
}

for key, value in defaults.items():

    if key not in st.session_state:

        st.session_state[key] = value


# =====================================================================
# API HEALTH
# =====================================================================

def get_api_health():

    try:

        response = requests.get(
            f"{API_URL}/health",
            timeout=3
        )

        if response.status_code == 200:

            return True, response.json()

        return False, response.text

    except Exception as exc:

        return False, str(exc)


api_online, api_data = get_api_health()


# =====================================================================
# SIDEBAR
# =====================================================================
# =====================================================================
# SIDEBAR
# =====================================================================

with st.sidebar:

    st.markdown(
        """
        <div class="kavach-brand">
            <div class="kavach-shield">🛡</div>
            <div>
                <div class="kavach-brand-name">KAVACH</div>
                <div class="kavach-brand-subtitle">
                    Pulse Risk Intelligence
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown(
        "### Command Center"
    )

    page = st.radio(
        "Command Centre Navigation",
        [
            "Live Assessment",
            "Applicant Comparison",
            "Risk & Confidence",
            "Validation",
            "Governance",
            "System Status",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    # ---------------------------------------------------------------
    # SYSTEM STATUS
    # ---------------------------------------------------------------

    if api_online:

        st.markdown(
            """
            <div class="status-card status-online">
                <span class="status-online-title">● SYSTEM ONLINE</span>
                <span class="status-description">
                    Kavach assessment engine connected
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption(
            f"Engine · {api_data.get('engine_version', 'Unknown')}"
        )

        st.caption(
            f"Model · {api_data.get('model_version', 'Unknown')}"
        )

        st.caption(
            f"Policy · {api_data.get('policy_version', 'Unknown')}"
        )

    else:

        st.markdown(
            """
            <div class="status-card status-offline">
                <span class="status-offline-title">● SYSTEM OFFLINE</span>
                <span class="status-description">
                    Assessment API is unavailable
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption(
            "Start the Kavach API on port 8000."
        )
        
    st.divider()

    st.markdown(
        """
        <div class="small-text">
            <b>KAVACH PULSE</b><br>
            Evidence-aware alternative credit assessment
            and policy intelligence.
            <br><br>
            Prototype • Live Engine
        </div>
        """,
        unsafe_allow_html=True,
    )

# =====================================================================
# HEADER
# =====================================================================


# =====================================================================
# HEADER
# =====================================================================

st.markdown(
    """<div class="kavach-header"><div class="kavach-header-icon">🛡</div><div class="kavach-header-content"><div class="kavach-header-title">KAVACH PULSE</div><div class="kavach-header-description">Evidence-aware alternative credit assessment&nbsp;&nbsp;•&nbsp;&nbsp;Policy intelligence</div></div><div class="live-indicator"><span class="live-dot"></span> LIVE ENGINE</div></div>""",
    unsafe_allow_html=True,
)

# =====================================================================
# LIVE ASSESSMENT
# =====================================================================

if page == "Live Assessment":

    st.markdown(
        '<div class="section-title">Live Assessment</div>',
        unsafe_allow_html=True
    )

    st.info(
        """
        **Kavach separates two questions:**

        **RISK** — What does the available behavioural evidence suggest?

        **CONFIDENCE** — How sufficient and reliable is that evidence?

        Therefore:

        **RISK ≠ CONFIDENCE**
        """
    )

    # ---------------------------------------------------------------
    # 1. APPLICANT
    # ---------------------------------------------------------------

    st.markdown("## 1. Applicant & Consent")

    col1, col2, col3 = st.columns(3)

    with col1:

        applicant_id = st.number_input(
            "Applicant ID",
            min_value=1,
            max_value=999999999,
            value=100,
            step=1,
        )

    with col2:

        source_count = st.number_input(
            "Data sources",
            min_value=1,
            max_value=10,
            value=3,
            step=1,
        )

    with col3:

        consent_status = (
            "GRANTED"
            if st.session_state.consent_granted
            else "NOT GRANTED"
        )

        st.metric(
            "Consent status",
            consent_status
        )

    # ---------------------------------------------------------------
    # ---------------------------------------------------------------
    # 2. FIVE EXPLICIT CONSENTS
    # ---------------------------------------------------------------

    st.markdown("### Explicit Consent Requirements")

    st.caption(
    "Each consent represents a separate processing purpose. "
    "Assessment is allowed only after all five required "
    "consent items are explicitly accepted."
    )

    st.info(
    """
    **Applicant control**

    Kavach uses purpose-specific consent rather than one
    blanket permission. Each processing purpose is shown
    separately so the applicant can understand what information
    is being used and why.
    """
    )

    # ---------------------------------------------------------------
    # CONSENT 1 — BANK / CASH-FLOW DATA
    # ---------------------------------------------------------------

    st.markdown("#### 1. Bank / Cash-Flow Data")

    st.caption(
    "Permission to use permitted transaction and cash-flow "
    "information for behavioural assessment."
    )

    st.session_state.consent_1 = st.checkbox(
    "I consent to Kavach using permitted bank and cash-flow data.",
    value=st.session_state.consent_1,
    )

    st.caption(
    "Purpose: evaluate permitted inflows, outflows, "
    "balance stability and cash-flow behaviour."
    )

    # ---------------------------------------------------------------
    # CONSENT 2 — INCOME / EMPLOYMENT DATA
    # ---------------------------------------------------------------

    st.markdown("#### 2. Income / Employment Data")

    st.caption(
    "Permission to use permitted income and employment-related "
    "evidence."
    )

    st.session_state.consent_2 = st.checkbox(
    "I consent to Kavach using permitted income and employment data.",
    value=st.session_state.consent_2,
    )

    st.caption(
    "Purpose: evaluate income consistency, volatility "
    "and observed income trends."
    )

    # ---------------------------------------------------------------
    # CONSENT 3 — PAYMENT / REPAYMENT DATA
    # ---------------------------------------------------------------

    st.markdown("#### 3. Payment / Repayment Behaviour")

    st.caption(
    "Permission to use permitted payment and repayment behaviour."
    )

    st.session_state.consent_3 = st.checkbox(
    "I consent to Kavach using permitted payment and repayment data.",
    value=st.session_state.consent_3,
    )

    st.caption(
    "Purpose: evaluate payment consistency and "
    "repayment-related behavioural signals."
    )

    # ---------------------------------------------------------------
    # CONSENT 4 — ALTERNATIVE BEHAVIOURAL DATA
    # ---------------------------------------------------------------

    st.markdown("#### 4. Alternative Behavioural Data")

    st.caption(
    "Permission to use permitted alternative behavioural "
    "evidence when available."
    )

    st.session_state.consent_4 = st.checkbox(
    "I consent to Kavach using permitted alternative behavioural data.",
    value=st.session_state.consent_4,
    )

    st.caption(
    "Purpose: supplement traditional credit information "
    "with consented behavioural evidence."
    )

    # ---------------------------------------------------------------
    # CONSENT 5 — CREDIT ASSESSMENT PROCESSING
    # ---------------------------------------------------------------

    st.markdown("#### 5. Credit Assessment Processing")

    st.caption(
    "Permission to process the consented evidence to generate "
    "a Kavach risk and evidence assessment."
    )

    st.session_state.consent_5 = st.checkbox(
    "I consent to Kavach processing my consented data for assessment.",
    value=st.session_state.consent_5,
    )

    st.caption(
    "Purpose: combine available evidence, generate risk and "
    "confidence outputs, and route the case according to "
    "the prototype policy."
    )

    # ---------------------------------------------------------------
    # CONSENT SUMMARY
    # ---------------------------------------------------------------

    consent_values = [
    st.session_state.consent_1,
    st.session_state.consent_2,
    st.session_state.consent_3,
    st.session_state.consent_4,
    st.session_state.consent_5,
    ]

    consent_count = sum(consent_values)

    all_consents = consent_count == 5
    st.session_state.consent_granted = all_consents
    st.divider()

    st.markdown("### Consent Status")

    st.progress(
        consent_count / 5,
        text=f"Consent completion: {consent_count}/5"
    )

    if consent_count == 0:

        st.warning(
            "No processing consent has been granted. "
            "Assessment is unavailable."
        )

    elif consent_count < 5:

        st.warning(
            f"{consent_count}/5 required consents granted. "
            "Complete all required consents before requesting "
            "an assessment."
        )

    else:

        st.success(
            "All 5 required consents have been explicitly granted. "
            "Assessment may proceed."
        )
    # ---------------------------------------------------------------
    # APPLICANT RIGHTS
    # ---------------------------------------------------------------

    st.markdown("### Applicant Rights")

    st.info(
    """
    **Right to withdraw**

    The applicant may withdraw consent subject to applicable
    processing and retention requirements.

    Withdrawal prevents further assessment processing based
    on withdrawn consent and should be recorded in the
    consent audit trail.
    """
    )

    # ---------------------------------------------------------------
    # CONSENT AUDIT SUMMARY
    # ---------------------------------------------------------------

    consent_audit_summary = [
    {
    "Consent": "Bank / Cash-Flow Data",
    "Purpose": "Cash-flow and balance behaviour",
    "Granted": "YES" if st.session_state.consent_1 else "NO",
    },
    {
    "Consent": "Income / Employment Data",
    "Purpose": "Income consistency and trends",
    "Granted": "YES" if st.session_state.consent_2 else "NO",
    },
    {
    "Consent": "Payment / Repayment Behaviour",
    "Purpose": "Payment consistency and repayment behaviour",
    "Granted": "YES" if st.session_state.consent_3 else "NO",
    },
    {
    "Consent": "Alternative Behavioural Data",
    "Purpose": "Supplementary behavioural evidence",
    "Granted": "YES" if st.session_state.consent_4 else "NO",
    },
    {
    "Consent": "Credit Assessment Processing",
    "Purpose": "Generate risk, confidence and policy outputs",
    "Granted": "YES" if st.session_state.consent_5 else "NO",
    },
    ]

    st.dataframe(
    consent_audit_summary,
    width="stretch",
    hide_index=True,
    )


    # 3. EVIDENCE AVAILABILITY
    # ---------------------------------------------------------------

    st.markdown("## 2. Evidence Availability")

    col1, col2, col3 = st.columns(3)

    with col1:

        history_months = st.slider(
            "Requested history",
            min_value=1,
            max_value=12,
            value=12,
            step=1,
        )

    with col2:

        available_months = st.slider(
            "Available months",
            min_value=0,
            max_value=history_months,
            value=history_months,
            step=1,
        )

    with col3:

        payment_success_rate = st.slider(
            "Payment success rate",
            min_value=0.50,
            max_value=1.00,
            value=0.98,
            step=0.01,
        )


    # ---------------------------------------------------------------
    # 4. BEHAVIOURAL INPUTS
    # ---------------------------------------------------------------

    st.markdown("## 3. Behavioural Inputs")

    st.warning(
        "Prototype demonstration inputs. "
        "These values are not real financial information."
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        income_cv = st.slider(
            "Income volatility",
            min_value=0.02,
            max_value=0.60,
            value=0.12,
            step=0.01,
        )

    with col2:

        cashflow_cv = st.slider(
            "Cash-flow volatility",
            min_value=0.05,
            max_value=1.00,
            value=0.20,
            step=0.01,
        )

    with col3:

        balance_min = st.number_input(
            "Minimum cash balance",
            min_value=0.0,
            max_value=500000.0,
            value=40000.0,
            step=1000.0,
        )


    col1, col2 = st.columns(2)

    with col1:

        inflow_ratio = st.slider(
            "Inflow / outflow ratio",
            min_value=0.50,
            max_value=2.50,
            value=1.55,
            step=0.01,
        )

    with col2:

        income_trend = st.slider(
            "Income trend",
            min_value=-0.20,
            max_value=0.20,
            value=0.04,
            step=0.01,
        )


    # ---------------------------------------------------------------
    # INPUT SUMMARY
    # ---------------------------------------------------------------

    summary = {
        "Applicant ID": str(applicant_id),
        "Requested history": f"{history_months} months",
        "Available history": f"{available_months} months",
        "Data sources": str(source_count),
        "Payment success": f"{payment_success_rate:.2f}",
        "Income volatility": f"{income_cv:.2f}",
        "Cash-flow volatility": f"{cashflow_cv:.2f}",
        "Minimum balance": f"₹{balance_min:,.0f}",
        "Inflow/outflow": f"{inflow_ratio:.2f}",
        "Income trend": f"{income_trend:+.2f}",
    }
    
    summary_df = pd.DataFrame(
        list(summary.items()),
        columns=["Parameter", "Value"],
    )
    
    st.dataframe(
        summary_df,
        width="stretch",
        hide_index=True,
    )

    # ---------------------------------------------------------------
    # 5. ASSESSMENT
    # ---------------------------------------------------------------

    st.markdown("## 4. Assessment")

    st.info(
        """
        Kavach evaluates the available evidence while keeping
        **risk and confidence separate**.

        A low-risk estimate supported by weak evidence is not treated
        as equivalent to the same risk estimate supported by strong evidence.
        """
    )


    assessment_allowed = (
        st.session_state.consent_granted
        and all_consents
        and not st.session_state.withdrawn
    )


    if not assessment_allowed:

        st.warning(
            "Assessment is locked until all 5 consent requirements "
            "have been accepted."
        )


    if st.button(
        "🛡️ Run Kavach Assessment",
        type="primary",
        disabled=not assessment_allowed,
        width="stretch",
    ):

        payload = {

            "applicant_id":
                int(applicant_id),

            "history_months":
                int(history_months),

            "available_months":
                int(available_months),

            "source_count":
                int(source_count),

            "payment_success_rate":
                float(payment_success_rate),

            "income_cv":
                float(income_cv),

            "cashflow_cv":
                float(cashflow_cv),

            "balance_min":
                float(balance_min),

            "inflow_to_outflow_ratio":
                float(inflow_ratio),

            "income_trend":
                float(income_trend),

            "consent_granted":
                True,
        }


        try:

            with st.spinner(
                "Kavach assessment engine processing..."
            ):

                response = requests.post(
                    f"{API_URL}/assess",
                    json=payload,
                    timeout=10,
                )


            if response.status_code == 200:

                assessment = response.json()

                st.session_state.assessment = assessment

                st.success(
                    "Assessment completed successfully."
                )

            else:

                st.error(
                    f"Assessment rejected: HTTP {response.status_code}"
                )

                st.code(
                    response.text,
                    language="json"
                )


        except requests.exceptions.ConnectionError:

            st.error(
                "Cannot connect to Kavach API at "
                f"{API_URL}."
            )

        except requests.exceptions.Timeout:

            st.error(
                "Kavach API request timed out."
            )

        except Exception as exc:

            st.error(
                f"Assessment error: {exc}"
            )


    # ---------------------------------------------------------------
    # 6. ASSESSMENT RESULT
    # ---------------------------------------------------------------

    if st.session_state.assessment is not None:

        assessment = st.session_state.assessment

        st.divider()

        st.markdown("## 5. Assessment Result")

        c1, c2, c3, c4 = st.columns(4)

        with c1:

            st.metric(
                "Risk Proxy",
                f"{assessment.get('risk_proxy_percent', 0):.2f}%"
            )

        with c2:

            st.metric(
                "Risk Band",
                assessment.get(
                    "risk_band",
                    "UNKNOWN"
                )
            )

        with c3:

            st.metric(
                "Evidence Quality",
                f"{assessment.get('evidence_quality', 0):.1f}/100"
            )

        with c4:

            st.metric(
                "Confidence",
                assessment.get(
                    "confidence",
                    "UNKNOWN"
                )
            )


        st.markdown("### Policy Decision")

        policy = assessment.get(
            "policy_decision",
            "UNKNOWN"
        )

        if policy == "PASS_TO_LENDER_POLICY":

            st.success(
                f"### {policy}"
            )

        elif policy == "MANUAL_REVIEW":

            st.warning(
                f"### {policy}"
            )

        elif policy == "INSUFFICIENT_EVIDENCE":

            st.error(
                f"### {policy}"
            )

        else:

            st.info(
                f"### {policy}"
            )


        c1, c2 = st.columns(2)

        with c1:

            st.markdown(
                "### Factors Supporting Lower Risk"
            )

            factors = assessment.get(
                "positive_factors",
                []
            )

            if factors:

                for item in factors:

                    st.write(
                        f"✓ {item}"
                    )

            else:

                st.write(
                    "No major positive behavioural signal identified."
                )


        with c2:

            st.markdown(
                "### Factors Increasing Concern"
            )

            factors = assessment.get(
                "risk_factors",
                []
            )

            if factors:

                for item in factors:

                    st.write(
                        f"⚠ {item}"
                    )

            else:

                st.write(
                    "No major adverse behavioural signal identified."
                )


        st.markdown(
            "### Evidence Limitations"
        )

        limitations = assessment.get(
            "evidence_limitations",
            []
        )

        if limitations:

            for item in limitations:

                st.write(
                    f"• {item}"
                )

        else:

            st.write(
                "No major evidence limitation identified."
            )


        st.markdown("### Assessment Metadata")

        metadata = {

            "Assessment ID":
                assessment.get(
                    "assessment_id",
                    "N/A"
                ),

            "Applicant ID":
                assessment.get(
                    "applicant_id",
                    "N/A"
                ),

            "History depth":
                assessment.get(
                    "history_depth",
                    "N/A"
                ),

            "Behavioural stability":
                assessment.get(
                    "behavioral_stability",
                    "N/A"
                ),

            "Model version":
                assessment.get(
                    "model_version",
                    "N/A"
                ),

            "Policy version":
                assessment.get(
                    "policy_version",
                    "N/A"
                ),

            "Generated at":
                assessment.get(
                    "generated_at",
                    "N/A"
                ),
        }

        st.json(metadata)


# =====================================================================
# RISK & CONFIDENCE
# =====================================================================
elif page == "Applicant Comparison":

    # ===============================================================
    # APPLICANT COMPARISON
    # ===============================================================

    st.markdown(
        '<div class="section-title">Applicant Comparison</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Compare two applicant profiles using the live Kavach "
        "assessment engine."
    )

    # ---------------------------------------------------------------
    # DEMO SCENARIOS
    # ---------------------------------------------------------------

    comparison_scenarios = {

        "Strong Established": {
            "applicant_id": 201,
            "description":
                "Complete history with strong and stable behaviour.",

            "payload": {
                "applicant_id": 201,
                "history_months": 12,
                "available_months": 12,
                "source_count": 3,
                "payment_success_rate": 0.98,
                "income_cv": 0.12,
                "cashflow_cv": 0.20,
                "balance_min": 40000,
                "inflow_to_outflow_ratio": 1.55,
                "income_trend": 0.04,
                "consent_granted": True,
            },
        },

        "Strong Behaviour / Thin File": {
            "applicant_id": 202,
            "description":
                "Excellent behaviour, but insufficient historical depth.",

            "payload": {
                "applicant_id": 202,
                "history_months": 2,
                "available_months": 2,
                "source_count": 3,
                "payment_success_rate": 0.98,
                "income_cv": 0.12,
                "cashflow_cv": 0.20,
                "balance_min": 40000,
                "inflow_to_outflow_ratio": 1.55,
                "income_trend": 0.04,
                "consent_granted": True,
            },
        },

        "Incomplete Evidence": {
            "applicant_id": 203,
            "description":
                "Long requested history, but substantial evidence is missing.",

            "payload": {
                "applicant_id": 203,
                "history_months": 12,
                "available_months": 7,
                "source_count": 2,
                "payment_success_rate": 0.96,
                "income_cv": 0.18,
                "cashflow_cv": 0.30,
                "balance_min": 25000,
                "inflow_to_outflow_ratio": 1.30,
                "income_trend": 0.01,
                "consent_granted": True,
            },
        },

        "Behavioural Deterioration": {
            "applicant_id": 204,
            "description":
                "Strong history, but poor and deteriorating behaviour.",

            "payload": {
                "applicant_id": 204,
                "history_months": 12,
                "available_months": 12,
                "source_count": 3,
                "payment_success_rate": 0.60,
                "income_cv": 0.50,
                "cashflow_cv": 0.80,
                "balance_min": 1000,
                "inflow_to_outflow_ratio": 0.70,
                "income_trend": -0.15,
                "consent_granted": True,
            },
        },
    }

    scenario_names = list(comparison_scenarios.keys())

    # ---------------------------------------------------------------
    # API STATUS
    # ---------------------------------------------------------------

    try:

        health_response = requests.get(
            f"{API_URL}/health",
            timeout=3
        )

        api_online = health_response.status_code == 200

    except requests.RequestException:

        api_online = False


    if not api_online:

        st.error(
            "Kavach API is offline. Start the live assessment API "
            "before running a comparison."
        )

        st.code(
            "python3 29_kavach_live_assessment_api.py",
            language="bash"
        )

        st.stop()


    st.success(
        "LIVE ENGINE CONNECTED • Comparison uses the Kavach API"
    )

    # ---------------------------------------------------------------
    # CORE PRINCIPLE
    # ---------------------------------------------------------------

    st.info(
        """
        **Kavach compares two independent dimensions:**

        **RISK** — What does the available behavioural evidence suggest?

        **CONFIDENCE** — How sufficient and reliable is that evidence?

        A low-risk estimate with weak evidence is not treated as
        equivalent to the same risk estimate supported by strong evidence.

        **RISK ≠ CONFIDENCE**
        """
    )

    # ---------------------------------------------------------------
    # PROFILE SELECTION
    # ---------------------------------------------------------------

    st.markdown("## 1. Select Two Profiles")

    col_a, col_b = st.columns(2)

    with col_a:

        st.markdown("### Applicant A")

        applicant_a = st.selectbox(
            "Choose Applicant A",
            scenario_names,
            index=0,
            key="comparison_applicant_a",
        )

        scenario_a = comparison_scenarios[applicant_a]

        st.caption(
            scenario_a["description"]
        )


    with col_b:

        st.markdown("### Applicant B")

        applicant_b = st.selectbox(
            "Choose Applicant B",
            scenario_names,
            index=1,
            key="comparison_applicant_b",
        )

        scenario_b = comparison_scenarios[applicant_b]

        st.caption(
            scenario_b["description"]
        )


    # ---------------------------------------------------------------
    # PROFILE INPUT PREVIEW
    # ---------------------------------------------------------------

    with st.expander(
        "View selected profile inputs",
        expanded=False
    ):

        input_col_a, input_col_b = st.columns(2)

        with input_col_a:

            st.markdown(
                f"**Applicant A — {applicant_a}**"
            )

            payload_a = scenario_a["payload"]

            st.write(
                f"History: {payload_a['history_months']} months"
            )

            st.write(
                f"Available: {payload_a['available_months']} months"
            )

            st.write(
                f"Payment success: "
                f"{payload_a['payment_success_rate']:.2f}"
            )

            st.write(
                f"Income volatility: "
                f"{payload_a['income_cv']:.2f}"
            )

            st.write(
                f"Cash-flow volatility: "
                f"{payload_a['cashflow_cv']:.2f}"
            )

            st.write(
                f"Minimum balance: "
                f"₹{payload_a['balance_min']:,.0f}"
            )

            st.write(
                f"Inflow/outflow: "
                f"{payload_a['inflow_to_outflow_ratio']:.2f}"
            )

            st.write(
                f"Income trend: "
                f"{payload_a['income_trend']:+.2f}"
            )


        with input_col_b:

            st.markdown(
                f"**Applicant B — {applicant_b}**"
            )

            payload_b = scenario_b["payload"]

            st.write(
                f"History: {payload_b['history_months']} months"
            )

            st.write(
                f"Available: {payload_b['available_months']} months"
            )

            st.write(
                f"Payment success: "
                f"{payload_b['payment_success_rate']:.2f}"
            )

            st.write(
                f"Income volatility: "
                f"{payload_b['income_cv']:.2f}"
            )

            st.write(
                f"Cash-flow volatility: "
                f"{payload_b['cashflow_cv']:.2f}"
            )

            st.write(
                f"Minimum balance: "
                f"₹{payload_b['balance_min']:,.0f}"
            )

            st.write(
                f"Inflow/outflow: "
                f"{payload_b['inflow_to_outflow_ratio']:.2f}"
            )

            st.write(
                f"Income trend: "
                f"{payload_b['income_trend']:+.2f}"
            )


    # ---------------------------------------------------------------
    # RUN COMPARISON
    # ---------------------------------------------------------------

    st.markdown("## 2. Live Comparison")

    if st.button(
        "⚡ Run Live Comparison",
        type="primary",
        width="stretch",
        key="run_applicant_comparison",
    ):

        with st.spinner(
            "Running both applicants through the live Kavach engine..."
        ):

            try:

                response_a = requests.post(
                    f"{API_URL}/assess",
                    json=scenario_a["payload"],
                    timeout=10,
                )

                response_b = requests.post(
                    f"{API_URL}/assess",
                    json=scenario_b["payload"],
                    timeout=10,
                )

            except requests.RequestException as exc:

                st.error(
                    f"Unable to connect to Kavach API: {exc}"
                )

                st.stop()


        if (
            response_a.status_code != 200
            or response_b.status_code != 200
        ):

            st.error(
                "One or both assessments were rejected by the Kavach API."
            )

            if response_a.status_code != 200:

                st.code(
                    response_a.text,
                    language="json"
                )

            if response_b.status_code != 200:

                st.code(
                    response_b.text,
                    language="json"
                )

            st.stop()


        result_a = response_a.json()
        result_b = response_b.json()

        st.session_state.comparison_result_a = result_a
        st.session_state.comparison_result_b = result_b
        st.session_state.comparison_name_a = applicant_a
        st.session_state.comparison_name_b = applicant_b


    # ---------------------------------------------------------------
    # DISPLAY SAVED COMPARISON
    # ---------------------------------------------------------------

    if (
        "comparison_result_a" not in st.session_state
        or "comparison_result_b" not in st.session_state
    ):

        st.info(
            "Select two profiles and click **Run Live Comparison** "
            "to generate the side-by-side assessment."
        )

    else:

        result_a = st.session_state.comparison_result_a
        result_b = st.session_state.comparison_result_b

        name_a = st.session_state.comparison_name_a
        name_b = st.session_state.comparison_name_b

        # -----------------------------------------------------------
        # HELPER
        # -----------------------------------------------------------

        def comparison_value(result, *keys, default="N/A"):

            for key in keys:

                value = result.get(key)

                if value is not None:
                    return value

            return default


        risk_a = comparison_value(
            result_a,
            "risk_proxy",
            "risk",
            "risk_score",
            default=0,
        )

        risk_b = comparison_value(
            result_b,
            "risk_proxy",
            "risk",
            "risk_score",
            default=0,
        )

        evidence_a = comparison_value(
            result_a,
            "evidence_quality",
            "evidence_score",
            default=0,
        )

        evidence_b = comparison_value(
            result_b,
            "evidence_quality",
            "evidence_score",
            default=0,
        )

        confidence_a = comparison_value(
            result_a,
            "confidence",
            default="N/A",
        )

        confidence_b = comparison_value(
            result_b,
            "confidence",
            default="N/A",
        )

        risk_band_a = comparison_value(
            result_a,
            "risk_band",
            default="N/A",
        )

        risk_band_b = comparison_value(
            result_b,
            "risk_band",
            default="N/A",
        )

        policy_a = comparison_value(
            result_a,
            "policy_decision",
            "policy",
            "policy_routing",
            default="N/A",
        )

        policy_b = comparison_value(
            result_b,
            "policy_decision",
            "policy",
            "policy_routing",
            default="N/A",
        )

        history_a = comparison_value(
            result_a,
            "history_depth",
            "history",
            default="N/A",
        )

        history_b = comparison_value(
            result_b,
            "history_depth",
            "history",
            default="N/A",
        )

        # -----------------------------------------------------------
        # RESULTS HEADER
        # -----------------------------------------------------------

        st.markdown("## 3. Assessment Comparison")

        result_col_a, vs_col, result_col_b = st.columns(
            [5, 1, 5]
        )

        with result_col_a:

            st.markdown(
                f"### 🛡️ Applicant A"
            )

            st.caption(name_a)

        with vs_col:

            st.markdown(
                "<h2 style='text-align:center;'>VS</h2>",
                unsafe_allow_html=True
            )

        with result_col_b:

            st.markdown(
                f"### 🛡️ Applicant B"
            )

            st.caption(name_b)


        # -----------------------------------------------------------
        # TOP METRICS
        # -----------------------------------------------------------

        metric_a, metric_b = st.columns(2)

        with metric_a:

            st.metric(
                "Risk",
                (
                    f"{float(risk_a):.2f}%"
                    if isinstance(
                        risk_a,
                        (int, float)
                    )
                    else str(risk_a)
                )
            )

            st.metric(
                "Evidence Quality",
                (
                    f"{float(evidence_a):.1f}/100"
                    if isinstance(
                        evidence_a,
                        (int, float)
                    )
                    else str(evidence_a)
                )
            )

            st.metric(
                "Confidence",
                str(confidence_a)
            )


        with metric_b:

            st.metric(
                "Risk",
                (
                    f"{float(risk_b):.2f}%"
                    if isinstance(
                        risk_b,
                        (int, float)
                    )
                    else str(risk_b)
                )
            )

            st.metric(
                "Evidence Quality",
                (
                    f"{float(evidence_b):.1f}/100"
                    if isinstance(
                        evidence_b,
                        (int, float)
                    )
                    else str(evidence_b)
                )
            )

            st.metric(
                "Confidence",
                str(confidence_b)
            )


        # -----------------------------------------------------------
        # SIDE-BY-SIDE TABLE
        # -----------------------------------------------------------

        st.markdown("### Decision Matrix")

        comparison_table = {
            "Dimension": [
                "Risk",
                "Risk Band",
                "Evidence Quality",
                "Confidence",
                "History",
                "Policy Decision",
            ],

            "Applicant A": [
                (
                    f"{float(risk_a):.2f}%"
                    if isinstance(risk_a, (int, float))
                    else str(risk_a)
                ),
                str(risk_band_a),
                (
                    f"{float(evidence_a):.1f}/100"
                    if isinstance(evidence_a, (int, float))
                    else str(evidence_a)
                ),
                str(confidence_a),
                str(history_a),
                str(policy_a),
            ],

            "Applicant B": [
                (
                    f"{float(risk_b):.2f}%"
                    if isinstance(risk_b, (int, float))
                    else str(risk_b)
                ),
                str(risk_band_b),
                (
                    f"{float(evidence_b):.1f}/100"
                    if isinstance(evidence_b, (int, float))
                    else str(evidence_b)
                ),
                str(confidence_b),
                str(history_b),
                str(policy_b),
            ],
        }

        st.table(comparison_table)


        # -----------------------------------------------------------
        # DIFFERENCE ANALYSIS
        # -----------------------------------------------------------

        st.markdown("### Comparison Signals")

        difference_col_1, difference_col_2 = st.columns(2)

        if (
            isinstance(risk_a, (int, float))
            and isinstance(risk_b, (int, float))
        ):

            risk_difference = abs(
                float(risk_a) - float(risk_b)
            )

            if risk_a < risk_b:

                lower_risk = "Applicant A"

            elif risk_b < risk_a:

                lower_risk = "Applicant B"

            else:

                lower_risk = "Neither — equal risk estimate"


        else:

            risk_difference = None
            lower_risk = "Unable to determine"


        if (
            isinstance(evidence_a, (int, float))
            and isinstance(evidence_b, (int, float))
        ):

            evidence_difference = abs(
                float(evidence_a) - float(evidence_b)
            )

            if evidence_a > evidence_b:

                stronger_evidence = "Applicant A"

            elif evidence_b > evidence_a:

                stronger_evidence = "Applicant B"

            else:

                stronger_evidence = "Neither — equal evidence"

        else:

            evidence_difference = None
            stronger_evidence = "Unable to determine"


        with difference_col_1:

            if risk_difference is not None:

                st.metric(
                    "Risk Difference",
                    f"{risk_difference:.2f} percentage points"
                )

            st.info(
                f"**Lower estimated risk:** {lower_risk}"
            )


        with difference_col_2:

            if evidence_difference is not None:

                st.metric(
                    "Evidence Difference",
                    f"{evidence_difference:.1f} points"
                )

            st.info(
                f"**Stronger evidence:** {stronger_evidence}"
            )


        # -----------------------------------------------------------
        # RISK ≠ CONFIDENCE EXPLANATION
        # -----------------------------------------------------------

        st.markdown("### Why the Results Differ")

        explanation_col_a, explanation_col_b = st.columns(2)

        supporting_a = comparison_value(
            result_a,
            "factors_supporting_lower_risk",
            "supporting_factors",
            default=[],
        )

        supporting_b = comparison_value(
            result_b,
            "factors_supporting_lower_risk",
            "supporting_factors",
            default=[],
        )

        concern_a = comparison_value(
            result_a,
            "factors_increasing_concern",
            "concern_factors",
            default=[],
        )

        concern_b = comparison_value(
            result_b,
            "factors_increasing_concern",
            "concern_factors",
            default=[],
        )


        with explanation_col_a:

            st.markdown(
                f"#### {name_a}"
            )

            st.markdown("**Factors supporting lower risk**")

            if isinstance(supporting_a, list) and supporting_a:

                for factor in supporting_a:

                    st.write(
                        f"✓ {factor}"
                    )

            else:

                st.write(
                    "No supporting factors returned."
                )

            st.markdown("**Factors increasing concern**")

            if isinstance(concern_a, list) and concern_a:

                for factor in concern_a:

                    st.write(
                        f"⚠ {factor}"
                    )

            else:

                st.write(
                    "No major concern identified."
                )


        with explanation_col_b:

            st.markdown(
                f"#### {name_b}"
            )

            st.markdown("**Factors supporting lower risk**")

            if isinstance(supporting_b, list) and supporting_b:

                for factor in supporting_b:

                    st.write(
                        f"✓ {factor}"
                    )

            else:

                st.write(
                    "No supporting factors returned."
                )

            st.markdown("**Factors increasing concern**")

            if isinstance(concern_b, list) and concern_b:

                for factor in concern_b:

                    st.write(
                        f"⚠ {factor}"
                    )

            else:

                st.write(
                    "No major concern identified."
                )


        # -----------------------------------------------------------
        # EVIDENCE LIMITATIONS
        # -----------------------------------------------------------

        limitations_a = comparison_value(
            result_a,
            "evidence_limitations",
            "limitations",
            default=[],
        )

        limitations_b = comparison_value(
            result_b,
            "evidence_limitations",
            "limitations",
            default=[],
        )

        st.markdown("### Evidence Limitations")

        limitation_col_a, limitation_col_b = st.columns(2)

        with limitation_col_a:

            st.markdown(
                f"**{name_a}**"
            )

            if isinstance(limitations_a, list) and limitations_a:

                for item in limitations_a:

                    st.warning(
                        str(item)
                    )

            else:

                st.success(
                    "No major evidence limitation identified."
                )


        with limitation_col_b:

            st.markdown(
                f"**{name_b}**"
            )

            if isinstance(limitations_b, list) and limitations_b:

                for item in limitations_b:

                    st.warning(
                        str(item)
                    )

            else:

                st.success(
                    "No major evidence limitation identified."
                )


        # -----------------------------------------------------------
        # FINAL INTERPRETATION
        # -----------------------------------------------------------

        st.markdown("### Kavach Interpretation")

        if lower_risk == stronger_evidence:

            st.success(
                f"**{lower_risk}** has both the lower estimated risk "
                f"and stronger evidence in this comparison."
            )

        else:

            st.info(
                f"""
                **Risk and evidence are telling different stories.**

                Lower estimated risk: **{lower_risk}**

                Stronger evidence: **{stronger_evidence}**

                This is exactly why Kavach does not treat risk as
                equivalent to confidence. A numerical risk estimate
                must be interpreted together with the quality and
                depth of the evidence supporting it.
                """
            )


        st.divider()

        st.caption(
            "Comparison results are generated from the live Kavach "
            "assessment API using prototype demonstration profiles."
        )

elif page == "Risk & Confidence":

    st.markdown(
        '<div class="section-title">Risk & Confidence</div>',
        unsafe_allow_html=True
    )

    st.info(
        """
        Kavach deliberately separates **risk estimation** from
        **evidence confidence**.

        This prevents a low estimated risk from automatically becoming
        a lending approval when the underlying evidence is weak.
        """
    )

    st.markdown("## Risk × Confidence Policy Matrix")

    matrix = [

        {
            "Risk": "LOW",
            "Confidence": "HIGH",
            "Policy Routing": "PASS / LENDER POLICY",
        },

        {
            "Risk": "LOW",
            "Confidence": "MEDIUM",
            "Policy Routing": "MANUAL REVIEW",
        },

        {
            "Risk": "LOW",
            "Confidence": "LOW",
            "Policy Routing": "INSUFFICIENT EVIDENCE",
        },

        {
            "Risk": "MODERATE",
            "Confidence": "HIGH",
            "Policy Routing": "PASS / LENDER POLICY",
        },

        {
            "Risk": "MODERATE",
            "Confidence": "MEDIUM",
            "Policy Routing": "MANUAL REVIEW",
        },

        {
            "Risk": "MODERATE",
            "Confidence": "LOW",
            "Policy Routing": "INSUFFICIENT EVIDENCE",
        },

        {
            "Risk": "ELEVATED",
            "Confidence": "HIGH",
            "Policy Routing": "MANUAL REVIEW",
        },

        {
            "Risk": "ELEVATED",
            "Confidence": "MEDIUM",
            "Policy Routing": "MANUAL REVIEW",
        },

        {
            "Risk": "ELEVATED",
            "Confidence": "LOW",
            "Policy Routing": "INSUFFICIENT EVIDENCE",
        },

        {
            "Risk": "HIGH",
            "Confidence": "HIGH",
            "Policy Routing": "DECLINE / REVIEW",
        },

        {
            "Risk": "HIGH",
            "Confidence": "MEDIUM",
            "Policy Routing": "DECLINE / REVIEW",
        },

        {
            "Risk": "HIGH",
            "Confidence": "LOW",
            "Policy Routing": "INSUFFICIENT EVIDENCE",
        },
    ]

    st.dataframe(
        matrix,
        width="stretch",
        hide_index=True,
    )

    st.success(
        "A low-risk estimate supported by weak evidence "
        "is not treated as equivalent to the same risk "
        "supported by strong evidence."
    )


# =====================================================================
# VALIDATION
# =====================================================================

elif page == "Validation":

    st.markdown(
        '<div class="section-title">Prototype Validation</div>',
        unsafe_allow_html=True
    )

    report_path = (
        "kavach_final_validation_report.json"
    )

    try:

        with open(
            report_path,
            "r",
            encoding="utf-8"
        ) as file:

            report = json.load(file)


        st.success(
            "Final validation report loaded."
        )

        final_status = report.get(
            "final_status",
            {}
        )

        technical = final_status.get(
            "technical_validation",
            "UNKNOWN"
        )

        live = final_status.get(
            "live_scenario_validation",
            "UNKNOWN"
        )

        regression = final_status.get(
            "automated_regression",
            "UNKNOWN"
        )


        c1, c2, c3 = st.columns(3)

        with c1:

            st.metric(
                "Technical validation",
                technical
            )

        with c2:

            st.metric(
                "Live scenarios",
                live
            )

        with c3:

            st.metric(
                "Regression",
                regression
            )


        st.json(report)


    except FileNotFoundError:

        st.warning(
            "kavach_final_validation_report.json "
            "was not found."
        )

        st.info(
            "Run 32_kavach_final_validation_report.py first."
        )

    except Exception as exc:

        st.error(
            f"Unable to load validation report: {exc}"
        )


# =====================================================================
# GOVERNANCE
# =====================================================================

elif page == "Governance":

    st.markdown(
        '<div class="section-title">Governance</div>',
        unsafe_allow_html=True
    )

    st.info(
        """
        Kavach is designed as a governed decision-support prototype,
        not an autonomous lending approval system.
        """
    )

    st.markdown("## Governance Principles")

    governance_items = [

        "Explicit applicant consent",

        "Purpose-aware data processing",

        "Right-to-withdraw concept",

        "Risk and confidence separation",

        "Evidence-quality assessment",

        "Human review for uncertain cases",

        "Model version tracking",

        "Policy version tracking",

        "Assessment traceability",

        "Data and model provenance",

        "Fairness evaluation",

        "Temporal drift monitoring",

        "Cost-sensitive policy analysis",

        "Production regulatory review requirement",

    ]

    for item in governance_items:

        st.write(
            f"✓ {item}"
        )


    st.markdown("## Important Prototype Limitations")

    limitations = [

        "Synthetic behavioural data is not real borrower data.",

        "Risk proxy is not a calibrated probability of default.",

        "Prototype thresholds are not lender-approved thresholds.",

        "Home Credit benchmark data does not represent Kavach's target population.",

        "Production lending decisions must not be made from this prototype.",

        "Real deployment requires legal, regulatory, fairness and model governance review.",

    ]

    for item in limitations:

        st.warning(
            item
        )


# =====================================================================
# SYSTEM STATUS
# =====================================================================

elif page == "System Status":

    st.markdown(
        '<div class="section-title">System Status</div>',
        unsafe_allow_html=True
    )

    online, health = get_api_health()

    if online:

        st.success(
            "Kavach API is operational."
        )

        st.json(
            health
        )

    else:

        st.error(
            "Kavach API is unavailable."
        )

        st.code(
            health
        )


    st.markdown("## Architecture")

    st.code(
        """
┌───────────────────────────────────────────────┐
│              KAVACH COMMAND CENTER            │
│                  Streamlit UI                  │
└──────────────────────┬────────────────────────┘
                       │
                       │ HTTP POST /assess
                       ▼
┌───────────────────────────────────────────────┐
│                 KAVACH API                    │
│                  FastAPI                      │
│                    :8000                      │
└──────────────────────┬────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────┐
│            ASSESSMENT ENGINE                  │
│                                               │
│  Evidence → Confidence → Risk → Policy        │
│                         ↓                     │
│                    Explanation                │
└───────────────────────────────────────────────┘
        """,
        language="text"
    )


# =====================================================================
# FOOTER
# =====================================================================

st.divider()

st.caption(
    "Kavach Pulse — Evidence-aware alternative credit assessment "
    "prototype | KAVACH-PROTOTYPE-v2"
)
