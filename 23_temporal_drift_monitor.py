# ============================================================
# KAVACH PULSE — TEMPORAL DRIFT & POPULATION STABILITY MONITOR
# ============================================================
#
# Purpose:
#   Monitor whether applicant characteristics and model
#   predictions change across historical "vintages".
#
# IMPORTANT:
#   Home Credit application_train.csv does not contain a clean
#   application timestamp in the selected data.
#
#   Therefore DAYS_ID_PUBLISH is used ONLY as a temporal proxy.
#
#   This is NOT true out-of-time validation.
#
# ============================================================

import os
import warnings

import numpy as np
import pandas as pd

from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    brier_score_loss,
    log_loss
)

warnings.filterwarnings("ignore")


# ============================================================
# CONFIGURATION
# ============================================================

APPLICATION_FILE = "application_train.csv"

PREDICTION_FILE = "kavach_logistic_test_predictions.csv"

DRIFT_OUTPUT = "kavach_temporal_drift_results.csv"

PERFORMANCE_OUTPUT = "kavach_temporal_performance_results.csv"

SUMMARY_OUTPUT = "kavach_temporal_drift_summary.csv"


# ============================================================
# HEADER
# ============================================================

print("=" * 70)
print("KAVACH PULSE — TEMPORAL DRIFT & POPULATION STABILITY MONITOR")
print("=" * 70)


# ============================================================
# 1. LOAD DATA
# ============================================================

print("\n[1] Loading benchmark data...")


if not os.path.exists(APPLICATION_FILE):

    raise FileNotFoundError(
        f"Could not find {APPLICATION_FILE}"
    )


if not os.path.exists(PREDICTION_FILE):

    raise FileNotFoundError(
        f"Could not find {PREDICTION_FILE}"
    )


application = pd.read_csv(
    APPLICATION_FILE
)


predictions = pd.read_csv(
    PREDICTION_FILE
)


print(
    "Application dataset:",
    application.shape
)


print(
    "Prediction dataset:",
    predictions.shape
)


# ============================================================
# 2. REQUIRED COLUMNS
# ============================================================

print("\n[2] Checking required columns...")


required_application = [
    "SK_ID_CURR",
    "TARGET",
    "DAYS_ID_PUBLISH",
    "AMT_INCOME_TOTAL",
    "AMT_CREDIT",
    "AMT_ANNUITY",
    "EXT_SOURCE_2",
    "EXT_SOURCE_3"
]


required_prediction = [
    "SK_ID_CURR",
    "ACTUAL_TARGET",
    "PREDICTED_PD"
]


missing_application = [
    c for c in required_application
    if c not in application.columns
]


missing_prediction = [
    c for c in required_prediction
    if c not in predictions.columns
]


if missing_application:

    raise ValueError(
        "Missing application columns:\n"
        + str(missing_application)
    )


if missing_prediction:

    raise ValueError(
        "Missing prediction columns:\n"
        + str(missing_prediction)
    )


print("Required columns: PASSED")


# ============================================================
# 3. ALIGN PREDICTIONS
# ============================================================

print("\n[3] Aligning predictions using SK_ID_CURR...")


evaluation = application[
    required_application
].merge(
    predictions[
        required_prediction
    ],
    on="SK_ID_CURR",
    how="inner",
    validate="one_to_one"
)


print(
    "Aligned dataset:",
    evaluation.shape
)


if len(evaluation) != len(predictions):

    raise ValueError(
        f"""
Prediction alignment failed.

Prediction rows:
{len(predictions)}

Matched rows:
{len(evaluation)}
"""
    )


target_match = (
    evaluation["TARGET"].astype(int)
    ==
    evaluation["ACTUAL_TARGET"].astype(int)
)


alignment_rate = target_match.mean()


print(
    f"Target alignment rate: {alignment_rate:.4f}"
)


if alignment_rate < 0.999999:

    raise ValueError(
        "Target alignment is not 100%. Stop."
    )


print("Alignment: PASSED")


# ============================================================
# 4. PREPARE VARIABLES
# ============================================================

print("\n[4] Preparing monitoring variables...")


evaluation["target"] = (
    evaluation["TARGET"]
    .astype(int)
)


evaluation["predicted_pd"] = pd.to_numeric(
    evaluation["PREDICTED_PD"],
    errors="coerce"
)


evaluation["days_id_publish"] = pd.to_numeric(
    evaluation["DAYS_ID_PUBLISH"],
    errors="coerce"
)


# Remove impossible prediction values.

evaluation = evaluation[
    evaluation["predicted_pd"].between(0, 1)
].copy()


# ============================================================
# 5. CREATE TEMPORAL PROXY
# ============================================================

print("\n[5] Creating temporal proxy...")


