import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from sklearn.preprocessing import (
    OneHotEncoder,
    StandardScaler
)

from sklearn.impute import SimpleImputer

from sklearn.linear_model import LogisticRegression

from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    brier_score_loss,
    log_loss
)

print("=" * 70)
print("KAVACH PULSE — THIN-FILE + ALTERNATIVE DATA MODEL")
print("=" * 70)


# =========================================================
# 1. LOAD DATA
# =========================================================

print("\n[1] Loading datasets...")

thin = pd.read_csv(
    "kavach_traditional_baseline.csv"
)

alternative = pd.read_csv(
    "kavach_synthetic_alternative_data.csv"
)

print(
    "Traditional dataset:",
    thin.shape
)

print(
    "Alternative dataset:",
    alternative.shape
)


# =========================================================
# 2. REMOVE FEATURES FROM TRADITIONAL DATA
# =========================================================

thin_remove = [
    "EXT_SOURCE_1",
    "EXT_SOURCE_2",
    "EXT_SOURCE_3",

    "AMT_REQ_CREDIT_BUREAU_HOUR",
    "AMT_REQ_CREDIT_BUREAU_DAY",
    "AMT_REQ_CREDIT_BUREAU_WEEK",
    "AMT_REQ_CREDIT_BUREAU_MON",
    "AMT_REQ_CREDIT_BUREAU_QRT",
    "AMT_REQ_CREDIT_BUREAU_YEAR",

    "DAYS_BIRTH",
    "DAYS_EMPLOYED",
    "DAYS_REGISTRATION",
    "DAYS_ID_PUBLISH",
]

thin = thin.drop(
    columns=thin_remove,
    errors="ignore"
)


# =========================================================
# 3. EXTRACT TARGET
# =========================================================

y = thin["TARGET"].copy()

thin = thin.drop(
    columns=["TARGET"]
)


# =========================================================
# 4. REMOVE TARGET FROM ALTERNATIVE DATA
# =========================================================

alternative_features = alternative.drop(
    columns=["TARGET"]
)


# =========================================================
# 5. COMBINE DATA
# =========================================================
#
# Both files were generated from the same original row
# order, so the rows correspond.
#
# =========================================================

X = pd.concat(
    [
        thin.reset_index(drop=True),
        alternative_features.reset_index(drop=True)
    ],
    axis=1
)

print(
    "\nCombined feature dataset:",
    X.shape
)

print(
    "Target:",
    y.shape
)


# =========================================================
# 6. CHECK FOR DUPLICATE COLUMN NAMES
# =========================================================

duplicate_columns = (
    X.columns[
        X.columns.duplicated()
    ]
    .tolist()
)

if duplicate_columns:

    print(
        "\nWARNING: duplicate columns found:"
    )

    print(
        duplicate_columns
    )

    raise ValueError(
        "Duplicate feature names detected."
    )


# =========================================================
# 7. TRAIN / VALIDATION / TEST SPLIT
# =========================================================
#
# IMPORTANT:
# Same random_state and same split structure as the
# thin-file experiment.
#
# =========================================================

indices = np.arange(
    len(X)
)

train_idx, temp_idx = train_test_split(
    indices,
    test_size=0.30,
    stratify=y,
    random_state=42
)

val_idx, test_idx = train_test_split(
    temp_idx,
    test_size=0.50,
    stratify=y.iloc[temp_idx],
    random_state=42
)

X_train = X.iloc[train_idx]
X_val = X.iloc[val_idx]
X_test = X.iloc[test_idx]

y_train = y.iloc[train_idx]
y_val = y.iloc[val_idx]
y_test = y.iloc[test_idx]

print("\nSplit sizes:")

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
# 8. IDENTIFY FEATURE TYPES
# =========================================================

categorical_features = (
    X_train
    .select_dtypes(
        include=["object"]
    )
    .columns
    .tolist()
)

