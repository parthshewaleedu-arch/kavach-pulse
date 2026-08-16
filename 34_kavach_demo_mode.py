import requests
import streamlit as st


# =====================================================================
# KAVACH PULSE — DEMO MODE
# =====================================================================

st.set_page_config(
    page_title="Kavach Pulse — Demo Mode",
    page_icon="🛡️",
    layout="wide"
)


# =====================================================================
# CONFIGURATION
# =====================================================================

API_URL = "http://127.0.0.1:8000"


# =====================================================================
# SCENARIOS
# =====================================================================

SCENARIOS = {

    "STRONG ESTABLISHED": {

        "description":
            "Long history, complete evidence, stable income and strong payment behaviour.",

        "payload": {

            "applicant_id": 100,

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


    "THIN FILE": {

        "description":
            "Strong behavioural signals, but only two months of history.",

        "payload": {

            "applicant_id": 101,

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


    "INCOMPLETE EVIDENCE": {

        "description":
            "Long requested history, but substantial periods of evidence are missing.",

        "payload": {

            "applicant_id": 102,

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


    "BEHAVIOURAL DETERIORATION": {

        "description":
            "Poor payment consistency, volatile finances and deteriorating income.",

        "payload": {

            "applicant_id": 103,

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

        return None

    except requests.RequestException:

        return None


def assess(payload):

    try:

        response = requests.post(
            f"{API_URL}/assess",
            json=payload,
            timeout=10
        )

        return response

    except requests.RequestException as exc:

        return exc


# =====================================================================
# HEADER
# =====================================================================

st.markdown(
    """
    # 🛡️ KAVACH PULSE

    ## Live Demonstration Mode

    **Evidence → Confidence → Risk → Policy**
    """
)

st.caption(
    "Interactive prototype demonstration"
)

st.divider()


# =====================================================================
# API STATUS
# =====================================================================

health = check_api()

if health:

    st.success(
        f"API ONLINE • Engine {health.get('engine_version', 'N/A')} • "
        f"Model {health.get('model_version', 'N/A')} • "
        f"Policy {health.get('policy_version', 'N/A')}"
    )

else:

    st.error(
        "Kavach API is offline. Start 29_kavach_live_assessment_api.py first."
    )

    st.stop()


# =====================================================================
# PROTOTYPE WARNING
# =====================================================================

st.warning(
    """
    **PROTOTYPE**

    Risk Proxy is an illustrative prototype score,
    not a calibrated Probability of Default.

    No real lending decision should be made from this system.
    """
)


# =====================================================================
# SCENARIO SELECTION
# =====================================================================

st.markdown(
    "## Choose a Scenario"
)

st.write(
    "Select a scenario to demonstrate how Kavach separates "
    "behavioural risk from evidence confidence."
)


scenario_names = list(SCENARIOS.keys())


columns = st.columns(4)


selected_scenario = None


for index, name in enumerate(scenario_names):

    scenario = SCENARIOS[name]

    with columns[index]:

        st.markdown(
            f"### {name}"
        )

        st.caption(
            scenario["description"]
        )

        if st.button(
            f"Run {name}",
            key=f"run_{index}",
            width="stretch"
        ):

            selected_scenario = name


# =====================================================================
# RUN SELECTED SCENARIO
# =====================================================================

if selected_scenario is not None:

    scenario = SCENARIOS[selected_scenario]

    payload = scenario["payload"]

    st.divider()

    st.markdown(
        f"## Running: {selected_scenario}"
    )

    st.info(
        scenario["description"]
    )


    with st.expander(
        "View scenario inputs"
    ):

        st.json(payload)


    with st.spinner(
        "Running live Kavach assessment..."
    ):

        response = assess(payload)


    if isinstance(
        response,
        requests.RequestException
    ):

        st.error(
            f"API request failed: {response}"
        )

        st.stop()


    if response.status_code != 200:

        st.error(
            f"Assessment rejected — HTTP {response.status_code}"
        )

        try:

            st.json(
                response.json()
            )

        except Exception:

            st.code(
                response.text
            )

        st.stop()


    result = response.json()


    st.success(
        "Live assessment completed."
    )


    # =================================================================
    # PRIMARY RESULT
    # =================================================================

    st.markdown(
        "## Assessment Result"
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "Risk Proxy",
            f"{result.get('risk_proxy_percent', 0):.2f}%"
        )

    with c2:

        st.metric(
            "Risk Band",
            result.get(
                "risk_band",
                "UNKNOWN"
            )
        )

    with c3:

        st.metric(
            "Evidence Quality",
            f"{result.get('evidence_quality', 0):.1f}/100"
        )

    with c4:

        st.metric(
            "Confidence",
            result.get(
                "confidence",
                "UNKNOWN"
            )
        )


    # =================================================================
    # POLICY
    # =================================================================

    policy = result.get(
        "policy_decision",
        "UNKNOWN"
    )


    st.markdown(
        "### Policy Routing"
    )


    if policy == "PASS_TO_LENDER_POLICY":

        st.success(
            f"**{policy}**"
        )

    elif policy == "MANUAL_REVIEW":

        st.warning(
            f"**{policy}**"
        )

    elif policy == "INSUFFICIENT_EVIDENCE":

        st.error(
            f"**{policy}**"
        )

    else:

        st.info(
            f"**{policy}**"
        )


    # =================================================================
    # EVIDENCE + RISK
    # =================================================================

    st.markdown(
        "## Kavach Reasoning"
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "History Depth",
            result.get(
                "history_depth",
                "UNKNOWN"
            )
        )

    with c2:

        st.metric(
            "Behavioural Stability",
            result.get(
                "behavioral_stability",
                "N/A"
            )
        )

    with c3:

        st.metric(
            "Applicant ID",
            result.get(
                "applicant_id",
                "N/A"
            )
        )


    # =================================================================
    # EXPLANATION
    # =================================================================

    left, right = st.columns(2)


    with left:

        st.markdown(
            "### Factors Supporting Lower Risk"
        )

        factors = result.get(
            "positive_factors",
            []
        )

        if factors:

            for factor in factors:

                st.write(
                    f"✓ {factor}"
                )

        else:

            st.write(
                "No major positive behavioural signal identified."
            )


    with right:

        st.markdown(
            "### Factors Increasing Concern"
        )

        factors = result.get(
            "risk_factors",
            []
        )

        if factors:

            for factor in factors:

                st.write(
                    f"⚠ {factor}"
                )

        else:

            st.write(
                "No major adverse behavioural signal identified."
            )


    # =================================================================
    # EVIDENCE LIMITATIONS
    # =================================================================

    st.markdown(
        "### Evidence Limitations"
    )

    limitations = result.get(
        "evidence_limitations",
        []
    )

    if limitations:

        for limitation in limitations:

            st.write(
                f"• {limitation}"
            )

    else:

        st.write(
            "No major evidence limitation identified."
        )


    # =================================================================
    # ARCHITECTURAL INTERPRETATION
    # =================================================================

    st.divider()

    st.markdown(
        "## Why This Matters"
    )


    if selected_scenario == "THIN FILE":

        st.info(
            """
            **Strong behaviour does not automatically mean sufficient evidence.**

            Kavach sees positive behavioural signals, but the applicant
            has only a very short history.

            Therefore:

            **Low risk estimate + Low confidence → Insufficient Evidence**
            """
        )


    elif selected_scenario == "INCOMPLETE EVIDENCE":

        st.info(
            """
            **Missing evidence reduces confidence.**

            The applicant requested a long history, but only part of
            that history is available.

            Kavach therefore separates the behavioural assessment
            from the reliability of the evidence supporting it.
            """
        )


    elif selected_scenario == "BEHAVIOURAL DETERIORATION":

        st.info(
            """
            **Strong evidence does not hide poor behaviour.**

            The applicant has extensive evidence, but the observed
            behavioural signals indicate deterioration.

            Therefore the system can produce:

            **High confidence + elevated risk → Manual Review**
            """
        )


    else:

        st.success(
            """
            **Strong evidence + stable behaviour**

            The applicant has a complete history, strong payment
            consistency and healthy cash-flow characteristics.

            This produces a high-confidence, low-risk prototype
            assessment suitable for passing to lender policy.
            """
        )


    # =================================================================
    # RAW RESPONSE
    # =================================================================

    with st.expander(
        "View complete API response"
    ):

        st.json(
            result
        )


# =====================================================================
# FOOTER
# =====================================================================

st.divider()

st.caption(
    "Kavach Pulse • Live Prototype Demonstration"
)

st.caption(
    "RISK ≠ CONFIDENCE"
)

st.caption(
    "Risk Proxy is illustrative and is not a calibrated "
    "Probability of Default."
)
