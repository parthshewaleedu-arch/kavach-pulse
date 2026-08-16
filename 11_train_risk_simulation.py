import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression

from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    brier_score_loss,
    log_loss
)

print("=" * 70)
print("KAVACH PULSE — SYNTHETIC RISK MODEL SIMULATION")
print("=" * 70)

RANDOM_SEED = 42

rng = np.random.default_rng(
    RANDOM_SEED
)


# =========================================================
# 1. LOAD BEHAVIORAL FEATURES
# =========================================================

print("\n[1] Loading behavioral features...")

df = pd.read_csv(
    "kavach_behavioral_features.csv"
)

print(
    "Dataset:",
    df.shape
)


# =========================================================
# 2. REMOVE IDENTIFIER
# =========================================================

X = df.drop(
    columns=["applicant_id"]
)


# =========================================================
# 3. NORMALIZE SIMULATION VARIABLES
# =========================================================

print(
    "\n[2] Creating simulation variables..."
)


def minmax(series):

    minimum = series.min()
    maximum = series.max()

    if maximum == minimum:
        return pd.Series(
            0.5,
            index=series.index
        )

    return (
        series - minimum
    ) / (
        maximum - minimum
    )


# ---------------------------------------------------------
# Stability
# ---------------------------------------------------------

income_stability = 1 - minmax(
    X["income_cv"]
)

cashflow_stability = 1 - minmax(
    X["cashflow_cv"]
)

payment_stability = (
    X["payment_success_rate"]
)

balance_resilience = minmax(
    X["balance_min"]
)

income_level = minmax(
    X["income_mean"]
)

cashflow_strength = minmax(
    X["net_cashflow_mean"]
)

income_trend_positive = (
    minmax(
        X["income_trend"]
    )
)


# =========================================================
# 4. SYNTHETIC LATENT RISK FUNCTION
# =========================================================
#
# IMPORTANT:
#
# These weights are simulation assumptions.
#
# They are NOT learned from real borrowers.
#
# They must NOT be presented as empirical evidence.
#
# =========================================================

print(
    "\n[3] Generating synthetic repayment propensity..."
)


risk_signal = (

    # Positive financial stability
    -1.10 * income_stability

    -0.70 * cashflow_stability

    -0.90 * payment_stability

    -0.60 * balance_resilience

    -0.45 * income_level

    -0.50 * cashflow_strength

    -0.25 * income_trend_positive

)


# Add applicant-level stochastic variation.

risk_signal += rng.normal(
    0,
    0.45,
    len(X)
)


# ---------------------------------------------------------
# Convert latent risk to probability
# ---------------------------------------------------------

def sigmoid(x):

    return 1 / (
        1 + np.exp(-x)
    )


# Shift the simulated population
# toward a realistic minority adverse-event rate.

latent_pd = sigmoid(
    risk_signal + 2.0
)


# =========================================================
# 5. GENERATE SYNTHETIC OUTCOMES
# =========================================================

print(
    "\n[4] Generating synthetic outcomes..."
)

y = (
    rng.random(
        len(latent_pd)
    )
    < latent_pd
).astype(int)


print(
    "Synthetic event rate:",
    round(
        y.mean() * 100,
        2
    ),
    "%"
)


# =========================================================
# 6. FEATURE SET
# =========================================================

feature_columns = [

    "history_months",

    "platform_tenure_months",

    "income_mean",

    "income_std",

    "income_cv",

    "income_min",

    "income_max",

    "income_trend",

    "bank_inflow_mean",

    "bank_outflow_mean",

    "net_cashflow_mean",

    "net_cashflow_std",

    "cashflow_cv",

    "balance_mean",

    "balance_min",

    "balance_max",

    "payment_success_rate",

    "missed_payment_rate",

    "active_days_mean",

    "inflow_to_outflow_ratio"
]


X = X[
    feature_columns
]


# =========================================================
# 7. TRAIN / VALIDATION / TEST
# =========================================================

print(
    "\n[5] Creating train/validation/test split..."
)

X_train, X_temp, y_train, y_temp = (
    train_test_split(
        X,
        y,
        test_size=0.30,
        stratify=y,
        random_state=RANDOM_SEED
    )
)

