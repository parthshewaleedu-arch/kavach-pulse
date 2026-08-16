import requests
import pandas as pd
import streamlit as st


# =====================================================================
# KAVACH PULSE — INTERACTIVE APPLICANT COMPARISON
# =====================================================================

st.set_page_config(
    page_title="Kavach Pulse — Comparison",
    page_icon="🛡️",
    layout="wide"
)


API_URL = "http://127.0.0.1:8000"


# =====================================================================
# SCENARIOS
# =====================================================================

SCENARIOS = {

    "Strong Established": {
        "applicant_id": 201,
        "description": "Complete history with strong and stable behaviour.",
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
            "consent_granted": True
        }
    },

    "Strong Behaviour / Thin File": {
        "applicant_id": 202,
        "description": "Excellent behaviour, but insufficient historical depth.",
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
            "consent_granted": True
        }
    },

    "Incomplete Evidence": {
        "applicant_id": 203,
        "description": "Long requested history, but substantial evidence is missing.",
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
            "consent_granted": True
        }
    },

    "Behavioural Deterioration": {
        "applicant_id": 204,
        "description": "Strong history, but poor and deteriorating behaviour.",
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
            "consent_granted": True
        }
    }
}


SCENARIO_NAMES = list(SCENARIOS.keys())


# =====================================================================
# API
# =====================================================================

def check_api():

    try:
        response = requests.get(
            f"{API_URL}/health",
            timeout=3
        )

        if response.status_code == 200:
            return response.json()

    except requests.RequestException:
        pass

    return None


def assess(payload):

    try:
        return requests.post(
            f"{API_URL}/assess",
            json=payload,
            timeout=10
        )

    except requests.RequestException as exc:
        return exc


# =====================================================================
# HEADER
# =====================================================================

st.title("🛡️ Kavach Pulse")

st.subheader(
    "Interactive Applicant Comparison"
)

st.caption(
    "Compare any two applicant profiles using the live Kavach assessment engine."
)


# =====================================================================
# API STATUS
# =====================================================================

health = check_api()

if health is None:

    st.error(
        "Kavach API is offline. Start 29_kavach_live_assessment_api.py first."
    )

    st.stop()


st.success(
    f"API ONLINE • Engine {health.get('engine_version', 'N/A')} • "
    f"Model {health.get('model_version', 'N/A')}"
)


# =====================================================================
# CORE PRINCIPLE
# =====================================================================

st.info(
    """
    ### Kavach separates two questions:

    **RISK** — What does the available behavioural evidence suggest?

    **CONFIDENCE** — How sufficient and reliable is that evidence?

    Therefore:

    ## RISK ≠ CONFIDENCE
    """
)


# =====================================================================
# SELECTION
# =====================================================================

st.markdown(
    "## Select Two Profiles"
)

col1, col2 = st.columns(2)


with col1:

    st.markdown(
        "### Applicant A"
    )

    applicant_a = st.selectbox(
        "Choose profile A",
        SCENARIO_NAMES,
        index=0,
        key="applicant_a"
    )

    st.caption(
        SCENARIOS[applicant_a]["description"]
    )


with col2:

    st.markdown(
        "### Applicant B"
    )

    applicant_b = st.selectbox(
        "Choose profile B",
        SCENARIO_NAMES,
        index=1,
        key="applicant_b"
    )

    st.caption(
        SCENARIOS[applicant_b]["description"]
    )


# =====================================================================
# PREVENT SAME PROFILE
# =====================================================================

if applicant_a == applicant_b:

    st.warning(
        "Select two different profiles to perform a meaningful comparison."
    )


# =====================================================================
# COMPARE BUTTON
# =====================================================================

compare = st.button(
    "⚖️ Compare Applicants",
    type="primary",
    width="stretch",
    disabled=(applicant_a == applicant_b)
)


# =====================================================================
# RUN COMPARISON
# =====================================================================

if compare:

    scenario_a = SCENARIOS[applicant_a]
    scenario_b = SCENARIOS[applicant_b]

    with st.spinner(
        "Running both applicants through Kavach..."
    ):

        response_a = assess(
            scenario_a["payload"]
        )

        response_b = assess(
            scenario_b["payload"]
        )


    # ---------------------------------------------------------------
    # Error handling
    # ---------------------------------------------------------------

    if isinstance(
        response_a,
        requests.RequestException
    ):

        st.error(
            f"Applicant A API error: {response_a}"
        )

        st.stop()


    if isinstance(
        response_b,
        requests.RequestException
    ):

        st.error(
            f"Applicant B API error: {response_b}"
        )

        st.stop()


    if response_a.status_code != 200:

        st.error(
            f"Applicant A assessment failed: "
            f"HTTP {response_a.status_code}"
        )

        st.stop()


    if response_b.status_code != 200:

        st.error(
            f"Applicant B assessment failed: "
            f"HTTP {response_b.status_code}"
        )

        st.stop()


    result_a = response_a.json()
    result_b = response_b.json()


    st.session_state["comparison_a"] = result_a
    st.session_state["comparison_b"] = result_b
    st.session_state["comparison_name_a"] = applicant_a
    st.session_state["comparison_name_b"] = applicant_b


