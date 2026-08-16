# 🛡️ KAVACH PULSE

## Behaviour-Aware Credit Assessment for Thin-File Applicants

Kavach Pulse is a technical prototype for behaviour-aware credit assessment
designed to explore how alternative behavioural evidence, evidence quality,
confidence, risk estimation and policy routing can work together for
thin-file applicants.

---

# 1. Core Problem

Traditional credit assessment can struggle with applicants who have limited
or insufficient conventional credit history.

The central question explored by Kavach is:

> Can available behavioural evidence be evaluated separately from the
> confidence in that evidence?

Kavach therefore separates:

    EVIDENCE
        ↓
    CONFIDENCE
        ↓
      RISK
        ↓
     POLICY
        ↓
    EXPLANATION
        ↓
    GOVERNANCE

The central architectural principle is:

> RISK ≠ CONFIDENCE

A low-risk signal supported by weak evidence should not automatically receive
the same treatment as a similar risk signal supported by strong evidence.

---

# 2. System Architecture

```text
Applicant
    │
    ▼
Consent & Data Governance
    │
    ▼
Behavioural Evidence
    │
    ├── Payment behaviour
    ├── Income stability
    ├── Cash-flow behaviour
    ├── Balance behaviour
    └── Inflow / outflow behaviour
    │
    ▼
Evidence Quality
    │
    ├── History depth
    ├── Completeness
    ├── Source coverage
    ├── Consistency
    └── Recency
    │
    ▼
Confidence Engine
    │
    ├── HIGH
    ├── MEDIUM
    └── LOW
    │
    ▼
Risk Engine
    │
    ▼
Risk Band
    │
    ├── LOW
    ├── MODERATE
    ├── ELEVATED
    └── HIGH
    │
    ▼
Risk × Confidence Policy
    │
    ├── PASS_TO_LENDER_POLICY
    ├── MANUAL_REVIEW
    ├── REQUEST_MORE_DATA
    └── INSUFFICIENT_EVIDENCE
    │
    ▼
Applicant Explanation
    │
    ▼
Audit / Governance

3. Major Components
01 — Home Credit Audit

Initial analysis of the public Home Credit benchmark dataset.

File:

01_home_credit_audit.py
02–04 — Traditional Benchmark

Baseline construction, logistic regression and calibration.

Files:

02_build_baseline.py
03_train_logistic.py
04_calibration.py

Benchmark performance:

ROC-AUC : 0.738517
PR-AUC  : 0.218903

These results are benchmark results and do not represent production Kavach
performance.

4. Thin-File Modelling

Files:

05_train_thin_file.py
16_thin_file_simulation.py
17_evidence_depth_engine.py

Kavach explicitly models different evidence depths:

VERY_THIN
THIN
DEVELOPING
STRONG
ESTABLISHED

The system does not assume that a short history is equivalent to a long
history.

5. Behavioural Evidence

Files:

06_generate_alternative_data.py
07_train_alternative_model.py
10_behavioral_feature_engine.py
11_train_risk_simulation.py

Example behavioural signals include:

Payment success rate
Income volatility
Cash-flow volatility
Minimum balance
Inflow / outflow ratio
Income trend
Behavioural stability

Synthetic behavioural histories are used for architectural demonstration.

They are NOT real borrower histories.

6. Evidence Quality

Files:

09_evidence_quality.py
16_thin_file_simulation.py
17_evidence_depth_engine.py

Evidence quality considers:

History completeness
History depth
Source coverage
Data consistency
Data recency

Example:

Strong behaviour
+
Very short history
=
Low confidence

This is deliberately different from treating the applicant as automatically
high risk.

7. Risk × Confidence Policy

Files:

12_kavach_pd_policy_engine.py
20_risk_confidence_policy_analysis.py
21_cost_sensitive_thresholds.py

Kavach separates:

RISK

from:

CONFIDENCE

Example:

LOW RISK + HIGH CONFIDENCE
    → PASS_TO_LENDER_POLICY


LOW RISK + LOW CONFIDENCE
    → INSUFFICIENT_EVIDENCE


HIGHER RISK + HIGH CONFIDENCE
    → MANUAL_REVIEW

Policy thresholds used in the prototype are illustrative.

They are not lender-approved thresholds.

8. Explainability

Files:

13_explainability_engine.py
14_feature_contribution_engine.py

The system generates:

Positive factors
Risk factors
Evidence limitations
Feature contribution information

The goal is to make an assessment explainable rather than returning only
a numerical score.

9. Consent Governance

File:

15_consent_data_governance.py

Consent is treated as a prerequisite for processing.

The live API enforces this requirement.

Example:

consent_granted = false

returns:

HTTP 403

with:

CONSENT_REQUIRED
10. Fairness

File:

19_fairness_audit.py

The prototype includes fairness diagnostics across:

Gender
Education
Income groups

The demographic attributes are used for auditing rather than predictive
modelling.

The fairness analysis is diagnostic only.

It does not establish legal or regulatory compliance.

11. Model Stability

Files:

22_model_stability.py
23_temporal_drift_monitor.py

Monitoring includes:

Population Stability Index
Prediction drift
Performance drift
Calibration drift
Vintage-level performance

Observed benchmark monitoring result:

Maximum PSI: 0.164683

Population drift status:

WARNING

This is a prototype monitoring result.

The dataset does not provide a clean application timestamp for the temporal
experiment, so the analysis uses a historical ordering proxy.

Therefore it is NOT true out-of-time validation.

12. Integrated Decision Engine

File:

24_kavach_integrated_decision_engine.py

The integrated engine combines:

Evidence
    ↓
Confidence
    ↓
Risk
    ↓
Policy
    ↓
Explanation
    ↓
Governance

Output:

kavach_integrated_decision_output.csv
13. Live Assessment API

File:

29_kavach_live_assessment_api.py

The API exposes the live prototype assessment engine.

Health endpoint:

GET /health

Assessment endpoint:

POST /assess

Example:

{
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
    "consent_granted": true
}
14. Interactive Command Center

File:

33_kavach_command_center.py

The Streamlit interface allows the user to:

Enter applicant evidence
Specify history depth
Specify available months
Configure behavioural inputs
Submit an assessment
View risk
View evidence quality
View confidence
View history depth
View policy routing
View explanations
15. Interactive Comparison

File:

35_kavach_comparison.py

The comparison interface allows the user to select any two profiles.

Example:

Strong Established
        VS
Strong Behaviour / Thin File

This demonstrates the central Kavach principle:

Similar behavioural strength
        +
Different evidence depth
        ↓
Different confidence
        ↓
Different policy treatment

Another comparison:

Strong Established
        VS
Behavioural Deterioration

demonstrates:

Strong evidence
        +
Poor behaviour
        ↓
Higher risk
        ↓
Manual review
16. Automated Validation
Live Scenario Validation

File:

30_kavach_live_scenario_test.py

Result:

6 / 6 architectural checks PASS

Scenarios tested:

Strong established applicant
Thin-file applicant
Incomplete evidence
Behavioural deterioration
Strong behaviour with thin history
Withdrawn consent
Regression Testing

File:

31_kavach_regression_tests.py

Result:

11 / 11 tests PASS

Tests include:

API health
Strong applicant
Thin-file handling
Incomplete evidence
Behavioural deterioration
Risk-confidence separation
Consent enforcement
Risk ordering
Evidence-depth ordering
Version metadata
Final Demo System Check

File:

37_kavach_demo_check.py

Current status:

PASS  API health
PASS  Live assessment
PASS  Consent enforcement
PASS  Thin-file handling
PASS  Behavioural deterioration


KAVACH DEMO SYSTEM: READY
17. Running Kavach

Activate the environment:

source ~/kavach-env/bin/activate

Go to the project directory:

cd ~/Documents/home\ credits

Run the API:

python3 29_kavach_live_assessment_api.py

Run the Command Center in another terminal:

streamlit run 33_kavach_command_center.py

Run the comparison dashboard:

streamlit run 35_kavach_comparison.py

Alternatively use the one-command launcher:

./run_kavach.sh
18. Validation Summary

Current prototype validation:

Regression tests:          11 / 11 PASS
Live scenarios:             6 / 6 PASS
API health:                 PASS
Consent enforcement:        PASS
Thin-file handling:         PASS
Behavioural ordering:       PASS

Home Credit benchmark:

ROC-AUC:                    0.738517
PR-AUC:                     0.218903

Monitoring:

Maximum PSI:                0.164683
Population drift:           WARNING
19. Critical Limitations

Kavach is currently a technical / conceptual prototype.

The following are NOT available:

Real target-population behavioural histories
Observed repayment outcomes for Kavach behavioural features
Production-calibrated PD model
Production policy thresholds
True target-population out-of-time validation

Synthetic behavioural data is used for architectural demonstration.

The risk proxy is NOT a calibrated probability of default.

The Home Credit dataset is a public benchmark and does not represent the
intended target population of Kavach.

Therefore:

Kavach should NOT be used to make real production lending decisions.

20. Production Roadmap

A production implementation would require:

Real consented behavioural data
Observed repayment outcomes
Target-population model development
Probability calibration
Out-of-time validation
Cost-sensitive policy optimization
Fairness validation
Explainability validation
Data governance
Model governance
Human-review governance
Regulatory and legal review
Production monitoring
Challenger-model framework
21. Final Architectural Principle

Kavach does not attempt to answer only:

"Is this applicant risky?"

It also asks:

"How much evidence do we actually have to support that assessment?"

Therefore:

                 EVIDENCE
                    ↓
               CONFIDENCE
                    ↓
                  RISK
                    ↓
                 POLICY
                    ↓
              EXPLANATION
                    ↓
               GOVERNANCE

The core principle remains:

RISK ≠ CONFIDENCE
Prototype Status

TECHNICAL PROTOTYPE VALIDATION: PASS

REAL TARGET-POPULATION VALIDATION: NOT AVAILABLE

PRODUCTION CREDIT MODEL: NOT VALIDATED
