"""
======================================================================
KAVACH PULSE — FINAL PROTOTYPE VALIDATION REPORT
======================================================================

Purpose:
    Consolidate the major Kavach prototype validation artifacts into
    one final machine-readable validation report.

IMPORTANT:
    This report does NOT establish production credit performance.

    Home Credit results are benchmark results.
    Behavioural histories and repayment simulations are synthetic.
    Risk proxy is not calibrated probability of default.
======================================================================
"""

import json
import glob
import os
from datetime import datetime

import pandas as pd


# ======================================================================
# CONFIGURATION
# ======================================================================

BASE_DIR = "."

print("=" * 70)
print("KAVACH PULSE — FINAL PROTOTYPE VALIDATION REPORT")
print("=" * 70)


# ======================================================================
# HELPER FUNCTIONS
# ======================================================================

def latest_file(pattern):
    files = glob.glob(
        os.path.join(BASE_DIR, pattern)
    )

    if not files:
        return None

    return max(
        files,
        key=os.path.getmtime
    )


def load_csv(pattern):
    path = latest_file(pattern)

    if path is None:
        return None, None

    return pd.read_csv(path), path


def safe_float(value):
    if pd.isna(value):
        return None

    return float(value)


# ======================================================================
# 1. LOAD CORE ARTIFACTS
# ======================================================================

print()
print("[1] Loading validation artifacts...")


scenario_df, scenario_file = load_csv(
    "kavach_live_scenario_results_*.csv"
)

scenario_checks_df, scenario_checks_file = load_csv(
    "kavach_live_scenario_checks_*.csv"
)

regression_df, regression_file = load_csv(
    "kavach_regression_results_*.csv"
)

print(
    "Scenario results:",
    scenario_file
)

print(
    "Scenario checks:",
    scenario_checks_file
)

print(
    "Regression results:",
    regression_file
)


# ======================================================================
# 2. LOAD EXISTING MODEL RESULTS
# ======================================================================

print()
print("[2] Loading benchmark and experiment results...")


ablation_file = "kavach_feature_ablation_results.csv"

if os.path.exists(ablation_file):

    ablation_df = pd.read_csv(
        ablation_file
    )

else:

    ablation_df = pd.DataFrame()


comparison_file = "kavach_model_comparison.csv"

if os.path.exists(comparison_file):

    comparison_df = pd.read_csv(
        comparison_file
    )

else:

    comparison_df = pd.DataFrame()


fairness_gender_file = (
    "kavach_fairness_gender.csv"
)

fairness_education_file = (
    "kavach_fairness_education.csv"
)

fairness_income_file = (
    "kavach_fairness_income.csv"
)

temporal_summary_file = (
    "kavach_temporal_drift_summary.csv"
)

cost_file = (
    "kavach_policy_cost_comparison.csv"
)

provenance_file = (
    "kavach_model_provenance_audit.json"
)


# ======================================================================
# 3. REGRESSION SUMMARY
# ======================================================================

print()
print("[3] Calculating regression validation...")


if regression_df is not None:

    regression_total = len(
        regression_df
    )

    regression_passed = int(
        (
            regression_df["status"]
            == "PASS"
        ).sum()
    )

    regression_failed = (
        regression_total
        -
        regression_passed
    )

else:

    regression_total = 0
    regression_passed = 0
    regression_failed = 0


regression_status = (

    "PASS"

    if regression_failed == 0
    and regression_total > 0

    else

    "FAIL"
)


print(
    "Regression tests:",
    regression_passed,
    "/",
    regression_total
)

print(
    "Status:",
    regression_status
)


# ======================================================================
# 4. LIVE SCENARIO SUMMARY
# ======================================================================

print()
print("[4] Calculating live scenario validation...")


if scenario_checks_df is not None:

    scenario_check_total = len(
        scenario_checks_df
    )

    scenario_check_passed = int(
        (
            scenario_checks_df["status"]
            == "PASS"
        ).sum()
    )

    scenario_check_failed = (
        scenario_check_total
        -
        scenario_check_passed
    )

else:

    scenario_check_total = 0
    scenario_check_passed = 0
    scenario_check_failed = 0


scenario_status = (

    "PASS"

    if scenario_check_failed == 0
    and scenario_check_total > 0

    else

    "FAIL"
)


scenario_count = (

    len(scenario_df)

    if scenario_df is not None

    else

    0
)


print(
    "Live scenarios:",
    scenario_count
)

print(
    "Architectural checks:",
    scenario_check_passed,
    "/",
    scenario_check_total
)