numeric_features = (
    X_train
    .select_dtypes(
        include=np.number
    )
    .columns
    .tolist()
)

print(
    "\nNumeric features:",
    len(numeric_features)
)

print(
    "Categorical features:",
    len(categorical_features)
)


# =========================================================
# 9. NUMERIC PIPELINE
# =========================================================

numeric_pipeline = Pipeline(
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
)


# =========================================================
# 10. CATEGORICAL PIPELINE
# =========================================================

categorical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(
                strategy="most_frequent"
            )
        ),

        (
            "onehot",
            OneHotEncoder(
                handle_unknown="ignore"
            )
        )
    ]
)


# =========================================================
# 11. PREPROCESSOR
# =========================================================

preprocessor = ColumnTransformer(
    transformers=[

        (
            "numeric",
            numeric_pipeline,
            numeric_features
        ),

        (
            "categorical",
            categorical_pipeline,
            categorical_features
        )
    ]
)


# =========================================================
# 12. LOGISTIC REGRESSION
# =========================================================

model = LogisticRegression(
    max_iter=1000,
    solver="lbfgs"
)


# =========================================================
# 13. COMPLETE PIPELINE
# =========================================================

pipeline = Pipeline(
    steps=[

        (
            "preprocessor",
            preprocessor
        ),

        (
            "model",
            model
        )
    ]
)


# =========================================================
# 14. TRAIN
# =========================================================

print(
    "\n[2] Training combined model..."
)

pipeline.fit(
    X_train,
    y_train
)

print(
    "Training complete."
)


# =========================================================
# 15. PREDICTIONS
# =========================================================

val_prob = pipeline.predict_proba(
    X_val
)[:, 1]

test_prob = pipeline.predict_proba(
    X_test
)[:, 1]


# =========================================================
# 16. EVALUATION FUNCTION
# =========================================================

def evaluate(
    name,
    y_true,
    probability
):

    roc = roc_auc_score(
        y_true,
        probability
    )

    pr_auc = average_precision_score(
        y_true,
        probability
    )

    brier = brier_score_loss(
        y_true,
        probability
    )

    loss = log_loss(
        y_true,
        probability
    )

    print(
        f"\n{name}"
    )

    print(
        "-" * 40
    )

    print(
        f"ROC-AUC : {roc:.4f}"
    )

    print(
        f"PR-AUC  : {pr_auc:.4f}"
    )

    print(
        f"Brier   : {brier:.4f}"
    )

    print(
        f"LogLoss : {loss:.4f}"
    )

    return {
        "roc_auc": roc,
        "pr_auc": pr_auc,
        "brier": brier,
        "log_loss": loss
    }


# =========================================================
# 17. EVALUATE
# =========================================================

val_metrics = evaluate(
    "VALIDATION",
    y_val,
    val_prob
)

test_metrics = evaluate(
    "TEST",
    y_test,
    test_prob
)


# =========================================================
# 18. LOAD THIN-FILE BASELINE PREDICTIONS
# =========================================================
#
# This allows direct comparison on the SAME test set.
#
# =========================================================

thin_predictions = pd.read_csv(
    "kavach_thin_file_predictions.csv"
)

thin_prob = (
    thin_predictions[
        "PREDICTED_PD"
    ]
)

thin_actual = (
    thin_predictions[
        "ACTUAL_TARGET"
    ]
)


# =========================================================
# 19. VERIFY TARGET ALIGNMENT
# =========================================================

if not np.array_equal(
    y_test.to_numpy(),
    thin_actual.to_numpy()
):

    print(
        "\nWARNING:"
    )

    print(
        "Test targets are not aligned with the saved "
        "thin-file predictions."
    )

    print(
        "Direct comparison cannot be trusted."
    )

    raise ValueError(
        "Test-set alignment failure."
    )


# =========================================================
# 20. BASELINE METRICS
# =========================================================

baseline_roc = roc_auc_score(
    thin_actual,
    thin_prob
)

