import os
import numpy as np
import pandas as pd

from sklearn.metrics import (
    roc_auc_score,
    precision_score,
    recall_score,
    confusion_matrix
)


print("=" * 70)
print("KAVACH PULSE — COST-SENSITIVE THRESHOLD OPTIMIZATION")
print("=" * 70)


# =========================================================
# CONFIGURATION
# =========================================================

PREDICTION_FILE = (
    "kavach_logistic_test_predictions.csv"
)

TARGET_FILE = (
    "application_train.csv"
)


# Illustrative business costs.
#
# IMPORTANT:
# These are NOT real lender economics.
# They exist only to demonstrate the optimization
# methodology.

COST_FALSE_POSITIVE = 10.0
COST_FALSE_NEGATIVE = 2.0
COST_MANUAL_REVIEW = 1.0


# =========================================================
# 1. LOAD REAL BENCHMARK PREDICTIONS
# =========================================================

print(
    "\n[1] Loading Home Credit benchmark predictions..."
)


if not os.path.exists(PREDICTION_FILE):

    raise FileNotFoundError(
        f"Missing {PREDICTION_FILE}"
    )


pred = pd.read_csv(
    PREDICTION_FILE
)


print(
    "Prediction dataset:",
    pred.shape
)

print(
    "Prediction columns:"
)

print(
    pred.columns.tolist()
)


# =========================================================
# 2. IDENTIFY TARGET / PREDICTION COLUMNS
# =========================================================
# =========================================================
# 2. IDENTIFY BENCHMARK COLUMNS
# =========================================================

print(
    "\n[2] Identifying benchmark columns..."
)

required_columns = [
    "ACTUAL_TARGET",
    "PREDICTED_PD"
]

missing_columns = [
    col
    for col in required_columns
    if col not in pred.columns
]

if missing_columns:

    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

print(
    "Actual target column: ACTUAL_TARGET"
)

print(
    "Predicted probability column: PREDICTED_PD"
)


# =========================================================
# 3. BUILD EVALUATION DATASET
# =========================================================

print(
    "\n[3] Building evaluation dataset..."
)

evaluation = pred[
    [
        "ACTUAL_TARGET",
        "PREDICTED_PD"
    ]
].copy()


evaluation = evaluation.rename(
    columns={
        "ACTUAL_TARGET": "target",
        "PREDICTED_PD": "predicted_pd"
    }
)


evaluation["target"] = (
    evaluation["target"]
    .astype(int)
)


evaluation["predicted_pd"] = (
    pd.to_numeric(
        evaluation["predicted_pd"],
        errors="coerce"
    )
)


evaluation = evaluation.dropna(
    subset=[
        "target",
        "predicted_pd"
    ]
)


print(
    "Evaluation observations:",
    len(evaluation)
)

print(
    "Observed default rate:",
    f"{evaluation['target'].mean() * 100:.2f}%"
)

print(
    "\nPredicted PD distribution:"
)

print(
    evaluation[
        "predicted_pd"
    ].describe()
)
# =========================================================
# 4. BASIC MODEL CHECK
# =========================================================

print(
    "\n[4] Checking benchmark model..."
)


auc = roc_auc_score(

    evaluation[
        "target"
    ],

    evaluation[
        "predicted_pd"
    ]

)


print(
    f"ROC-AUC: {auc:.6f}"
)


# =========================================================
# 5. DEFINE DECISION STRATEGIES
# =========================================================
#
# Strategy A:
#   Binary decision
#
# Strategy B:
#   Low-risk -> accept
#   Middle -> manual review
#   High-risk -> decline/review
#
# Strategy B is more representative of Kavach.
#
# =========================================================


def evaluate_binary_threshold(
    data,
    threshold
):

    y = data[
        "target"
    ].to_numpy()

    p = data[
        "predicted_pd"
    ].to_numpy()


    predicted_default = (
        p >= threshold
    ).astype(int)


    tn, fp, fn, tp = (
        confusion_matrix(
            y,
            predicted_default,
            labels=[
                0,
                1
            ]
        ).ravel()
    )


    cost = (

        fp
        *
        COST_FALSE_POSITIVE

        +

        fn
        *
        COST_FALSE_NEGATIVE

    )


    return {

        "threshold":
            threshold,

        "false_positives":
            fp,

        "false_negatives":
            fn,

        "true_positives":
            tp,

        "true_negatives":
            tn,

        "total_cost":
            cost,

        "cost_per_applicant":
            cost / len(data),

        "predicted_high_risk_rate":
            predicted_default.mean()

    }