# =====================================================================
# DISPLAY RESULTS
# =====================================================================

if (
    "comparison_a" in st.session_state
    and "comparison_b" in st.session_state
):

    result_a = st.session_state["comparison_a"]
    result_b = st.session_state["comparison_b"]

    name_a = st.session_state["comparison_name_a"]
    name_b = st.session_state["comparison_name_b"]


    st.divider()

    st.markdown(
        "## Live Comparison"
    )


    # ================================================================
    # APPLICANT HEADERS
    # ================================================================

    col1, col2, col3 = st.columns(
        [1, 0.2, 1]
    )


    with col1:

        st.markdown(
            f"## 👤 {name_a}"
        )

        st.caption(
            f"Applicant ID: {result_a.get('applicant_id', 'N/A')}"
        )


    with col2:

        st.markdown(
            "## VS"
        )


    with col3:

        st.markdown(
            f"## 👤 {name_b}"
        )

        st.caption(
            f"Applicant ID: {result_b.get('applicant_id', 'N/A')}"
        )


    # ================================================================
    # METRICS
    # ================================================================

    st.markdown(
        "### Assessment Metrics"
    )


    metrics = [
        ("Risk Proxy", "risk_proxy_percent", "%"),
        ("Evidence Quality", "evidence_quality", "/100"),
        ("Confidence", "confidence", ""),
        ("History Depth", "history_depth", ""),
        ("Behavioural Stability", "behavioral_stability", ""),
        ("Risk Band", "risk_band", ""),
        ("Policy Decision", "policy_decision", "")
    ]


    for label, key, suffix in metrics:

        col1, col2, col3 = st.columns(
            [1.5, 1, 1]
        )


        with col1:

            st.markdown(
                f"**{label}**"
            )


        with col2:

            value_a = result_a.get(
                key,
                "N/A"
            )

            if isinstance(
                value_a,
                float
            ):

                if key == "risk_proxy_percent":

                    value_a = f"{value_a:.2f}{suffix}"

                elif key == "evidence_quality":

                    value_a = f"{value_a:.1f}{suffix}"

                elif key == "behavioral_stability":

                    value_a = f"{value_a:.1f}"

            st.write(
                value_a
            )


        with col3:

            value_b = result_b.get(
                key,
                "N/A"
            )

            if isinstance(
                value_b,
                float
            ):

                if key == "risk_proxy_percent":

                    value_b = f"{value_b:.2f}{suffix}"

                elif key == "evidence_quality":

                    value_b = f"{value_b:.1f}{suffix}"

                elif key == "behavioral_stability":

                    value_b = f"{value_b:.1f}"

            st.write(
                value_b
            )


    # ================================================================
    # SIDE-BY-SIDE CARDS
    # ================================================================

    st.divider()

    col1, col2 = st.columns(2)


    with col1:

        st.markdown(
            f"### {name_a}"
        )

        st.metric(
            "Risk",
            f"{result_a.get('risk_proxy_percent', 0):.2f}%"
        )

        st.metric(
            "Evidence",
            f"{result_a.get('evidence_quality', 0):.1f}/100"
        )

        st.metric(
            "Confidence",
            result_a.get(
                "confidence",
                "N/A"
            )
        )

        st.write(
            f"**History:** "
            f"{result_a.get('history_depth', 'N/A')}"
        )

        st.write(
            f"**Policy:** "
            f"{result_a.get('policy_decision', 'N/A')}"
        )


    with col2:

        st.markdown(
            f"### {name_b}"
        )

        st.metric(
            "Risk",
            f"{result_b.get('risk_proxy_percent', 0):.2f}%"
        )

        st.metric(
            "Evidence",
            f"{result_b.get('evidence_quality', 0):.1f}/100"
        )

        st.metric(
            "Confidence",
            result_b.get(
                "confidence",
                "N/A"
            )
        )

        st.write(
            f"**History:** "
            f"{result_b.get('history_depth', 'N/A')}"
        )

        st.write(
            f"**Policy:** "
            f"{result_b.get('policy_decision', 'N/A')}"
        )


    # ================================================================
    # DIFFERENCE ANALYSIS
    # ================================================================

    st.divider()

    st.markdown(
        "## Difference Analysis"
    )


    risk_a = result_a.get(
        "risk_proxy_percent",
        0
    )

    risk_b = result_b.get(
        "risk_proxy_percent",
        0
    )


    evidence_a = result_a.get(
        "evidence_quality",
        0
    )

    evidence_b = result_b.get(
        "evidence_quality",
        0
    )


    stability_a = result_a.get(
        "behavioral_stability",
        0
    )

    stability_b = result_b.get(
        "behavioral_stability",
        0
    )


    c1, c2, c3 = st.columns(3)


    with c1:

        st.metric(
            "Risk Difference",
            f"{abs(risk_a - risk_b):.2f} percentage points"
        )


    with c2:

        st.metric(
            "Evidence Difference",
            f"{abs(evidence_a - evidence_b):.1f} points"
        )


    with c3:

        st.metric(
            "Behaviour Difference",
            f"{abs(stability_a - stability_b):.1f} points"
        )


    # ================================================================
    # EVIDENCE / RISK VISUAL
    # ================================================================

    st.divider()

    st.markdown(
        "## Risk vs Evidence"
    )


    chart_df = pd.DataFrame({

        "Risk Proxy": [
            risk_a,
            risk_b
        ],

        "Evidence Quality": [
            evidence_a,
            evidence_b
        ]

    }, index=[

        name_a,
        name_b

    ])


    st.bar_chart(
        chart_df,
        width="stretch"
    )


    # ================================================================
    # EXPLANATION
    # ================================================================

    st.divider()

    st.markdown(
        "## Explain the Difference"
    )


    positive_a = result_a.get(
        "positive_factors",
        []
    )

    positive_b = result_b.get(
        "positive_factors",
        []
    )


    risk_factors_a = result_a.get(
        "risk_factors",
        []
    )

    risk_factors_b = result_b.get(
        "risk_factors",
        []
    )


    col1, col2 = st.columns(2)


    with col1:

        st.markdown(
            f"### {name_a}"
        )

        st.markdown(
            "**Positive factors**"
        )

        for item in positive_a:

            st.write(
                f"✓ {item}"
            )


        st.markdown(
            "**Risk factors**"
        )

        for item in risk_factors_a:

            st.write(
                f"⚠ {item}"
            )


    with col2:

        st.markdown(
            f"### {name_b}"
        )

        st.markdown(
            "**Positive factors**"
        )

        for item in positive_b:

            st.write(
                f"✓ {item}"
            )


        st.markdown(
            "**Risk factors**"
        )

        for item in risk_factors_b:

            st.write(
                f"⚠ {item}"
            )


    # ================================================================
    # KEY INSIGHT
    # ================================================================

    st.divider()

    st.markdown(
        "## 🛡️ Kavach Insight"
    )


    confidence_a = result_a.get(
        "confidence",
        "N/A"
    )

    confidence_b = result_b.get(
        "confidence",
        "N/A"
    )


    policy_a = result_a.get(
        "policy_decision",
        "N/A"
    )

    policy_b = result_b.get(
        "policy_decision",
        "N/A"
    )


    history_a = result_a.get(
        "history_depth",
        "N/A"
    )

    history_b = result_b.get(
        "history_depth",
        "N/A"
    )


    if (
        confidence_a != confidence_b
        or policy_a != policy_b
    ):

        st.success(
            f"""
            **The two applicants are not supported by equivalent evidence.**

            {name_a}:
            **{confidence_a} confidence** •
            **{history_a} history** •
            **{policy_a}**

            {name_b}:
            **{confidence_b} confidence** •
            **{history_b} history** •
            **{policy_b}**

            Kavach therefore avoids treating their assessments
            as equivalent merely because their behavioural risk
            signals may appear similar.

            ### RISK ≠ CONFIDENCE
            """
        )

    else:

        st.info(
            """
            Both applicants currently produce the same confidence
            and policy category.

            Compare another pair to demonstrate the effect of
            evidence depth or behavioural deterioration.
            """
        )


    # ================================================================
    # RAW RESPONSES
    # ================================================================

    with st.expander(
        "View raw Applicant A response"
    ):

        st.json(
            result_a
        )


    with st.expander(
        "View raw Applicant B response"
    ):

        st.json(
            result_b
        )


# =====================================================================
# FOOTER
# =====================================================================

st.divider()

st.caption(
    "Kavach Pulse • Interactive comparison prototype"
)

st.caption(
    "Risk Proxy is illustrative and is NOT a calibrated Probability of Default."
)

st.caption(
    "RISK ≠ CONFIDENCE"
)
