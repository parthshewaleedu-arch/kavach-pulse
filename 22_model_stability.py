# ============================================================
# KAVACH PULSE — MODEL STRESS & STABILITY ANALYSIS
# ============================================================
#
# Purpose:
#   Evaluate whether the baseline Logistic Regression model
#   behaves consistently across:
#
#   1. PD score bands
#   2. Gender
#   3. Income groups
#   4. Education groups
#   5. Age groups
#   6. Employment groups
#
# IMPORTANT:
#   - Home Credit is a public benchmark dataset.
#   - This is NOT validation on Kavach's target population.
#   - Results are benchmark/stability diagnostics only.
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

OUTPUT_FILE = "kavach_model_stability_results.csv"

SUMMARY_FILE = "kavach_model_stability_summary.csv"


# ============================================================
# HEADER
# ============================================================

print("=" * 70)
print("KAVACH PULSE — MODEL STRESS & STABILITY ANALYSIS")
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
# 2. CHECK REQUIRED COLUMNS
# ============================================================

print("\n[2] Checking required columns...")


required_application_columns = [
    "SK_ID_CURR",
    "TARGET",
    "CODE_GENDER",
    "AMT_INCOME_TOTAL",
    "NAME_EDUCATION_TYPE",
    "DAYS_BIRTH",
    "DAYS_EMPLOYED"
]


required_prediction_columns = [
    "SK_ID_CURR",
    "ACTUAL_TARGET",
    "PREDICTED_PD"
]


missing_application = [
    col
    for col in required_application_columns
    if col not in application.columns
]


missing_prediction = [
    col
    for col in required_prediction_columns
    if col not in predictions.columns
]


if missing_application:
    raise ValueError(
        "Missing columns in application_train.csv:\n"
        + str(missing_application)
    )


if missing_prediction:
    raise ValueError(
        "Missing columns in prediction file:\n"
        + str(missing_prediction)
    )


print("Required columns: PASSED")


# ============================================================
# 3. CHECK ID UNIQUENESS
# ============================================================

print("\n[3] Checking applicant ID uniqueness...")


if application["SK_ID_CURR"].duplicated().any():

    raise ValueError(
        "application_train.csv contains duplicate SK_ID_CURR values."
    )


if predictions["SK_ID_CURR"].duplicated().any():

    raise ValueError(
        "Prediction file contains duplicate SK_ID_CURR values."
    )


print("Application IDs unique: PASSED")
print("Prediction IDs unique: PASSED")


# ============================================================
# 4. MERGE USING SK_ID_CURR
# ============================================================

print("\n[4] Aligning predictions with original applicants...")


evaluation = application[
    required_application_columns
].merge(
    predictions[
        required_prediction_columns
    ],
    on="SK_ID_CURR",
    how="inner",
    validate="one_to_one"
)


print(
    "Aligned dataset:",
    evaluation.shape
)


# ============================================================
# 5. ALIGNMENT VALIDATION
# ============================================================

print("\n[5] Running alignment checks...")


if len(evaluation) != len(predictions):

    raise ValueError(
        f"""
Prediction alignment failed.

Prediction rows:
{len(predictions)}

Matched rows:
{len(evaluation)}

Every prediction must match exactly one applicant.
"""
    )


target_alignment = (
    evaluation["TARGET"].astype(int)
    ==
    evaluation["ACTUAL_TARGET"].astype(int)
)


target_alignment_rate = target_alignment.mean()


print(
    f"Target alignment rate: {target_alignment_rate:.4f}"
)


if target_alignment_rate < 0.999999:

    raise ValueError(
        f"""
Target alignment failed.

Alignment rate:
{target_alignment_rate:.6f}

Expected:
1.000000

Stop.
"""
    )


print("Target alignment: PASSED")


# ============================================================
# 6. PREDICTION VALIDATION
# ============================================================

print("\n[6] Validating predicted probabilities...")


evaluation["predicted_pd"] = pd.to_numeric(
    evaluation["PREDICTED_PD"],
    errors="coerce"
)


if evaluation["predicted_pd"].isna().any():

    raise ValueError(
        "Predicted PD contains NaN/non-numeric values."
    )


if (
    evaluation["predicted_pd"].min() < 0
    or
    evaluation["predicted_pd"].max() > 1
):

    raise ValueError(
        "Predicted PD values must be between 0 and 1."
    )