# =========================================================
# 6. BINARY THRESHOLD SEARCH
# =========================================================

print(
    "\n[5] Searching binary decision thresholds..."
)


thresholds = np.arange(
    0.01,
    0.51,
    0.005
)


binary_results = []


for threshold in thresholds:

    binary_results.append(

        evaluate_binary_threshold(
            evaluation,
            threshold
        )

    )


binary_results = pd.DataFrame(
    binary_results
)


best_binary = binary_results.loc[
    binary_results[
        "total_cost"
    ].idxmin()
]


print(
    "\nBest binary threshold:"
)

print(
    best_binary.to_string()
)


# =========================================================
# 7. THREE-WAY KAVACH POLICY
# =========================================================
#
# Three zones:
#
# LOW RISK
#     -> PASS
#
# MIDDLE
#     -> MANUAL REVIEW
#
# HIGH RISK
#     -> DECLINE / REVIEW
#
# =========================================================


def evaluate_three_way_policy(
    data,
    pass_threshold,
    decline_threshold
):

    y = data[
        "target"
    ].to_numpy()

    p = data[
        "predicted_pd"
    ].to_numpy()


    decisions = np.where(

        p < pass_threshold,

        "PASS",

        np.where(

            p < decline_threshold,

            "MANUAL_REVIEW",

            "DECLINE"

        )

    )


    # ---------------------------------------------
    # Classification:
    #
    # PASS = predicted good
    # DECLINE = predicted risky
    #
    # MANUAL_REVIEW is intentionally treated
    # separately.
    # ---------------------------------------------

    pass_mask = (
        decisions == "PASS"
    )

    decline_mask = (
        decisions == "DECLINE"
    )

    review_mask = (
        decisions == "MANUAL_REVIEW"
    )


    # False approval:
    #
    # Risky applicant was automatically passed.

    false_approvals = np.sum(

        pass_mask
        &
        (y == 1)

    )


    # False rejection:
    #
    # Good applicant was automatically declined.

    false_rejections = np.sum(

        decline_mask
        &
        (y == 0)

    )


    manual_reviews = np.sum(
        review_mask
    )


    total_cost = (

        false_approvals
        *
        COST_FALSE_POSITIVE

        +

        false_rejections
        *
        COST_FALSE_NEGATIVE

        +

        manual_reviews
        *
        COST_MANUAL_REVIEW

    )


    return {

        "pass_threshold":
            pass_threshold,

        "decline_threshold":
            decline_threshold,

        "false_approvals":
            false_approvals,

        "false_rejections":
            false_rejections,

        "manual_reviews":
            manual_reviews,

        "pass_rate":
            pass_mask.mean(),

        "manual_review_rate":
            review_mask.mean(),

        "decline_rate":
            decline_mask.mean(),

        "total_cost":
            total_cost,

        "cost_per_applicant":
            total_cost / len(data)

    }


# =========================================================
# 8. SEARCH THREE-WAY POLICY SPACE
# =========================================================

print(
    "\n[6] Searching three-way policy thresholds..."
)


policy_results = []


pass_thresholds = np.arange(
    0.03,
    0.20,
    0.01
)


decline_thresholds = np.arange(
    0.10,
    0.35,
    0.01
)


for pass_threshold in pass_thresholds:

    for decline_threshold in decline_thresholds:

        # Invalid policy:
        #
        # decline threshold must be higher
        # than pass threshold.

        if (
            decline_threshold
            <=
            pass_threshold
        ):

            continue


        result = evaluate_three_way_policy(

            evaluation,

            pass_threshold,

            decline_threshold

        )


        policy_results.append(
            result
        )


policy_results = pd.DataFrame(
    policy_results
)


best_policy = policy_results.loc[
    policy_results[
        "total_cost"
    ].idxmin()
]


print(
    "\nBest three-way policy:"
)

print(
    best_policy.to_string()
)


# =========================================================
# 9. SHOW TOP POLICIES
# =========================================================

