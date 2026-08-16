"""
======================================================================
KAVACH PULSE — AUTOMATED REGRESSION TEST SUITE
======================================================================

Purpose:
    Automatically validate the live Kavach API architecture.

This is a prototype regression suite.

It verifies:
    1. API health
    2. Successful assessment
    3. Thin-file evidence handling
    4. Incomplete evidence handling
    5. Behavioural deterioration detection
    6. Risk-confidence separation
    7. Consent enforcement
    8. Response schema integrity
    9. Value sanity checks

This does NOT establish production credit-model validity.
======================================================================
"""

import requests
import sys
from datetime import datetime


# ======================================================================
# CONFIGURATION
# ======================================================================

API_URL = "http://127.0.0.1:8000"

TIMEOUT = 10

tests = []



# ======================================================================
# TEST HELPERS
# ======================================================================

def record_test(
    name,
    passed,
    message
):

    tests.append({

        "test":
            name,

        "status":
            "PASS"
            if passed
            else
            "FAIL",

        "message":
            message
    })



def post_assessment(payload):

    return requests.post(

        f"{API_URL}/assess",

        json=payload,

        timeout=TIMEOUT
    )



# ======================================================================
# EXPECTED RESPONSE FIELDS
# ======================================================================

REQUIRED_FIELDS = {

    "assessment_id",

    "applicant_id",

    "risk_proxy",

    "risk_proxy_percent",

    "risk_band",

    "evidence_quality",

    "confidence",

    "history_depth",

    "behavioral_stability",

    "policy_decision",

    "positive_factors",

    "risk_factors",

    "evidence_limitations",

    "model_version",

    "policy_version",

    "generated_at"
}



# ======================================================================
# TEST PAYLOADS
# ======================================================================

