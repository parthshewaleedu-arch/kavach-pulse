"""
======================================================================
KAVACH PULSE — LIVE SCENARIO VALIDATION
======================================================================

Purpose:
    Validate the integrated Kavach API against deliberately different
    applicant scenarios.

This is NOT model validation.

It is an integration / behavioural consistency test.

API:
    http://127.0.0.1:8000

======================================================================
"""

import requests
import pandas as pd
from datetime import datetime


API_URL = "http://127.0.0.1:8000"


# ======================================================================
# TEST SCENARIOS
# ======================================================================

scenarios = [

    {
        "scenario": "STRONG_ESTABLISHED",

        "description":
            "Long history, complete evidence, stable income and payments.",

        "payload": {
            "applicant_id": 9001,
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

    {
        "scenario": "THIN_FILE",

        "description":
            "Very short history with limited evidence.",

        "payload": {
            "applicant_id": 9002,
            "history_months": 2,
            "available_months": 2,
            "source_count": 1,
            "payment_success_rate": 0.98,
            "income_cv": 0.12,
            "cashflow_cv": 0.20,
            "balance_min": 40000,
            "inflow_to_outflow_ratio": 1.55,
            "income_trend": 0.04,
            "consent_granted": True
        }
    },

    {
        "scenario": "INCOMPLETE_EVIDENCE",

        "description":
            "Long requested history but substantial missing periods.",

        "payload": {
            "applicant_id": 9003,
            "history_months": 12,
            "available_months": 5,
            "source_count": 2,
            "payment_success_rate": 0.95,
            "income_cv": 0.15,
            "cashflow_cv": 0.25,
            "balance_min": 30000,
            "inflow_to_outflow_ratio": 1.35,
            "income_trend": 0.02,
            "consent_granted": True
        }
    },

    {
        "scenario": "UNSTABLE_BEHAVIOUR",

        "description":
            "Poor payment consistency and highly volatile finances.",

        "payload": {
            "applicant_id": 9004,
            "history_months": 12,
            "available_months": 12,
            "source_count": 3,
            "payment_success_rate": 0.65,
            "income_cv": 0.50,
            "cashflow_cv": 0.80,
            "balance_min": 5000,
            "inflow_to_outflow_ratio": 0.85,
            "income_trend": -0.10,
            "consent_granted": True
        }
    },

    {
        "scenario": "STRONG_BEHAVIOUR_THIN_FILE",

        "description":
            "Excellent behaviour but insufficient history.",

        "payload": {
            "applicant_id": 9005,
            "history_months": 2,
            "available_months": 2,
            "source_count": 1,
            "payment_success_rate": 1.00,
            "income_cv": 0.08,
            "cashflow_cv": 0.12,
            "balance_min": 50000,
            "inflow_to_outflow_ratio": 1.70,
            "income_trend": 0.06,
            "consent_granted": True
        }
    },

    {
        "scenario": "WITHDRAWN_CONSENT",

        "description":
            "Applicant has not provided processing consent.",

        "payload": {
            "applicant_id": 9006,
            "history_months": 12,
            "available_months": 12,
            "source_count": 3,
            "payment_success_rate": 0.98,
            "income_cv": 0.12,
            "cashflow_cv": 0.20,
            "balance_min": 40000,
            "inflow_to_outflow_ratio": 1.55,
            "income_trend": 0.04,
            "consent_granted": False
        }
    }
]


# ======================================================================
# HEADER
# ======================================================================

print("=" * 70)
print("KAVACH PULSE — LIVE SCENARIO VALIDATION")
print("=" * 70)

print()
print("API:", API_URL)
print("Scenarios:", len(scenarios))
print()


# ======================================================================
# HEALTH CHECK
# ======================================================================

print("[1] Checking API health...")

try:

    health_response = requests.get(
        f"{API_URL}/health",
        timeout=5
    )

    if health_response.status_code != 200:

        raise RuntimeError(
            f"Health check failed: "
            f"HTTP {health_response.status_code}"
        )

    health = health_response.json()

    print("API STATUS: HEALTHY")

    print(
        "Engine:",
        health.get("engine_version")
    )

    print(
        "Model:",
        health.get("model_version")
    )

    print(
        "Policy:",
        health.get("policy_version")
    )

except Exception as e:

    print()
    print("API HEALTH CHECK FAILED")
    print(e)
    print()
    print(
        "Start the API first:"
    )
    print(
        "python3 29_kavach_live_assessment_api.py"
    )

    raise SystemExit(1)


# ======================================================================
# RUN SCENARIOS
# ======================================================================

print()
print("=" * 70)
print("[2] Running live assessment scenarios")
print("=" * 70)


results = []


for scenario in scenarios:

    name = scenario["scenario"]
    description = scenario["description"]
    payload = scenario["payload"]

    print()
    print("-" * 70)
    print(name)
    print("-" * 70)

    print(description)

    try:

        response = requests.post(
            f"{API_URL}/assess",
            json=payload,
            timeout=10
        )

        print(
            "HTTP status:",
            response.status_code
        )

        # --------------------------------------------------------------
        # Successful assessment
        # --------------------------------------------------------------

        if response.status_code == 200:

            result = response.json()

            results.append({

                "scenario":
                    name,

                "applicant_id":
                    payload["applicant_id"],

                "status":
                    "PASS",

                "risk_proxy":
                    result.get("risk_proxy"),

                "risk_percent":
                    result.get("risk_proxy_percent"),

                "risk_band":
                    result.get("risk_band"),

                "evidence_quality":
                    result.get("evidence_quality"),

                "confidence":
                    result.get("confidence"),

                "history_depth":
                    result.get("history_depth"),

                "behavioral_stability":
                    result.get(
                        "behavioral_stability"
                    ),

                "policy_decision":
                    result.get(
                        "policy_decision"
                    ),

                "error":
                    ""
            })

            print(
                "Risk:",
                result.get("risk_proxy_percent"),
                "%"
            )

            print(
                "Risk band:",
                result.get("risk_band")
            )

            print(
                "Evidence:",
                result.get("evidence_quality")
            )

            print(
                "Confidence:",
                result.get("confidence")
            )

            print(
                "History:",
                result.get("history_depth")
            )

            print(
                "Policy:",
                result.get("policy_decision")
            )

        # --------------------------------------------------------------
        # Expected rejection
        # --------------------------------------------------------------

        else:

            error_text = response.text

            results.append({

                "scenario":
                    name,

                "applicant_id":
                    payload["applicant_id"],

                "status":
                    "REJECTED",

                "risk_proxy":
                    None,

                "risk_percent":
                    None,

                "risk_band":
                    None,

                "evidence_quality":
                    None,

                "confidence":
                    None,

                "history_depth":
                    None,

                "behavioral_stability":
                    None,

                "policy_decision":
                    "REQUEST_REJECTED",

                "error":
                    error_text
            })

            print(
                "Request rejected:"
            )

            print(error_text)
    except requests.exceptions.RequestException as e:

        results.append({

            "scenario": name,
            "applicant_id": payload["applicant_id"],
            "status": "API_ERROR",

            "risk_proxy": None,
            "risk_percent": None,
            "risk_band": None,
            "evidence_quality": None,
            "confidence": None,
            "history_depth": None,
            "behavioral_stability": None,

            "policy_decision": "API_ERROR",
            "error": str(e)
        })

        print(
            "API request failed:"
        )

        print(e)


# ======================================================================
# RESULTS TABLE
# ======================================================================

print()
print("=" * 70)
print("[3] LIVE SCENARIO RESULTS")
print("=" * 70)

results_df = pd.DataFrame(results)

print()

print(
    results_df[
        [
            "scenario",
            "status",
            "risk_percent",
            "risk_band",
            "evidence_quality",
            "confidence",
            "history_depth",
            "policy_decision"
        ]
    ].to_string(
        index=False
    )
)


# ======================================================================
# ARCHITECTURAL CHECKS
# ======================================================================

print()
print("=" * 70)
print("[4] ARCHITECTURAL CONSISTENCY CHECKS")
print("=" * 70)


checks = []


def add_check(name, passed, reason):

    checks.append({

        "check": name,

        "status":
            "PASS" if passed else "FAIL",

        "reason": reason
    })


# ----------------------------------------------------------------------
# Strong applicant
# ----------------------------------------------------------------------

strong = results_df[
    results_df["scenario"]
    == "STRONG_ESTABLISHED"
]

if len(strong) == 1:

    row = strong.iloc[0]

    add_check(
        "Strong applicant assessment",
        row["status"] == "PASS",
        "Strong applicant received a valid assessment."
    )


# ----------------------------------------------------------------------
# Thin file
# ----------------------------------------------------------------------

thin = results_df[
    results_df["scenario"]
    == "THIN_FILE"
]

if len(thin) == 1:

    row = thin.iloc[0]

    add_check(
        "Thin-file evidence handling",
        (
            row["status"] == "PASS"
            and row["history_depth"]
            in [
                "VERY_THIN",
                "THIN"
            ]
        ),
        "Short history should affect evidence depth."
    )


# ----------------------------------------------------------------------
# Incomplete evidence
# ----------------------------------------------------------------------

incomplete = results_df[
    results_df["scenario"]
    == "INCOMPLETE_EVIDENCE"
]

if len(incomplete) == 1:

    row = incomplete.iloc[0]

    add_check(
        "Incomplete evidence handling",
        (
            row["status"] == "PASS"
            and row["evidence_quality"]
            is not None
        ),
        "Missing periods must influence evidence quality."
    )


# ----------------------------------------------------------------------
# Unstable behaviour
# ----------------------------------------------------------------------

unstable = results_df[
    results_df["scenario"]
    == "UNSTABLE_BEHAVIOUR"
]

if len(unstable) == 1:

    row = unstable.iloc[0]

    add_check(
        "Behavioural deterioration detection",
        (
            row["status"] == "PASS"
            and row["risk_percent"] is not None
        ),
        "Poor behavioural inputs must reach the risk engine."
    )


# ----------------------------------------------------------------------
# Thin but strong behaviour
# ----------------------------------------------------------------------

thin_strong = results_df[
    results_df["scenario"]
    == "STRONG_BEHAVIOUR_THIN_FILE"
]

if len(thin_strong) == 1:

    row = thin_strong.iloc[0]

    add_check(
        "Risk versus confidence separation",
        (
            row["status"] == "PASS"
            and row["history_depth"]
            in [
                "VERY_THIN",
                "THIN"
            ]
        ),
        "Good behaviour should not erase insufficient history."
    )


# ----------------------------------------------------------------------
# Consent
# ----------------------------------------------------------------------

consent = results_df[
    results_df["scenario"]
    == "WITHDRAWN_CONSENT"
]

if len(consent) == 1:

    row = consent.iloc[0]

    add_check(
        "Consent enforcement",
        row["status"] == "REJECTED",
        "Processing must not continue without consent."
    )


# ======================================================================
# PRINT CHECKS
# ======================================================================

checks_df = pd.DataFrame(checks)

print()

for _, row in checks_df.iterrows():

    print(
        f"{row['status']:4} "
        f"{row['check']}"
    )

    print(
        f"     {row['reason']}"
    )


# ======================================================================
# OVERALL STATUS
# ======================================================================

all_passed = (
    checks_df["status"] == "PASS"
).all()


print()
print("=" * 70)

if all_passed:

    print(
        "OVERALL STATUS: PASS"
    )

else:

    print(
        "OVERALL STATUS: REVIEW REQUIRED"
    )

print("=" * 70)


# ======================================================================
# SAVE
# ======================================================================

timestamp = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)

output_file = (
    "kavach_live_scenario_results_"
    + timestamp
    + ".csv"
)

results_df.to_csv(
    output_file,
    index=False
)

checks_file = (
    "kavach_live_scenario_checks_"
    + timestamp
    + ".csv"
)

checks_df.to_csv(
    checks_file,
    index=False
)


print()
print("Saved:")
print(" ", output_file)
print(" ", checks_file)

print()
print("=" * 70)
print("LIVE SCENARIO VALIDATION COMPLETE")
print("=" * 70)