print(
    "\n" + "=" * 70
)

print(
    "TOP 10 THREE-WAY POLICIES"
)

print(
    "=" * 70
)


print(

    policy_results
    .sort_values(
        "total_cost"
    )
    .head(10)
    .to_string(
        index=False
    )

)


# =========================================================
# 10. BASELINE COMPARISON
# =========================================================

print(
    "\n" + "=" * 70
)

print(
    "POLICY COMPARISON"
)

print(
    "=" * 70
)


# Baseline: everyone goes to manual review.

baseline_manual_cost = (

    len(evaluation)
    *
    COST_MANUAL_REVIEW

)


# Baseline: everybody accepted.

all_accept_cost = (

    (
        evaluation[
            "target"
        ]
        ==
        1
    )
    .sum()
    *
    COST_FALSE_POSITIVE

)


# Baseline: everybody declined.

all_decline_cost = (

    (
        evaluation[
            "target"
        ]
        ==
        0
    )
    .sum()
    *
    COST_FALSE_NEGATIVE

)


comparison = pd.DataFrame({

    "strategy": [

        "ALL_MANUAL_REVIEW",

        "ALL_ACCEPT",

        "ALL_DECLINE",

        "BEST_BINARY",

        "BEST_THREE_WAY"

    ],

    "total_cost": [

        baseline_manual_cost,

        all_accept_cost,

        all_decline_cost,

        best_binary[
            "total_cost"
        ],

        best_policy[
            "total_cost"
        ]

    ]

})


comparison[
    "cost_per_applicant"
] = (

    comparison[
        "total_cost"
    ]
    /
    len(evaluation)

)


print(
    comparison.to_string(
        index=False
    )
)


# =========================================================
# 11. KAVACH POLICY INTERPRETATION
# =========================================================

print(
    "\n" + "=" * 70
)

print(
    "KAVACH POLICY INTERPRETATION"
)

print(
    "=" * 70
)


print(
    f"""
Illustrative cost assumptions:

False approval cost:
    {COST_FALSE_POSITIVE}

False rejection cost:
    {COST_FALSE_NEGATIVE}

Manual review cost:
    {COST_MANUAL_REVIEW}

Best three-way policy:

PASS below:
    {best_policy['pass_threshold']:.3f}

MANUAL REVIEW between:
    {best_policy['pass_threshold']:.3f}
    and
    {best_policy['decline_threshold']:.3f}

DECLINE / REVIEW above:
    {best_policy['decline_threshold']:.3f}

Resulting routing:

PASS:
    {best_policy['pass_rate'] * 100:.2f}%

MANUAL REVIEW:
    {best_policy['manual_review_rate'] * 100:.2f}%

DECLINE:
    {best_policy['decline_rate'] * 100:.2f}%
"""
)


# =========================================================
# 12. SAVE RESULTS
# =========================================================

binary_results.to_csv(

    "kavach_binary_threshold_analysis.csv",

    index=False

)


policy_results.to_csv(

    "kavach_three_way_policy_analysis.csv",

    index=False

)


comparison.to_csv(

    "kavach_policy_cost_comparison.csv",

    index=False

)


# =========================================================
# 13. METHODOLOGY WARNING
# =========================================================

print(
    "\n" + "=" * 70
)

print(
    "METHODOLOGY WARNING"
)

print(
    "=" * 70
)

print(
    """
This experiment uses the public Home Credit
benchmark dataset.

It demonstrates decision-threshold optimization
using observed historical outcomes.

However:

1. Home Credit is NOT Kavach's target population.

2. The cost values are illustrative.

3. The optimized thresholds are NOT production
   lending thresholds.

4. The results do NOT establish that Kavach
   improves lending outcomes.

5. Production optimization requires:
   - target-population data
   - validated repayment outcomes
   - actual lender economics
   - expected-loss modelling
   - regulatory constraints
   - fairness constraints
   - operational review capacity

The important methodological principle is:

MODEL SCORE
     ↓
BUSINESS COST
     ↓
DECISION THRESHOLD

rather than choosing thresholds arbitrarily.
"""
)

print(
    "=" * 70
)

print(
    "COST-SENSITIVE THRESHOLD OPTIMIZATION COMPLETE"
)

print(
    "=" * 70
)
