import pandas as pd
import uuid
from datetime import datetime, timedelta

print("=" * 70)
print("KAVACH PULSE — CONSENT + DATA GOVERNANCE ENGINE")
print("=" * 70)


# =========================================================
# 1. DATA SOURCES
# =========================================================

DATA_SOURCES = {

    "bank_cashflow": {
        "name": "Bank cash-flow history",
        "purpose": "Assess income stability, cash-flow behaviour and repayment capacity",
        "period": "Last 12 months",
        "sensitivity": "HIGH",
        "default_requested": True
    },

    "platform_income": {
        "name": "Platform income history",
        "purpose": "Assess income continuity and volatility",
        "period": "Last 12 months",
        "sensitivity": "HIGH",
        "default_requested": True
    },

    "repayment_history": {
        "name": "Repayment history",
        "purpose": "Assess payment consistency",
        "period": "Last 12 months",
        "sensitivity": "HIGH",
        "default_requested": True
    },

    "credit_bureau": {
        "name": "Credit bureau information",
        "purpose": "Assess existing credit obligations and repayment history",
        "period": "Current available history",
        "sensitivity": "HIGH",
        "default_requested": False
    },

    "location": {
        "name": "Location information",
        "purpose": "Not required for the core behavioural assessment",
        "period": "Not requested",
        "sensitivity": "HIGH",
        "default_requested": False
    }
}


# =========================================================
# 2. CONSENT RECORD
# =========================================================

def create_consent_record(
    applicant_id,
    selected_sources,
    purpose,
    duration_days=30
):

    consent_id = (
        "KVC-"
        +
        uuid.uuid4().hex[:12].upper()
    )

    timestamp = datetime.now()

    expiry = (
        timestamp
        +
        timedelta(
            days=duration_days
        )
    )

    return {

        "consent_id":
            consent_id,

        "applicant_id":
            applicant_id,

        "timestamp":
            timestamp.isoformat(),

        "expiry":
            expiry.isoformat(),

        "purpose":
            purpose,

        "selected_sources":
            ",".join(
                selected_sources
            ),

        "status":
            "ACTIVE",

        "withdrawn":
            False
    }


# =========================================================
# 3. CONSENT VALIDATION
# =========================================================

def validate_consent(record):

    required = [

        "consent_id",

        "applicant_id",

        "timestamp",

        "expiry",

        "purpose",

        "selected_sources",

        "status",

        "withdrawn"
    ]

    missing = [
        field
        for field in required
        if field not in record
    ]

    if missing:

        return False, (
            "Missing consent fields: "
            +
            ", ".join(missing)
        )

    if not record[
        "selected_sources"
    ]:

        return False, (
            "No data sources selected"
        )

    if not record[
        "purpose"
    ]:

        return False, (
            "Purpose is required"
        )

    if record[
        "withdrawn"
    ]:

        return False, (
            "Consent has been withdrawn"
        )

    return True, "VALID"


# =========================================================
# 4. DATA MINIMIZATION
# =========================================================

def apply_data_minimization(
    selected_sources
):

    approved = []

    rejected = []

    for source in selected_sources:

        if source not in DATA_SOURCES:

            rejected.append(
                source
            )

            continue

        # Location is intentionally excluded
        # from the core prototype.

        if source == "location":

            rejected.append(
                source
            )

        else:

            approved.append(
                source
            )

    return approved, rejected


# =========================================================
# 5. APPLICANT SIMULATION
# =========================================================

applicant_id = 1001

purpose = (
    "Assess credit eligibility using "
    "consented financial and behavioural information."
)


# Applicant chooses these.

requested_sources = [

    "bank_cashflow",

    "platform_income",

    "repayment_history"
]


approved_sources, rejected_sources = (
    apply_data_minimization(
        requested_sources
    )
)


# =========================================================
# 6. CREATE CONSENT
# =========================================================

consent = create_consent_record(

    applicant_id=
        applicant_id,

    selected_sources=
        approved_sources,

    purpose=
        purpose,

    duration_days=
        30
)


# =========================================================
# 7. VALIDATE
# =========================================================