evaluation["target"] = (
    evaluation["TARGET"]
    .astype(int)
)


print(
    "PD minimum:",
    f"{evaluation['predicted_pd'].min():.6f}"
)


print(
    "PD maximum:",
    f"{evaluation['predicted_pd'].max():.6f}"
)


print("Prediction validation: PASSED")


# ============================================================
# 7. OVERALL MODEL PERFORMANCE
# ============================================================

print("\n[7] Overall benchmark performance...")


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


print(
    f"ROC-AUC : {overall_auc:.6f}"
)


print(
    f"PR-AUC  : {overall_pr_auc:.6f}"
)


print(
    f"Brier   : {overall_brier:.6f}"
)


print(
    f"LogLoss : {overall_logloss:.6f}"
)


# ============================================================
# 8. CREATE AGE
# ============================================================

print("\n[8] Creating applicant segments...")


evaluation["AGE_YEARS"] = (
    -evaluation["DAYS_BIRTH"] / 365.25
)


evaluation["AGE_GROUP"] = pd.cut(
    evaluation["AGE_YEARS"],
    bins=[
        0,
        25,
        35,
        45,
        55,
        65,
        np.inf
    ],
    labels=[
        "<=25",
        "26-35",
        "36-45",
        "46-55",
        "56-65",
        "65+"
    ],
    include_lowest=True
)


# ============================================================
# 9. CREATE INCOME GROUP
# ============================================================

evaluation["INCOME_GROUP"] = pd.qcut(
    evaluation["AMT_INCOME_TOTAL"],
    q=4,
    labels=[
        "LOW",
        "LOWER_MIDDLE",
        "UPPER_MIDDLE",
        "HIGH"
    ],
    duplicates="drop"
)


# ============================================================
# 10. CREATE EMPLOYMENT GROUP
# ============================================================

evaluation["EMPLOYMENT_YEARS"] = np.where(
    evaluation["DAYS_EMPLOYED"] < 0,
    -evaluation["DAYS_EMPLOYED"] / 365.25,
    np.nan
)


evaluation["EMPLOYMENT_GROUP"] = pd.cut(
    evaluation["EMPLOYMENT_YEARS"],
    bins=[
        -0.001,
        1,
        3,
        5,
        10,
        np.inf
    ],
    labels=[
        "<=1Y",
        "1-3Y",
        "3-5Y",
        "5-10Y",
        "10Y+"
    ],
    include_lowest=True
)


# ============================================================
# 11. CREATE PD BANDS
# ============================================================

evaluation["PD_BAND"] = pd.cut(
    evaluation["predicted_pd"],
    bins=[
        -np.inf,
        0.025,
        0.05,
        0.10,
        0.20,
        0.35,
        np.inf
    ],
    labels=[
        "<2.5%",
        "2.5-5%",
        "5-10%",
        "10-20%",
        "20-35%",
        ">35%"
    ]
)


# ============================================================
# 12. CREATE DECISION AT 10% PD
# ============================================================

evaluation["HIGH_RISK_10"] = (
    evaluation["predicted_pd"] >= 0.10
).astype(int)


# ============================================================
# 13. SEGMENT EVALUATION FUNCTION
# ============================================================

def evaluate_segment(
    df,
    segment_name,
    segment_column
):

    rows = []


    for group_value, group_df in df.groupby(
        segment_column,
        observed=True
    ):

        group_df = group_df.copy()


        n = len(group_df)


        if n == 0:
            continue


        default_rate = group_df[
            "target"
        ].mean()


        predicted_high_risk_rate = group_df[
            "HIGH_RISK_10"
        ].mean()


        mean_pd = group_df[
            "predicted_pd"
        ].mean()


        median_pd = group_df[
            "predicted_pd"
        ].median()


        if group_df["target"].nunique() >= 2:

            auc = roc_auc_score(
                group_df["target"],
                group_df["predicted_pd"]
            )

            pr_auc = average_precision_score(
                group_df["target"],
                group_df["predicted_pd"]
            )

        else:

            auc = np.nan
            pr_auc = np.nan


        brier = brier_score_loss(
            group_df["target"],
            group_df["predicted_pd"]
        )


        logloss = log_loss(
            group_df["target"],
            group_df["predicted_pd"],
            labels=[0, 1]
        )


        rows.append({

            "segment_type":
                segment_name,

            "segment":
                str(group_value),

            "n":
                n,

            "population_share":
                n / len(df),

            "observed_default_rate":
                default_rate,

            "mean_predicted_pd":
                mean_pd,

            "median_predicted_pd":
                median_pd,

            "high_risk_rate_at_10pct":
                predicted_high_risk_rate,

            "roc_auc":
                auc,

            "pr_auc":
                pr_auc,

            "brier":
                brier,

            "log_loss":
                logloss

        })


    return pd.DataFrame(rows)