X_val, X_test, y_val, y_test = (
    train_test_split(
        X_temp,
        y_temp,
        test_size=0.50,
        stratify=y_temp,
        random_state=RANDOM_SEED
    )
)

print(
    "Train:",
    X_train.shape
)

print(
    "Validation:",
    X_val.shape
)

print(
    "Test:",
    X_test.shape
)


# =========================================================
# 8. PREPROCESSING
# =========================================================

numeric_features = (
    X_train.columns
    .tolist()
)


preprocessor = ColumnTransformer(
    transformers=[

        (
            "numeric",

            Pipeline(
                steps=[

                    (
                        "imputer",

                        SimpleImputer(
                            strategy="median"
                        )
                    ),

                    (
                        "scaler",

                        StandardScaler()
                    )
                ]
            ),

            numeric_features
        )
    ]
)


# =========================================================
# 9. LOGISTIC RISK MODEL
# =========================================================

print(
    "\n[6] Training logistic risk model..."
)

model = Pipeline(
    steps=[

        (
            "preprocessor",
            preprocessor
        ),

        (
            "classifier",

            LogisticRegression(
                max_iter=1000
            )
        )
    ]
)


model.fit(
    X_train,
    y_train
)

print(
    "Training complete."
)


# =========================================================
# 10. EVALUATION
# =========================================================

def evaluate(
    name,
    X_data,
    y_data
):

    probabilities = (
        model
        .predict_proba(
            X_data
        )[:, 1]
    )

    roc = roc_auc_score(
        y_data,
        probabilities
    )

    pr_auc = average_precision_score(
        y_data,
        probabilities
    )

    brier = brier_score_loss(
        y_data,
        probabilities
    )

    loss = log_loss(
        y_data,
        probabilities
    )

    print(
        f"\n{name}"
    )

    print("-" * 45)

    print(
        f"ROC-AUC : {roc:.6f}"
    )

    print(
        f"PR-AUC  : {pr_auc:.6f}"
    )

    print(
        f"Brier   : {brier:.6f}"
    )

    print(
        f"LogLoss : {loss:.6f}"
    )

    return {

        "dataset":
            name,

        "roc_auc":
            roc,

        "pr_auc":
            pr_auc,

        "brier":
            brier,

        "log_loss":
            loss
    }


results = []

results.append(
    evaluate(
        "VALIDATION",
        X_val,
        y_val
    )
)

results.append(
    evaluate(
        "TEST",
        X_test,
        y_test
    )
)


# =========================================================
# 11. PREDICTION DISTRIBUTION
# =========================================================

test_probabilities = (
    model
    .predict_proba(
        X_test
    )[:, 1]
)

print(
    "\n[7] Predicted PD distribution:"
)

print(
    pd.Series(
        test_probabilities
    )
    .describe()
    .round(4)
)


# =========================================================
# 12. SAVE MODEL OUTPUT
# =========================================================

predictions = X_test.copy()

predictions[
    "actual_synthetic_outcome"
] = y_test

predictions[
    "predicted_pd"
] = test_probabilities


predictions.to_csv(
    "kavach_synthetic_risk_predictions.csv",
    index=False
)


pd.DataFrame(
    results
).to_csv(
    "kavach_synthetic_risk_metrics.csv",
    index=False
)


# =========================================================
# 13. IMPORTANT METHODOLOGY NOTICE
# =========================================================

print("\n")
print("=" * 70)

print(
    "METHODOLOGY WARNING"
)

print("=" * 70)

print(
    """
This experiment uses SYNTHETIC repayment outcomes.

The outcome-generating process was created
from simulation assumptions.

Therefore:

1. The model performance is NOT evidence of
   real-world credit predictive performance.

2. ROC-AUC cannot be presented as validation
   on real borrowers.

3. The synthetic model exists only to test
   the Kavach technical pipeline.

4. Real production validation requires
   consented historical behavioral data linked
   to observed repayment outcomes.
"""
)

print("=" * 70)
print(
    "SYNTHETIC RISK MODEL COMPLETE"
)
print("=" * 70)