baseline_pr = average_precision_score(
    thin_actual,
    thin_prob
)

baseline_brier = brier_score_loss(
    thin_actual,
    thin_prob
)

baseline_loss = log_loss(
    thin_actual,
    thin_prob
)


# =========================================================
# 21. IMPROVEMENT
# =========================================================

delta_roc = (
    test_metrics["roc_auc"]
    - baseline_roc
)

delta_pr = (
    test_metrics["pr_auc"]
    - baseline_pr
)

delta_brier = (
    test_metrics["brier"]
    - baseline_brier
)

delta_loss = (
    test_metrics["log_loss"]
    - baseline_loss
)


# =========================================================
# 22. COMPARISON
# =========================================================

comparison = pd.DataFrame({

    "metric": [
        "ROC-AUC",
        "PR-AUC",
        "Brier",
        "LogLoss"
    ],

    "thin_file": [
        baseline_roc,
        baseline_pr,
        baseline_brier,
        baseline_loss
    ],

    "thin_plus_alternative": [
        test_metrics["roc_auc"],
        test_metrics["pr_auc"],
        test_metrics["brier"],
        test_metrics["log_loss"]
    ],

    "difference": [
        delta_roc,
        delta_pr,
        delta_brier,
        delta_loss
    ]
})


print(
    "\n"
    + "=" * 70
)

print(
    "THIN-FILE vs THIN + ALTERNATIVE"
)

print(
    "=" * 70
)

print(
    comparison.round(6).to_string(
        index=False
    )
)


# =========================================================
# 23. SAVE COMPARISON
# =========================================================

comparison.to_csv(
    "kavach_model_comparison.csv",
    index=False
)


# =========================================================
# 24. SAVE MODEL
# =========================================================

joblib.dump(
    pipeline,
    "kavach_alternative_model.joblib"
)


# =========================================================
# 25. SAVE TEST PREDICTIONS
# =========================================================

predictions = pd.DataFrame({

    "ACTUAL_TARGET":
        y_test.to_numpy(),

    "THIN_FILE_PD":
        thin_prob.to_numpy(),

    "THIN_PLUS_ALTERNATIVE_PD":
        test_prob
})

predictions.to_csv(
    "kavach_alternative_test_predictions.csv",
    index=False
)


# =========================================================
# 26. SAVE METADATA
# =========================================================

metadata = {

    "model_type":
        "Logistic Regression",

    "dataset_size":
        len(X),

    "traditional_features":
        len(thin.columns),

    "alternative_features":
        len(alternative_features.columns),

    "target_prevalence":
        float(y.mean()),

    "thin_file_test_auc":
        float(baseline_roc),

    "combined_test_auc":
        float(test_metrics["roc_auc"]),

    "auc_improvement":
        float(delta_roc),

    "thin_file_test_pr_auc":
        float(baseline_pr),

    "combined_test_pr_auc":
        float(test_metrics["pr_auc"]),

    "pr_auc_improvement":
        float(delta_pr),

    "synthetic_alternative_data":
        True
}

pd.Series(
    metadata
).to_json(
    "kavach_alternative_model_metadata.json",
    indent=2
)


# =========================================================
# 27. FINAL OUTPUT
# =========================================================

print(
    "\nSaved:"
)

print(
    "  kavach_alternative_model.joblib"
)

print(
    "  kavach_alternative_test_predictions.csv"
)

print(
    "  kavach_model_comparison.csv"
)

print(
    "  kavach_alternative_model_metadata.json"
)

print(
    "\nIMPORTANT:"
)

print(
    "The alternative data used in this experiment is SYNTHETIC."
)

print(
    "The results are a controlled simulation, NOT real-world"
)

print(
    "evidence of gig-worker credit performance."
)

print(
    "\n"
    + "=" * 70
)

print(
    "ALTERNATIVE MODEL EXPERIMENT COMPLETE"
)

print(
    "=" * 70
)