# ============================================================
# 14. RUN SEGMENT ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("SEGMENT STABILITY ANALYSIS")
print("=" * 70)


results = []


# Gender
gender_results = evaluate_segment(
    evaluation,
    "GENDER",
    "CODE_GENDER"
)


results.append(
    gender_results
)


# Income
income_results = evaluate_segment(
    evaluation,
    "INCOME",
    "INCOME_GROUP"
)


results.append(
    income_results
)


# Education
education_results = evaluate_segment(
    evaluation,
    "EDUCATION",
    "NAME_EDUCATION_TYPE"
)


results.append(
    education_results
)


# Age
age_results = evaluate_segment(
    evaluation,
    "AGE",
    "AGE_GROUP"
)


results.append(
    age_results
)


# Employment
employment_results = evaluate_segment(
    evaluation,
    "EMPLOYMENT",
    "EMPLOYMENT_GROUP"
)


results.append(
    employment_results
)


# PD band
pd_results = evaluate_segment(
    evaluation,
    "PD_BAND",
    "PD_BAND"
)


results.append(
    pd_results
)


all_results = pd.concat(
    results,
    ignore_index=True
)


# ============================================================
# 15. PRINT RESULTS
# ============================================================

def print_results(
    title,
    dataframe
):

    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

    display_columns = [
        "segment",
        "n",
        "observed_default_rate",
        "mean_predicted_pd",
        "high_risk_rate_at_10pct",
        "roc_auc",
        "pr_auc",
        "brier",
        "log_loss"
    ]

    print(
        dataframe[
            display_columns
        ].to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}"
        )
    )


print_results(
    "GENDER STABILITY",
    gender_results
)


print_results(
    "INCOME STABILITY",
    income_results
)


print_results(
    "EDUCATION STABILITY",
    education_results
)


print_results(
    "AGE STABILITY",
    age_results
)


print_results(
    "EMPLOYMENT STABILITY",
    employment_results
)


print_results(
    "PD BAND DISTRIBUTION",
    pd_results
)


# ============================================================
# 16. FIND WORST SEGMENTS
# ============================================================

print("\n" + "=" * 70)
print("STRESS TEST — WORST SEGMENTS")
print("=" * 70)


# Only consider reasonably sized groups.

large_groups = all_results[
    all_results["n"] >= 100
].copy()


worst_auc = large_groups.sort_values(
    "roc_auc",
    ascending=True
).head(5)


worst_brier = large_groups.sort_values(
    "brier",
    ascending=False
).head(5)


worst_logloss = large_groups.sort_values(
    "log_loss",
    ascending=False
).head(5)


print("\nLowest ROC-AUC segments:")


print(
    worst_auc[
        [
            "segment_type",
            "segment",
            "n",
            "roc_auc"
        ]
    ].to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)


print("\nHighest Brier-score segments:")


print(
    worst_brier[
        [
            "segment_type",
            "segment",
            "n",
            "brier"
        ]
    ].to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)


print("\nHighest LogLoss segments:")


print(
    worst_logloss[
        [
            "segment_type",
            "segment",
            "n",
            "log_loss"
        ]
    ].to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)


# ============================================================
# 17. PD CALIBRATION BY DECILE
# ============================================================

print("\n" + "=" * 70)
print("PD DECILE CALIBRATION")
print("=" * 70)


evaluation["PD_DECILE"] = pd.qcut(
    evaluation["predicted_pd"],
    q=10,
    labels=False,
    duplicates="drop"
)