print(
"""
WARNING:

DAYS_ID_PUBLISH is NOT a true application timestamp.

It represents the number of days before the application
that the client's identity document was changed/published.

For this experiment it is used only as a historical
ordering proxy.

Therefore:

TEMPORAL DRIFT ≠ TRUE OUT-OF-TIME VALIDATION
"""
)


# Larger DAYS_ID_PUBLISH means the document event was
# further in the past relative to application.

# We divide observations into five equal-frequency
# historical proxy cohorts.

evaluation["vintage"] = pd.qcut(
    evaluation["days_id_publish"],
    q=5,
    labels=[
        "VINTAGE_1",
        "VINTAGE_2",
        "VINTAGE_3",
        "VINTAGE_4",
        "VINTAGE_5"
    ],
    duplicates="drop"
)


print("\nVintage distribution:")


print(
    evaluation["vintage"]
    .value_counts()
    .sort_index()
)


# ============================================================
# 6. PSI FUNCTION
# ============================================================

def calculate_psi(
    reference,
    current,
    bins=10
):

    reference = pd.Series(
        reference
    ).dropna()


    current = pd.Series(
        current
    ).dropna()


    if len(reference) == 0 or len(current) == 0:

        return np.nan


    # Quantile bins from reference population.

    quantiles = np.linspace(
        0,
        1,
        bins + 1
    )


    edges = np.unique(
        reference.quantile(
            quantiles
        ).values
    )


    if len(edges) < 3:

        return 0.0


    reference_counts, _ = np.histogram(
        reference,
        bins=edges
    )


    current_counts, _ = np.histogram(
        current,
        bins=edges
    )


    reference_pct = (
        reference_counts
        /
        len(reference)
    )


    current_pct = (
        current_counts
        /
        len(current)
    )


    # Avoid division by zero.

    epsilon = 1e-6


    reference_pct = np.clip(
        reference_pct,
        epsilon,
        None
    )


    current_pct = np.clip(
        current_pct,
        epsilon,
        None
    )


    psi = np.sum(
        (
            current_pct
            -
            reference_pct
        )
        *
        np.log(
            current_pct
            /
            reference_pct
        )
    )


    return float(psi)


# ============================================================
# 7. PSI INTERPRETATION
# ============================================================

def psi_status(
    psi
):

    if pd.isna(psi):

        return "UNAVAILABLE"


    if psi < 0.10:

        return "STABLE"


    elif psi < 0.25:

        return "WARNING"


    else:

        return "CRITICAL"


# ============================================================
# 8. REFERENCE VINTAGE
# ============================================================

print("\n[6] Selecting reference vintage...")


vintages = list(
    evaluation[
        "vintage"
    ].cat.categories
)


if len(vintages) < 2:

    raise ValueError(
        "Not enough temporal cohorts."
    )


reference_vintage = vintages[0]


reference = evaluation[
    evaluation["vintage"]
    ==
    reference_vintage
].copy()


print(
    "Reference vintage:",
    reference_vintage
)


print(
    "Reference observations:",
    len(reference)
)


# ============================================================
# 9. FEATURES TO MONITOR
# ============================================================

monitor_features = [

    "AMT_INCOME_TOTAL",

    "AMT_CREDIT",

    "AMT_ANNUITY",

    "EXT_SOURCE_2",

    "EXT_SOURCE_3",

    "predicted_pd"

]


# ============================================================
# 10. FEATURE DRIFT
# ============================================================

print("\n[7] Calculating feature drift...")


drift_rows = []


for vintage in vintages:

    current = evaluation[
        evaluation["vintage"]
        ==
        vintage
    ].copy()


    for feature in monitor_features:

        psi = calculate_psi(
            reference[feature],
            current[feature]
        )


        drift_rows.append({

            "reference_vintage":
                reference_vintage,

            "current_vintage":
                vintage,

            "feature":
                feature,

            "psi":
                psi,

            "status":
                psi_status(psi),

            "reference_mean":
                reference[feature].mean(),

            "current_mean":
                current[feature].mean(),

            "reference_median":
                reference[feature].median(),

            "current_median":
                current[feature].median(),

            "reference_n":
                len(reference),

            "current_n":
                len(current)

        })


drift_results = pd.DataFrame(
    drift_rows
)


# ============================================================
# 11. PRINT DRIFT RESULTS
# ============================================================

print("\n" + "=" * 70)
print("POPULATION STABILITY RESULTS")
print("=" * 70)


print(
    drift_results[
        [
            "current_vintage",
            "feature",
            "psi",
            "status"
        ]
    ].to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)


# ============================================================
# 12. PERFORMANCE BY VINTAGE
# ============================================================

print("\n" + "=" * 70)
print("MODEL PERFORMANCE BY VINTAGE")
print("=" * 70)


performance_rows = []


