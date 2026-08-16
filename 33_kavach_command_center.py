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

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 4px;
    }

    .subtitle {
        font-size: 18px;
        opacity: 0.70;
        margin-bottom: 30px;
    }

    .section-title {
        font-size: 28px;
        font-weight: 750;
        margin-top: 20px;
        margin-bottom: 15px;
    }

    .consent-card {
        border: 1px solid rgba(128,128,128,0.30);
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 10px;
    }

    .status-card {
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 15px;
    }

    .small-text {
        font-size: 13px;
        opacity: 0.70;
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

with st.sidebar:

    st.markdown(
        """
        # 🛡️ Kavach

        ### Command Center
        """
    )

    st.divider()

    st.markdown("### Navigation")

    page = st.radio(
        "Navigation",
        [
            "Live Assessment",
            "Risk & Confidence",
            "Validation",
            "Governance",
            "System Status",
        ],
        label_visibility="collapsed",
    )
    st.divider()

    if api_online:

        st.success("● API ONLINE")

        st.caption(
            f"Engine: {api_data.get('engine_version', 'Unknown')}"
        )

        st.caption(
            f"Model: {api_data.get('model_version', 'Unknown')}"
        )

        st.caption(
            f"Policy: {api_data.get('policy_version', 'Unknown')}"
        )

    else:

        st.error("● API OFFLINE")

        st.caption(
            "Start the Kavach API on port 8000."
        )


# =====================================================================
# HEADER
# =====================================================================

st.markdown(
    '<div class="main-title">🛡️ KAVACH PULSE</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Evidence-aware alternative credit assessment and policy intelligence platform'
    '</div>',
    unsafe_allow_html=True
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