valid, message = (
    validate_consent(
        consent
    )
)


print(
    "\nConsent validation:"
)

print(
    "Status:",
    "VALID" if valid else "INVALID"
)

print(
    "Message:",
    message
)


# =========================================================
# 8. CONSENT DISPLAY
# =========================================================

print(
    "\n" + "=" * 70
)

print(
    "APPLICANT CONSENT SCREEN"
)

print(
    "=" * 70
)

print(
    "\nPurpose:"
)

print(
    purpose
)


print(
    "\nRequested data:"
)

for source in approved_sources:

    info = DATA_SOURCES[
        source
    ]

    print(
        f"\n✓ {info['name']}"
    )

    print(
        f"  Purpose: {info['purpose']}"
    )

    print(
        f"  Period: {info['period']}"
    )


if rejected_sources:

    print(
        "\nData not required:"
    )

    for source in rejected_sources:

        print(
            f"✗ {source}"
        )


print(
    "\nConsent ID:"
)

print(
    consent[
        "consent_id"
    ]
)


print(
    "\nConsent expires:"
)

print(
    consent[
        "expiry"
    ]
)


# =========================================================
# 9. AUDIT LOG
# =========================================================

audit_log = []

audit_log.append({

    "timestamp":
        consent["timestamp"],

    "applicant_id":
        applicant_id,

    "consent_id":
        consent["consent_id"],

    "event":
        "CONSENT_GRANTED",

    "purpose":
        purpose,

    "sources":
        ",".join(
            approved_sources
        )
})


# =========================================================
# 10. WITHDRAW CONSENT
# =========================================================

def withdraw_consent(
    record
):

    record[
        "withdrawn"
    ] = True

    record[
        "status"
    ] = "WITHDRAWN"

    audit_log.append({

        "timestamp":
            datetime.now().isoformat(),

        "applicant_id":
            record["applicant_id"],

        "consent_id":
            record["consent_id"],

        "event":
            "CONSENT_WITHDRAWN"
    })

    return record


# Demonstration

print(
    "\n" + "=" * 70
)

print(
    "CONSENT WITHDRAWAL DEMONSTRATION"
)

print(
    "=" * 70
)

withdrawn = withdraw_consent(
    consent.copy()
)

print(
    "New status:",
    withdrawn["status"]
)


# =========================================================
# 11. POST-WITHDRAWAL VALIDATION
# =========================================================

valid_after_withdrawal, message = (
    validate_consent(
        withdrawn
    )
)

print(
    "Can new processing continue?",
    valid_after_withdrawal
)

print(
    "Reason:",
    message
)


# =========================================================
# 12. SAVE AUDIT LOG
# =========================================================

audit_df = pd.DataFrame(
    audit_log
)

audit_df.to_csv(
    "kavach_consent_audit_log.csv",
    index=False
)


consent_df = pd.DataFrame(
    [consent]
)

consent_df.to_csv(
    "kavach_consent_records.csv",
    index=False
)


print(
    "\nSaved:"
)

print(
    "  kavach_consent_records.csv"
)

print(
    "  kavach_consent_audit_log.csv"
)


# =========================================================
# 13. GOVERNANCE CHECKLIST
# =========================================================

print(
    "\n" + "=" * 70
)

print(
    "KAVACH GOVERNANCE CHECKLIST"
)

print(
    "=" * 70
)

checks = {

    "Purpose specified":
        bool(purpose),

    "Specific sources selected":
        len(approved_sources) > 0,

    "Unnecessary location excluded":
        "location"
        not in approved_sources,

    "Consent record created":
        bool(
            consent[
                "consent_id"
            ]
        ),

    "Audit event recorded":
        len(audit_log) > 0,

    "Withdrawal supported":
        withdrawn[
            "status"
        ] == "WITHDRAWN"
}


for name, result in checks.items():

    print(
        f"{'PASS' if result else 'FAIL'}"
        f"  {name}"
    )


print(
    "\n" + "=" * 70
)

print(
    "CONSENT + DATA GOVERNANCE ENGINE COMPLETE"
)

print(
    "=" * 70
)