print(
    "Status:",
    scenario_status
)


# ======================================================================
# 5. BENCHMARK RESULTS
# ======================================================================

print()
print("[5] Extracting benchmark results...")


benchmark = {}


if not comparison_df.empty:

    for _, row in comparison_df.iterrows():

        model_name = str(
            row.get(
                "model",
                row.get(
                    "strategy",
                    "unknown"
                )
            )
        )

        benchmark[
            model_name
        ] = {

            "roc_auc":
                safe_float(
                    row.get(
                        "ROC-AUC",
                        row.get(
                            "roc_auc"
                        )
                    )
                ),

            "pr_auc":
                safe_float(
                    row.get(
                        "PR-AUC",
                        row.get(
                            "pr_auc"
                        )
                    )
                ),

            "brier":
                safe_float(
                    row.get(
                        "Brier",
                        row.get(
                            "brier"
                        )
                    )
                ),

            "log_loss":
                safe_float(
                    row.get(
                        "LogLoss",
                        row.get(
                            "log_loss"
                        )
                    )
                )
        }


# Explicit known benchmark from the completed experiment.

home_credit_benchmark = {

    "roc_auc": 0.738517,

    "pr_auc": 0.218903,

    "brier": 0.068993,

    "log_loss": 0.251773
}


# ======================================================================
# 6. ABLATION RESULTS
# ======================================================================

print()
print("[6] Extracting feature ablation results...")


ablation_results = []


if not ablation_df.empty:

    for _, row in ablation_df.iterrows():

        ablation_results.append({

            "model":
                str(
                    row.get(
                        "model",
                        ""
                    )
                ),

            "features":
                safe_float(
                    row.get(
                        "features"
                    )
                ),

            "roc_auc":
                safe_float(
                    row.get(
                        "roc_auc"
                    )
                ),

            "pr_auc":
                safe_float(
                    row.get(
                        "pr_auc"
                    )
                )
        })


# ======================================================================
# 7. FAIRNESS SUMMARY
# ======================================================================

print()
print("[7] Extracting fairness audit results...")


fairness_summary = {}


def load_fairness(
    label,
    filename
):

    if not os.path.exists(
        filename
    ):

        return None

    df = pd.read_csv(
        filename
    )

    return {

        "groups":
            int(
                len(df)
            ),

        "columns":
            list(
                df.columns
            )
    }


fairness_summary["gender"] = load_fairness(
    "gender",
    fairness_gender_file
)

fairness_summary["education"] = load_fairness(
    "education",
    fairness_education_file
)

fairness_summary["income"] = load_fairness(
    "income",
    fairness_income_file
)


# Known diagnostic results from Stage 19.

fairness_selection_rates = {

    "gender":
        0.984,

    "education":
        0.760,

    "income":
        0.972
}

fairness_flags = {

    "gender_selection_rate":
        "NO_INITIAL_FLAG",

    "education_selection_rate":
        "INVESTIGATE",

    "income_selection_rate":
        "NO_INITIAL_FLAG"
}


# ======================================================================
# 8. TEMPORAL DRIFT
# ======================================================================

print()
print("[8] Extracting temporal monitoring...")


temporal_summary = {}


if os.path.exists(
    temporal_summary_file
):

    df = pd.read_csv(
        temporal_summary_file
    )

    temporal_summary = {

        "rows":
            int(
                len(df)
            ),

        "columns":
            list(
                df.columns
            )
    }


temporal_summary.update({

    "maximum_psi":
        0.164683,

    "warning_signals":
        3,

    "critical_signals":
        0,

    "population_drift_status":
        "WARNING",

    "performance_status":
        "STABLE",

    "overall_status":
        "WARNING"
})


# ======================================================================
# 9. COST-SENSITIVE POLICY
# ======================================================================

print()
print("[9] Extracting policy optimization...")


cost_summary = {

    "best_binary_threshold":
        0.505,

    "best_binary_cost_per_applicant":
        0.164893,

    "best_three_way_pass_threshold":
        0.100,

    "best_three_way_decline_threshold":
        0.340,

    "best_three_way_cost_per_applicant":
        0.610077,

    "pass_rate":
        0.739047,

    "manual_review_rate":
        0.248336,

    "decline_rate":
        0.012617
}


# ======================================================================
# 10. PROVENANCE
# ======================================================================

print()
print("[10] Loading provenance audit...")


provenance = {}

if os.path.exists(
    provenance_file
):

    try:

        with open(
            provenance_file,
            "r"
        ) as f:

            provenance = json.load(f)

    except Exception:

        provenance = {}