STRONG_APPLICANT = {

    "applicant_id": 9101,

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



THIN_FILE_APPLICANT = {

    "applicant_id": 9102,

    "history_months": 2,

    "available_months": 2,

    "source_count": 2,

    "payment_success_rate": 0.98,

    "income_cv": 0.10,

    "cashflow_cv": 0.18,

    "balance_min": 40000,

    "inflow_to_outflow_ratio": 1.60,

    "income_trend": 0.05,

    "consent_granted": True
}



INCOMPLETE_APPLICANT = {

    "applicant_id": 9103,

    "history_months": 12,

    "available_months": 5,

    "source_count": 2,

    "payment_success_rate": 0.95,

    "income_cv": 0.20,

    "cashflow_cv": 0.35,

    "balance_min": 20000,

    "inflow_to_outflow_ratio": 1.25,

    "income_trend": 0.00,

    "consent_granted": True
}



UNSTABLE_APPLICANT = {

    "applicant_id": 9104,

    "history_months": 12,

    "available_months": 12,

    "source_count": 3,

    "payment_success_rate": 0.65,

    "income_cv": 0.50,

    "cashflow_cv": 0.80,

    "balance_min": 3000,

    "inflow_to_outflow_ratio": 0.85,

    "income_trend": -0.10,

    "consent_granted": True
}



THIN_STRONG_BEHAVIOUR = {

    "applicant_id": 9105,

    "history_months": 2,

    "available_months": 2,

    "source_count": 3,

    "payment_success_rate": 1.00,

    "income_cv": 0.05,

    "cashflow_cv": 0.10,

    "balance_min": 100000,

    "inflow_to_outflow_ratio": 1.80,

    "income_trend": 0.10,

    "consent_granted": True
}



NO_CONSENT_APPLICANT = {

    "applicant_id": 9106,

    "history_months": 12,

    "available_months": 12,

    "source_count": 3,

    "payment_success_rate": 0.98,

    "income_cv": 0.10,

    "cashflow_cv": 0.20,

    "balance_min": 50000,

    "inflow_to_outflow_ratio": 1.60,

    "income_trend": 0.05,

    "consent_granted": False
}



# ======================================================================
# HEADER
# ======================================================================

print("=" * 70)

print(
    "KAVACH PULSE — AUTOMATED REGRESSION TEST SUITE"
)

print("=" * 70)

print()

print(
    "API:",
    API_URL
)

print(
    "Tests:",
    10
)

print()



# ======================================================================
# TEST 1 — HEALTH
# ======================================================================

print("[1] API HEALTH")

try:

    response = requests.get(

        f"{API_URL}/health",

        timeout=TIMEOUT
    )

    passed = (

        response.status_code == 200

        and

        response.json().get("status")
        == "healthy"
    )

    record_test(

        "API health",

        passed,

        (
            "API healthy"
            if passed
            else
            response.text
        )
    )

except Exception as e:

    record_test(

        "API health",

        False,

        str(e)
    )



# ======================================================================
# FUNCTION FOR VALID ASSESSMENT TESTS
# ======================================================================

def run_valid_test(

    test_number,

    name,

    payload
):

    print()

    print(
        f"[{test_number}] {name}"
    )

    try:

        response = post_assessment(
            payload
        )

        if response.status_code != 200:

            record_test(

                name,

                False,

                f"HTTP {response.status_code}"
            )

            print(
                "FAIL:",
                response.text
            )

            return None


        result = response.json()


        missing = (

            REQUIRED_FIELDS
            -
            set(result.keys())
        )


        if missing:

            record_test(

                name,

                False,

                f"Missing fields: {sorted(missing)}"
            )

            print(
                "FAIL: missing fields",
                missing
            )

            return None


        risk = result["risk_proxy"]

        evidence = result[
            "evidence_quality"
        ]

        confidence = result[
            "confidence"
        ]


        sanity = (

            0 <= risk <= 1

            and

            0 <= evidence <= 100

            and

            confidence
            in {
                "HIGH",
                "MEDIUM",
                "LOW"
            }
        )


        record_test(

            name,

            sanity,

            (
                "Valid response and values"
                if sanity
                else
                "Invalid response values"
            )
        )


        print(
            "Risk:",
            result["risk_proxy_percent"],
            "%"
        )

        print(
            "Evidence:",
            result["evidence_quality"]
        )

        print(
            "Confidence:",
            result["confidence"]
        )

        print(
            "Policy:",
            result["policy_decision"]
        )


        return result


    except Exception as e:

        record_test(

            name,

            False,

            str(e)
        )

        print(
            "FAIL:",
            e
        )

        return None



# ======================================================================
# TEST 2 — STRONG APPLICANT
# ======================================================================

strong = run_valid_test(

    2,

    "Strong applicant",

    STRONG_APPLICANT
)



# ======================================================================
# TEST 3 — THIN FILE
# ======================================================================

thin = run_valid_test(

    3,

    "Thin-file handling",

    THIN_FILE_APPLICANT
)



# ======================================================================
# TEST 4 — INCOMPLETE EVIDENCE
# ======================================================================

incomplete = run_valid_test(

    4,

    "Incomplete evidence handling",

    INCOMPLETE_APPLICANT
)



# ======================================================================
# TEST 5 — UNSTABLE BEHAVIOUR
# ======================================================================

unstable = run_valid_test(

    5,

    "Behavioural deterioration",

    UNSTABLE_APPLICANT
)



# ======================================================================
# TEST 6 — RISK VS CONFIDENCE
# ======================================================================

thin_strong = run_valid_test(

    6,

    "Risk-confidence separation",

    THIN_STRONG_BEHAVIOUR
)


if thin_strong is not None:

    passed = (

        thin_strong["confidence"]
        == "LOW"

        and

        thin_strong["policy_decision"]
        == "INSUFFICIENT_EVIDENCE"
    )

    record_test(

        "Thin strong-behaviour separation",

        passed,

        (
            "Good behaviour did not override thin evidence"
            if passed
            else
            "Risk-confidence separation failed"
        )
    )



# ======================================================================
# TEST 7 — CONSENT ENFORCEMENT
# ======================================================================

print()

print(
    "[7] Consent enforcement"
)

try:

    response = post_assessment(

        NO_CONSENT_APPLICANT
    )

    passed = (

        response.status_code
        == 403
    )

    record_test(

        "Consent enforcement",

        passed,

        (
            "403 correctly returned"
            if passed
            else
            f"Expected 403, received {response.status_code}"
        )
    )

    print(
        "HTTP:",
        response.status_code
    )

except Exception as e:

    record_test(

        "Consent enforcement",

        False,

        str(e)
    )



# ======================================================================
# TEST 8 — STRONG VS UNSTABLE RISK
# ======================================================================

print()

print(
    "[8] Behavioural risk ordering"
)

if (

    strong is not None

    and

    unstable is not None
):

    passed = (

        unstable["risk_proxy"]
        >
        strong["risk_proxy"]
    )

    record_test(

        "Risk ordering",

        passed,

        (
            "Unstable behaviour produced higher risk"
            if passed
            else
            "Risk ordering failed"
        )
    )

else:

    record_test(

        "Risk ordering",

        False,

        "Required assessments unavailable"
    )



# ======================================================================
# TEST 9 — THIN FILE EVIDENCE
# ======================================================================

print()

print(
    "[9] Evidence depth ordering"
)

if (

    strong is not None

    and

    thin is not None
):

    passed = (

        thin["evidence_quality"]
        <
        strong["evidence_quality"]

        and

        thin["confidence"]
        !=
        "HIGH"
    )

    record_test(

        "Evidence depth ordering",

        passed,

        (
            "Thin file has weaker evidence/confidence"
            if passed
            else
            "Evidence depth logic failed"
        )
    )

else:

    record_test(

        "Evidence depth ordering",

        False,

        "Required assessments unavailable"
    )



# ======================================================================
# TEST 10 — RESPONSE MODEL VERSION
# ======================================================================

print()

print(
    "[10] Model and policy version"
)

if strong is not None:

    passed = (

        bool(
            strong["model_version"]
        )

        and

        bool(
            strong["policy_version"]
        )
    )

    record_test(

        "Version metadata",

        passed,

        (
            "Model and policy versions present"
            if passed
            else
            "Version metadata missing"
        )
    )

else:

    record_test(

        "Version metadata",

        False,

        "Strong assessment unavailable"
    )



# ======================================================================
# FINAL RESULTS
# ======================================================================

print()

print("=" * 70)

print(
    "REGRESSION TEST RESULTS"
)

print("=" * 70)

print()


for test in tests:

    print(

        f"{test['status']:4} "
        f"{test['test']}"
    )

    print(

        "     ",
        test["message"]
    )



total = len(tests)

passed = sum(

    test["status"] == "PASS"

    for test in tests
)

failed = total - passed



print()

print(
    "Total tests :",
    total
)

print(
    "Passed      :",
    passed
)

print(
    "Failed      :",
    failed
)



# ======================================================================
# SAVE RESULTS
# ======================================================================

timestamp = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)

output_file = (

    f"kavach_regression_results_"
    f"{timestamp}.csv"
)


import pandas as pd


pd.DataFrame(
    tests
).to_csv(

    output_file,

    index=False
)


print()

print(
    "Saved:"
)

print(
    " ",
    output_file
)



# ======================================================================
# FINAL STATUS
# ======================================================================

print()

print("=" * 70)

if failed == 0:

    print(
        "OVERALL STATUS: PASS"
    )

    print(
        "Kavach regression suite passed."
    )

else:

    print(
        "OVERALL STATUS: FAIL"
    )

    print(
        "One or more regression tests failed."
    )

print("=" * 70)


if failed > 0:

    sys.exit(1)
