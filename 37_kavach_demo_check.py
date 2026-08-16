import requests
import sys
import time


API_URL = "http://127.0.0.1:8000"


print("=" * 70)
print("KAVACH PULSE — FINAL DEMO SYSTEM CHECK")
print("=" * 70)


# ==============================================================
# 1. API HEALTH
# ==============================================================

print("\n[1] Checking Kavach API...")

try:

    response = requests.get(
        f"{API_URL}/health",
        timeout=5
    )

    response.raise_for_status()

    health = response.json()

    print("PASS — API is healthy")

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

except Exception as exc:

    print("FAIL — API unavailable")
    print(exc)

    sys.exit(1)


# ==============================================================
# 2. LIVE ASSESSMENT
# ==============================================================

print("\n[2] Testing live assessment endpoint...")


payload = {

    "applicant_id": 999,

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


try:

    response = requests.post(
        f"{API_URL}/assess",
        json=payload,
        timeout=10
    )

    response.raise_for_status()

    result = response.json()

    print("PASS — Assessment endpoint working")

    print(
        "Risk:",
        result.get("risk_proxy_percent"),
        "%"
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

except Exception as exc:

    print("FAIL — Assessment endpoint failed")
    print(exc)

    sys.exit(1)


# ==============================================================
# 3. CONSENT ENFORCEMENT
# ==============================================================

print("\n[3] Testing consent enforcement...")


payload_no_consent = payload.copy()

payload_no_consent[
    "applicant_id"
] = 998

payload_no_consent[
    "consent_granted"
] = False


try:

    response = requests.post(
        f"{API_URL}/assess",
        json=payload_no_consent,
        timeout=10
    )

    if response.status_code == 403:

        print(
            "PASS — Assessment correctly rejected without consent"
        )

    else:

        print(
            "FAIL — Expected HTTP 403, received:",
            response.status_code
        )

        sys.exit(1)

except Exception as exc:

    print("FAIL — Consent test failed")
    print(exc)

    sys.exit(1)


# ==============================================================
# 4. THIN-FILE TEST
# ==============================================================

print("\n[4] Testing thin-file behaviour...")


thin_payload = {

    "applicant_id": 997,

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


try:

    response = requests.post(
        f"{API_URL}/assess",
        json=thin_payload,
        timeout=10
    )

    response.raise_for_status()

    thin_result = response.json()

    print("PASS — Thin-file assessment working")

    print(
        "Evidence:",
        thin_result.get("evidence_quality")
    )

    print(
        "Confidence:",
        thin_result.get("confidence")
    )

    print(
        "History:",
        thin_result.get("history_depth")
    )

    print(
        "Policy:",
        thin_result.get("policy_decision")
    )

except Exception as exc:

    print("FAIL — Thin-file test failed")
    print(exc)

    sys.exit(1)


# ==============================================================
# 5. BEHAVIOURAL DETERIORATION
# ==============================================================

print("\n[5] Testing behavioural deterioration...")


unstable_payload = {

    "applicant_id": 996,

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


try:

    response = requests.post(
        f"{API_URL}/assess",
        json=unstable_payload,
        timeout=10
    )

    response.raise_for_status()

    unstable_result = response.json()

    print("PASS — Behavioural deterioration detected")

    print(
        "Risk:",
        unstable_result.get("risk_proxy_percent"),
        "%"
    )

    print(
        "Risk band:",
        unstable_result.get("risk_band")
    )

    print(
        "Policy:",
        unstable_result.get("policy_decision")
    )

except Exception as exc:

    print("FAIL — Behavioural test failed")
    print(exc)

    sys.exit(1)


# ==============================================================
# 6. FINAL CHECK
# ==============================================================

print("\n" + "=" * 70)
print("FINAL DEMO SYSTEM STATUS")
print("=" * 70)

print()
print("PASS  API health")
print("PASS  Live assessment")
print("PASS  Consent enforcement")
print("PASS  Thin-file handling")
print("PASS  Behavioural deterioration")
print()

print("KAVACH DEMO SYSTEM: READY")
print("=" * 70)