for vintage in vintages:

    group = evaluation[
        evaluation["vintage"]
        ==
        vintage
    ].copy()


    n = len(group)


    default_rate = group[
        "target"
    ].mean()


    mean_pd = group[
        "predicted_pd"
    ].mean()


    if group["target"].nunique() >= 2:

        auc = roc_auc_score(
            group["target"],
            group["predicted_pd"]
        )


        pr_auc = average_precision_score(
            group["target"],
            group["predicted_pd"]
        )

    else:

        auc = np.nan
        pr_auc = np.nan


    brier = brier_score_loss(
        group["target"],
        group["predicted_pd"]
    )


    logloss = log_loss(
        group["target"],
        group["predicted_pd"],
        labels=[0, 1]
    )


    performance_rows.append({

        "vintage":
            vintage,

        "n":
            n,

        "observed_default_rate":
            default_rate,

        "mean_predicted_pd":
            mean_pd,

        "roc_auc":
            auc,

        "pr_auc":
            pr_auc,

        "brier":
            brier,

        "log_loss":
            logloss

    })


performance_results = pd.DataFrame(
    performance_rows
)


print(
    performance_results.to_string(
        index=False,
        float_format=lambda x: f"{x:.5f}"
    )
)


# ============================================================
# 13. CALIBRATION GAP BY VINTAGE
# ============================================================

performance_results[
    "calibration_gap"
] = (
    performance_results[
        "observed_default_rate"
    ]
    -
    performance_results[
        "mean_predicted_pd"
    ]
)


# ============================================================
# 14. BASELINE PERFORMANCE
# ============================================================

overall_auc = roc_auc_score(
    evaluation["target"],
    evaluation["predicted_pd"]
)


overall_pr_auc = average_precision_score(
    evaluation["target"],
    evaluation["predicted_pd"]
)


overall_brier = brier_score_loss(
    evaluation["target"],
    evaluation["predicted_pd"]
)


overall_logloss = log_loss(
    evaluation["target"],
    evaluation["predicted_pd"]
)


# ============================================================
# 15. PERFORMANCE DRIFT
# ============================================================

valid_auc = performance_results[
    "roc_auc"
].dropna()


auc_min = valid_auc.min()


auc_max = valid_auc.max()


auc_range = auc_max - auc_min


brier_max = (
    performance_results[
        "brier"
    ].max()
)


logloss_max = (
    performance_results[
        "log_loss"
    ].max()
)


calibration_gap_max = (
    performance_results[
        "calibration_gap"
    ]
    .abs()
    .max()
)


# ============================================================
# 16. GLOBAL DRIFT STATUS
# ============================================================

max_psi = drift_results[
    "psi"
].max()


critical_drift_count = (
    drift_results[
        "status"
    ]
    ==
    "CRITICAL"
).sum()


warning_drift_count = (
    drift_results[
        "status"
    ]
    ==
    "WARNING"
).sum()


if critical_drift_count > 0:

    global_drift_status = "CRITICAL"

elif warning_drift_count > 0:

    global_drift_status = "WARNING"

else:

    global_drift_status = "STABLE"


# ============================================================
# 17. PERFORMANCE STATUS
# ============================================================

# These are prototype monitoring thresholds,
# NOT regulatory thresholds.

if auc_range > 0.10:

    performance_status = "WARNING"

elif auc_range > 0.20:

    performance_status = "CRITICAL"

else:

    performance_status = "STABLE"


# Correct ordering: critical must be checked first.

if auc_range > 0.20:

    performance_status = "CRITICAL"

elif auc_range > 0.10:

    performance_status = "WARNING"

else:

    performance_status = "STABLE"


# ============================================================
# 18. OVERALL MONITORING STATUS
# ============================================================

if (
    global_drift_status == "CRITICAL"
    or
    performance_status == "CRITICAL"
):

    overall_status = "CRITICAL"

elif (
    global_drift_status == "WARNING"
    or
    performance_status == "WARNING"
):

    overall_status = "WARNING"

else:

    overall_status = "STABLE"


# ============================================================
# 19. MONITORING SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("TEMPORAL MONITORING SUMMARY")
print("=" * 70)


print(
    f"Overall benchmark ROC-AUC: {overall_auc:.6f}"
)


print(
    f"Overall benchmark PR-AUC : {overall_pr_auc:.6f}"
)


print(
    f"Overall benchmark Brier  : {overall_brier:.6f}"
)


print(
    f"Overall benchmark LogLoss: {overall_logloss:.6f}"
)


print(
    f"Maximum PSI              : {max_psi:.6f}"
)


print(
    f"Critical drift signals   : {critical_drift_count}"
)


print(
    f"Warning drift signals    : {warning_drift_count}"
)


print(
    f"Vintage ROC-AUC range    : {auc_range:.6f}"
)