# ======================================================================
# 11. FINAL VALIDATION STATUS
# ======================================================================

print()
print("[11] Determining final prototype status...")


all_validation_passed = (

    regression_status == "PASS"

    and

    scenario_status == "PASS"
)


if all_validation_passed:

    prototype_validation_status = (
        "TECHNICAL_PROTOTYPE_VALIDATION_PASS"
    )

else:

    prototype_validation_status = (
        "TECHNICAL_PROTOTYPE_VALIDATION_FAIL"
    )


# ======================================================================
# 12. LIMITATIONS
# ======================================================================

limitations = [

    "Behavioural histories are synthetic.",

    "Synthetic alternative data is not real gig-worker data.",

    "Synthetic repayment outcomes are not real borrower outcomes.",

    "The risk proxy is not a calibrated probability of default.",

    "Home Credit benchmark performance does not represent Kavach target-population performance.",

    "Policy thresholds are prototype assumptions.",

    "Fairness audit does not establish legal or regulatory compliance.",

    "Temporal monitoring uses a historical ordering proxy rather than a true application timestamp.",

    "Production validation requires consented target-population behavioural histories linked to observed repayment outcomes.",

    "Production deployment requires model governance, legal review, regulatory review, lender integration and ongoing monitoring."
]


# ======================================================================
# 13. WHAT HAS BEEN DEMONSTRATED
# ======================================================================

demonstrated = [

    "Consent-gated assessment workflow",

    "Thin-file evidence handling",

    "Evidence quality estimation",

    "History-depth classification",

    "Confidence routing",

    "Behavioural feature engineering",

    "Prototype risk scoring",

    "Risk-confidence separation",

    "Policy routing",

    "Applicant-level explanations",

    "Feature contribution explanation",

    "Fairness auditing",

    "Cost-sensitive threshold analysis",

    "Population and prediction drift monitoring",

    "Model and data provenance tracking",

    "Integrated decision engine",

    "Live API assessment",

    "Live scenario validation",

    "Automated regression testing"
]


# ======================================================================
# 14. FINAL REPORT OBJECT
# ======================================================================

report = {

    "report_metadata": {

        "report_name":
            "Kavach Pulse Final Prototype Validation Report",

        "generated_at":
            datetime.now().astimezone().isoformat(),

        "prototype_version":
            "KAVACH-PROTOTYPE-v2",

        "policy_version":
            "KAVACH-POLICY-PROTOTYPE-v2"
    },


    "final_status": {

        "technical_validation":
            prototype_validation_status,

        "live_scenario_validation":
            scenario_status,

        "automated_regression":
            regression_status,

        "regression_tests":
            regression_total,

        "regression_passed":
            regression_passed,

        "regression_failed":
            regression_failed,

        "scenario_checks":
            scenario_check_total,

        "scenario_checks_passed":
            scenario_check_passed,

        "scenario_checks_failed":
            scenario_check_failed
    },


    "benchmark": {

        "dataset":
            "Home Credit public benchmark",

        "roc_auc":
            home_credit_benchmark[
                "roc_auc"
            ],

        "pr_auc":
            home_credit_benchmark[
                "pr_auc"
            ],

        "brier":
            home_credit_benchmark[
                "brier"
            ],

        "log_loss":
            home_credit_benchmark[
                "log_loss"
            ],

        "interpretation":
            "Benchmark result only; not evidence of Kavach target-population performance."
    },


    "feature_ablation":
        ablation_results,


    "fairness": {

        "selection_rate_ratios":
            fairness_selection_rates,

        "initial_flags":
            fairness_flags,

        "interpretation":
            "Prototype fairness diagnostics only."
    },


    "temporal_monitoring":
        temporal_summary,


    "policy_optimization":
        cost_summary,


    "live_validation": {

        "scenario_count":
            scenario_count,

        "scenario_checks":
            scenario_check_passed,

        "scenario_status":
            scenario_status
    },


    "automated_regression": {

        "total":
            regression_total,

        "passed":
            regression_passed,

        "failed":
            regression_failed,

        "status":
            regression_status
    },


    "demonstrated_capabilities":
        demonstrated,


    "limitations":
        limitations,


    "provenance":

        {

            "provenance_audit_available":
                bool(
                    provenance
                ),

            "real_public_data":
                [
                    "Home Credit application_train.csv"
                ],

            "synthetic_data":
                [
                    "kavach_synthetic_alternative_data.csv",
                    "kavach_thin_file_monthly_history.csv",
                    "kavach_synthetic_monthly_history.csv",
                    "kavach_synthetic_risk_predictions.csv"
                ],

            "production_credit_validation":
                "NOT AVAILABLE"
        }
}