calibration = (
    evaluation
    .groupby(
        "PD_DECILE",
        observed=True
    )
    .agg(
        observations=(
            "target",
            "size"
        ),

        mean_predicted_pd=(
            "predicted_pd",
            "mean"
        ),

        observed_default_rate=(
            "target",
            "mean"
        )
    )
    .reset_index()
)


calibration["calibration_gap"] = (
    calibration["observed_default_rate"]
    -
    calibration["mean_predicted_pd"]
)


print(
    calibration.to_string(
        index=False,
        float_format=lambda x: f"{x:.5f}"
    )
)


# ============================================================
# 18. OVERALL STABILITY DIAGNOSTICS
# ============================================================

print("\n" + "=" * 70)
print("OVERALL STABILITY DIAGNOSTICS")
print("=" * 70)


segment_auc_values = (
    large_groups["roc_auc"]
    .dropna()
)


segment_brier_values = (
    large_groups["brier"]
    .dropna()
)


segment_logloss_values = (
    large_groups["log_loss"]
    .dropna()
)


print(
    "Overall ROC-AUC:",
    f"{overall_auc:.6f}"
)


print(
    "Segment ROC-AUC minimum:",
    f"{segment_auc_values.min():.6f}"
)


print(
    "Segment ROC-AUC maximum:",
    f"{segment_auc_values.max():.6f}"
)


print(
    "Segment ROC-AUC range:",
    f"{segment_auc_values.max() - segment_auc_values.min():.6f}"
)


print(
    "Overall Brier:",
    f"{overall_brier:.6f}"
)


print(
    "Segment Brier maximum:",
    f"{segment_brier_values.max():.6f}"
)


print(
    "Overall LogLoss:",
    f"{overall_logloss:.6f}"
)


print(
    "Segment LogLoss maximum:",
    f"{segment_logloss_values.max():.6f}"
)


# ============================================================
# 19. SAVE RESULTS
# ============================================================

print("\n[9] Saving stability analysis...")


all_results.to_csv(
    OUTPUT_FILE,
    index=False
)


calibration.to_csv(
    "kavach_model_calibration_by_decile.csv",
    index=False
)


summary = pd.DataFrame({

    "metric": [

        "overall_roc_auc",

        "overall_pr_auc",

        "overall_brier",

        "overall_log_loss",

        "minimum_segment_roc_auc",

        "maximum_segment_roc_auc",

        "segment_roc_auc_range",

        "maximum_segment_brier",

        "maximum_segment_log_loss",

        "target_alignment_rate"

    ],

    "value": [

        overall_auc,

        overall_pr_auc,

        overall_brier,

        overall_logloss,

        segment_auc_values.min(),

        segment_auc_values.max(),

        segment_auc_values.max()
        -
        segment_auc_values.min(),

        segment_brier_values.max(),

        segment_logloss_values.max(),

        target_alignment_rate

    ]

})


summary.to_csv(
    SUMMARY_FILE,
    index=False
)


# ============================================================
# 20. FINAL STATUS
# ============================================================

print("\nSaved:")

print(
    f"  {OUTPUT_FILE}"
)

print(
    "  kavach_model_calibration_by_decile.csv"
)

print(
    f"  {SUMMARY_FILE}"
)


print("\n" + "=" * 70)
print("METHODOLOGY WARNING")
print("=" * 70)

print(
"""
This analysis evaluates stability of the baseline
Logistic Regression model on the Home Credit benchmark.

It does NOT establish stability on Kavach's intended
target population.

The analysis checks whether model discrimination,
calibration-related metrics and predicted-risk rates
vary substantially across observable benchmark groups.

Important limitations:

1. Home Credit is not Kavach's target population.

2. These results are benchmark diagnostics.

3. Group-level differences do not automatically imply
   discrimination.

4. Protected-group analysis requires legally and
   statistically appropriate methodology.

5. Production stability requires:

   - target-population data
   - out-of-time validation
   - population stability monitoring
   - calibration monitoring
   - fairness analysis
   - drift detection
   - observed repayment outcomes
   - operational monitoring

The key principle is:

OVERALL MODEL PERFORMANCE
        is NOT
SUFFICIENT EVIDENCE OF MODEL STABILITY.

A production model must remain reliable
across relevant populations and time periods.
"""
)


print("=" * 70)
print("MODEL STRESS & STABILITY ANALYSIS COMPLETE")
print("=" * 70)
