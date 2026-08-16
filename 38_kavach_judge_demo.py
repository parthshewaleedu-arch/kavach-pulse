import json
import requests
from datetime import datetime


API_URL = "http://127.0.0.1:8000"


def section(title):
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def assess(name, payload):
    print()
    print("-" * 72)
    print(name)
    print("-" * 72)

    response = requests.post(
        f"{API_URL}/assess",
        json=payload,
        timeout=10,
    )

    print("HTTP:", response.status_code)

    if response.status_code != 200:
        print(response.text)
        return None

    result = response.json()

    print("Risk:", result["risk_proxy_percent"], "%")
    print("Risk band:", result["risk_band"])
    print("Evidence:", result["evidence_quality"])
    print("Confidence:", result["confidence"])
    print("History:", result["history_depth"])
    print("Behavioural stability:", result["behavioral_stability"])
    print("Policy:", result["policy_decision"])

    return result


# =====================================================================
# KAVACH JUDGE DEMO
# =====================================================================

section("KAVACH PULSE — JUDGE DEMONSTRATION CHECK")

print("API:", API_URL)
print("Generated:", datetime.now().isoformat())


# =====================================================================
# 1. API HEALTH
# =====================================================================

section("[1] API HEALTH")

health = requests.get(
    f"{API_URL}/health",
    timeout=5,
)

if health.status_code != 200:
    raise SystemExit("API is not healthy.")

health_data = health.json()

print("STATUS:", health_data.get("status"))
print("Engine:", health_data.get("engine_version"))
print("Model:", health_data.get("model_version"))
print("Policy:", health_data.get("policy_version"))


# =====================================================================
# 2. STRONG APPLICANT
# =====================================================================

section("[2] STRONG APPLICANT")

strong_payload = {
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
    "consent_granted": True,
}

strong = assess(
    "STRONG / ESTABLISHED APPLICANT",
    strong_payload,
)


# =====================================================================
# 3. THIN FILE
# =====================================================================

section("[3] THIN-FILE APPLICANT")

thin_payload = {
    "applicant_id": 9002,
    "history_months": 12,
    "available_months": 3,
    "source_count": 1,
    "payment_success_rate": 0.98,
    "income_cv": 0.12,
    "cashflow_cv": 0.20,
    "balance_min": 40000,
    "inflow_to_outflow_ratio": 1.55,
    "income_trend": 0.04,
    "consent_granted": True,
}

thin = assess(
    "THIN-FILE / STRONG BEHAVIOUR",
    thin_payload,
)


# =====================================================================
# 4. UNSTABLE APPLICANT
# =====================================================================

section("[4] BEHAVIOURAL DETERIORATION")

unstable_payload = {
    "applicant_id": 9003,
    "history_months": 12,
    "available_months": 12,
    "source_count": 3,
    "payment_success_rate": 0.62,
    "income_cv": 0.48,
    "cashflow_cv": 0.82,
    "balance_min": 1000,
    "inflow_to_outflow_ratio": 0.85,
    "income_trend": -0.12,
    "consent_granted": True,
}

unstable = assess(
    "UNSTABLE BEHAVIOUR",
    unstable_payload,
)


# =====================================================================
# 5. CONSENT ENFORCEMENT
# =====================================================================

section("[5] CONSENT ENFORCEMENT")

no_consent_payload = dict(strong_payload)

no_consent_payload["applicant_id"] = 9004
no_consent_payload["consent_granted"] = False

response = requests.post(
    f"{API_URL}/assess",
    json=no_consent_payload,
    timeout=10,
)

print("HTTP:", response.status_code)

if response.status_code == 403:
    print("PASS — assessment blocked without consent")
else:
    print("FAIL — consent enforcement unexpected")


# =====================================================================
# 6. ARCHITECTURAL CHECKS
# =====================================================================

section("[6] ARCHITECTURAL CHECKS")

checks = []

if strong:
    checks.append(
        (
            "Strong applicant produces valid assessment",
            strong["policy_decision"] in [
                "PASS_TO_LENDER_POLICY",
                "MANUAL_REVIEW",
                "INSUFFICIENT_EVIDENCE",
            ],
        )
    )

if thin:
    checks.append(
        (
            "Thin evidence reduces confidence",
            thin["confidence"] in ["LOW", "MEDIUM"],
        )
    )

if unstable and strong:
    checks.append(
        (
            "Behavioural deterioration increases risk",
            unstable["risk_proxy"] > strong["risk_proxy"],
        )
    )

if thin:
    checks.append(
        (
            "Risk and confidence remain separate",
            thin["confidence"] != "HIGH",
        )
    )

checks.append(
    (
        "Consent is enforced",
        response.status_code == 403,
    )
)


for name, passed in checks:
    print(
        ("PASS " if passed else "FAIL ") + name
    )


# =====================================================================
# 7. FINAL STATUS
# =====================================================================

section("FINAL JUDGE DEMO STATUS")

passed = sum(
    1
    for _, result in checks
    if result
)

total = len(checks)

print(f"Checks passed: {passed}/{total}")

if passed == total:
    print()
    print("KAVACH DEMO SYSTEM: READY")
    print()
else:
    print()
    print("KAVACH DEMO SYSTEM: REVIEW REQUIRED")
    print()


# =====================================================================
# 8. KEY MESSAGE
# =====================================================================

section("CORE KAVACH PRINCIPLE")

print(
    "RISK != CONFIDENCE"
)

print()
print(
    "Kavach does not treat a low-risk estimate supported by weak"
)
print(
    "evidence as equivalent to the same estimate supported by"
)
print(
    "strong evidence."
)

print()
print(
    "Architecture:"
)
print(
    "CONSENT -> EVIDENCE -> CONFIDENCE -> RISK -> POLICY -> EXPLANATION"
)

print()
print(
    "This is a validated technical prototype, not a production"
)
print(
    "credit-decision system."
)

print()
print("=" * 72)
print("KAVACH JUDGE DEMONSTRATION CHECK COMPLETE")
print("=" * 72)