print(
    f"Maximum calibration gap  : {calibration_gap_max:.6f}"
)


print(
    f"Population drift status  : {global_drift_status}"
)


print(
    f"Performance status       : {performance_status}"
)


print(
    f"OVERALL STATUS           : {overall_status}"
)


# ============================================================
# 20. IDENTIFY LARGEST DRIFT
# ============================================================

print("\n" + "=" * 70)
print("LARGEST DRIFT SIGNALS")
print("=" * 70)


largest_drift = (
    drift_results
    .sort_values(
        "psi",
        ascending=False
    )
    .head(10)
)


print(
    largest_drift[
        [
            "current_vintage",
            "feature",
            "psi",
            "status"
        ]
    ].to_string(
        index=False,
        float_format=lambda x: f"{x:.5f}"
    )
)


# ============================================================
# 21. IDENTIFY WORST VINTAGES
# ============================================================

print("\n" + "=" * 70)
print("WORST VINTAGES")
print("=" * 70)


print(
    "\nLowest ROC-AUC:"
)


print(
    performance_results
    .sort_values(
        "roc_auc",
        ascending=True
    )
    [
        [
            "vintage",
            "n",
            "roc_auc",
            "pr_auc",
            "calibration_gap"
        ]
    ]
    .head(5)
    .to_string(
        index=False,
        float_format=lambda x: f"{x:.5f}"
    )
)


print(
    "\nLargest absolute calibration gap:"
)


print(
    performance_results
    .assign(
        abs_calibration_gap=
        performance_results[
            "calibration_gap"
        ].abs()
    )
    .sort_values(
        "abs_calibration_gap",
        ascending=False
    )
    [
        [
            "vintage",
            "n",
            "observed_default_rate",
            "mean_predicted_pd",
            "calibration_gap"
        ]
    ]
    .head(5)
    .to_string(
        index=False,
        float_format=lambda x: f"{x:.5f}"
    )
)


# ============================================================
# 22. SAVE FILES
# ============================================================

print("\n[8] Saving monitoring outputs...")


drift_results.to_csv(
    DRIFT_OUTPUT,
    index=False
)


performance_results.to_csv(
    PERFORMANCE_OUTPUT,
    index=False
)


summary = pd.DataFrame({

    "metric": [

        "overall_status",

        "population_drift_status",

        "performance_status",

        "overall_roc_auc",

        "overall_pr_auc",

        "overall_brier",

        "overall_log_loss",

        "maximum_psi",

        "critical_drift_signals",

        "warning_drift_signals",

        "vintage_auc_min",

        "vintage_auc_max",

        "vintage_auc_range",

        "maximum_calibration_gap",

        "target_alignment_rate"

    ],

    "value": [

        overall_status,

        global_drift_status,

        performance_status,

        overall_auc,

        overall_pr_auc,

        overall_brier,

        overall_logloss,

        max_psi,

        critical_drift_count,

        warning_drift_count,

        auc_min,

        auc_max,

        auc_range,

        calibration_gap_max,

        alignment_rate

    ]

})


summary.to_csv(
    SUMMARY_OUTPUT,
    index=False
)


print("\nSaved:")

print(
    f"  {DRIFT_OUTPUT}"
)

print(
    f"  {PERFORMANCE_OUTPUT}"
)

print(
    f"  {SUMMARY_OUTPUT}"
)


# ============================================================
# 23. METHODOLOGY WARNING
# ============================================================

print("\n" + "=" * 70)
print("METHODOLOGY WARNING")
print("=" * 70)

print(
"""
This is a TEMPORAL DRIFT MONITORING PROTOTYPE.

The Home Credit dataset does not provide a clean
application timestamp in this analysis.

DAYS_ID_PUBLISH is therefore used only as a
historical ordering proxy.

Consequently:

1. This is NOT true out-of-time validation.

2. PSI thresholds are prototype monitoring thresholds.

3. STABLE/WARNING/CRITICAL labels are not regulatory
   standards.

4. The model is still being evaluated on the
   Home Credit benchmark population.

5. These results do NOT establish Kavach production
   stability.

A production monitoring system should use:

- true application timestamps
- rolling time windows
- out-of-time validation
- Population Stability Index (PSI)
- characteristic stability
- prediction drift
- default-rate drift
- calibration drift
- ROC-AUC / PR-AUC drift
- fairness drift
- missing-data drift
- challenger-model monitoring
- automated alerts
- model governance procedures

The production principle is:

DATA DRIFT
     +
PREDICTION DRIFT
     +
PERFORMANCE DRIFT
     +
CALIBRATION DRIFT
     =
MODEL MONITORING
"""
)


print("=" * 70)
print("TEMPORAL DRIFT & STABILITY MONITOR COMPLETE")
print("=" * 70)