# ======================================================================
# 15. SAVE JSON
# ======================================================================

json_output = (
    "kavach_final_validation_report.json"
)


with open(
    json_output,
    "w"
) as f:

    json.dump(
        report,
        f,
        indent=2
    )


# ======================================================================
# 16. SAVE SUMMARY CSV
# ======================================================================

summary_rows = [

    {
        "category":
            "Technical validation",

        "metric":
            "Overall status",

        "value":
            prototype_validation_status
    },

    {
        "category":
            "Regression",

        "metric":
            "Tests passed",

        "value":
            f"{regression_passed}/{regression_total}"
    },

    {
        "category":
            "Live scenarios",

        "metric":
            "Architectural checks passed",

        "value":
            f"{scenario_check_passed}/{scenario_check_total}"
    },

    {
        "category":
            "Benchmark",

        "metric":
            "ROC-AUC",

        "value":
            home_credit_benchmark["roc_auc"]
    },

    {
        "category":
            "Benchmark",

        "metric":
            "PR-AUC",

        "value":
            home_credit_benchmark["pr_auc"]
    },

    {
        "category":
            "Benchmark",

        "metric":
            "Brier",

        "value":
            home_credit_benchmark["brier"]
    },

    {
        "category":
            "Benchmark",

        "metric":
            "LogLoss",

        "value":
            home_credit_benchmark["log_loss"]
    },

    {
        "category":
            "Fairness",

        "metric":
            "Gender selection-rate ratio",

        "value":
            fairness_selection_rates["gender"]
    },

    {
        "category":
            "Fairness",

        "metric":
            "Education selection-rate ratio",

        "value":
            fairness_selection_rates["education"]
    },

    {
        "category":
            "Fairness",

        "metric":
            "Income selection-rate ratio",

        "value":
            fairness_selection_rates["income"]
    },

    {
        "category":
            "Drift",

        "metric":
            "Maximum PSI",

        "value":
            temporal_summary["maximum_psi"]
    },

    {
        "category":
            "Drift",

        "metric":
            "Population drift",

        "value":
            temporal_summary[
                "population_drift_status"
            ]
    },

    {
        "category":
            "Policy",

        "metric":
            "Best three-way pass threshold",

        "value":
            cost_summary[
                "best_three_way_pass_threshold"
            ]
    },

    {
        "category":
            "Policy",

        "metric":
            "Best three-way decline threshold",

        "value":
            cost_summary[
                "best_three_way_decline_threshold"
            ]
    },

    {
        "category":
            "Data",

        "metric":
            "Real target-population validation",

        "value":
            "NOT AVAILABLE"
    },

    {
        "category":
            "Model",

        "metric":
            "Production PD validation",

        "value":
            "NOT AVAILABLE"
    }
]


summary_df = pd.DataFrame(
    summary_rows
)


csv_output = (
    "kavach_final_validation_summary.csv"
)


summary_df.to_csv(
    csv_output,
    index=False
)


# ======================================================================
# 17. FINAL CONSOLE SUMMARY
# ======================================================================

print()
print("=" * 70)
print("FINAL KAVACH VALIDATION SUMMARY")
print("=" * 70)

print()

print(
    "Technical validation:",
    prototype_validation_status
)

print(
    "Live scenario checks:",
    f"{scenario_check_passed}/{scenario_check_total}"
)

print(
    "Regression tests:",
    f"{regression_passed}/{regression_total}"
)

print()

print(
    "Home Credit benchmark ROC-AUC:",
    home_credit_benchmark["roc_auc"]
)

print(
    "Home Credit benchmark PR-AUC:",
    home_credit_benchmark["pr_auc"]
)

print(
    "Maximum PSI:",
    temporal_summary["maximum_psi"]
)

print(
    "Population drift:",
    temporal_summary[
        "population_drift_status"
    ]
)

print()

print(
    "REAL TARGET-POPULATION VALIDATION:"
)

print(
    "NOT AVAILABLE"
)

print()

print(
    "PRODUCTION CREDIT MODEL:"
)

print(
    "NOT VALIDATED"
)

print()

print("=" * 70)

print(
    "Saved:"
)

print(
    " ",
    json_output
)

print(
    " ",
    csv_output
)

print("=" * 70)

print()

print(
    "KAVACH FINAL VALIDATION REPORT COMPLETE"
)

print("=" * 70)
