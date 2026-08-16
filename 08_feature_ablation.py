import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression

from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    brier_score_loss,
    log_loss
)

print("=" * 70)
print("KAVACH PULSE — REAL-DATA FEATURE ABLATION")
print("=" * 70)


# =========================================================
# 1. LOAD
# =========================================================

df = pd.read_csv(
    "kavach_traditional_baseline.csv"
)

print("\nDataset:", df.shape)

y = df["TARGET"].copy()

X = df.drop(
    columns=["TARGET"]
)


# =========================================================
# 2. DEFINE FEATURE GROUPS
# =========================================================

external_features = [
    "EXT_SOURCE_1",
    "EXT_SOURCE_2",
    "EXT_SOURCE_3"
]

bureau_features = [
    "AMT_REQ_CREDIT_BUREAU_HOUR",
    "AMT_REQ_CREDIT_BUREAU_DAY",
    "AMT_REQ_CREDIT_BUREAU_WEEK",
    "AMT_REQ_CREDIT_BUREAU_MON",
    "AMT_REQ_CREDIT_BUREAU_QRT",
    "AMT_REQ_CREDIT_BUREAU_YEAR"
]

raw_date_features = [
    "DAYS_BIRTH",
    "DAYS_EMPLOYED",
    "DAYS_REGISTRATION",
    "DAYS_ID_PUBLISH"
]


# =========================================================
# 3. BUILD FOUR FEATURE SETS
# =========================================================

# ---------------------------------------------------------
# MODEL 1 — THIN FILE
# ---------------------------------------------------------

thin_remove = (
    external_features
    + bureau_features
    + raw_date_features
)

X_thin = X.drop(
    columns=thin_remove,
    errors="ignore"
)


# ---------------------------------------------------------
# MODEL 2 — THIN + EXTERNAL
# ---------------------------------------------------------

thin_external_remove = (
    bureau_features
    + raw_date_features
)

X_thin_external = X.drop(
    columns=thin_external_remove,
    errors="ignore"
)


# ---------------------------------------------------------
# MODEL 3 — THIN + BUREAU
# ---------------------------------------------------------

thin_bureau_remove = (
    external_features
    + raw_date_features
)

X_thin_bureau = X.drop(
    columns=thin_bureau_remove,
    errors="ignore"
)


# ---------------------------------------------------------
# MODEL 4 — FULL TRADITIONAL
# ---------------------------------------------------------

full_remove = raw_date_features

X_full = X.drop(
    columns=full_remove,
    errors="ignore"
)


datasets = {

    "Thin-file":
        X_thin,

    "Thin + External":
        X_thin_external,

    "Thin + Bureau":
        X_thin_bureau,

    "Full Traditional":
        X_full
}


# =========================================================
# 4. CREATE ONE COMMON SPLIT
# =========================================================
#
# This is critical.
#
# Every model sees exactly the same applicants in:
#
# TRAIN
# VALIDATION
# TEST
#
# =========================================================

indices = np.arange(
    len(df)
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

print("\nCommon split:")

print(
    "Train:",
    len(train_idx)
)

print(
    "Validation:",
    len(val_idx)
)

print(
    "Test:",
    len(test_idx)
)


# =========================================================
# 5. MODEL FUNCTION
# =========================================================

def train_and_evaluate(
    name,
    X_data
):

    print("\n")
    print("=" * 70)
    print(name)
    print("=" * 70)

    X_train = X_data.iloc[train_idx]
    X_val = X_data.iloc[val_idx]
    X_test = X_data.iloc[test_idx]

    y_train = y.iloc[train_idx]
    y_val = y.iloc[val_idx]
    y_test = y.iloc[test_idx]

    # -----------------------------------------------------
    # Identify column types
    # -----------------------------------------------------

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
        "\nFeatures:",
        X_data.shape[1]
    )

    print(
        "Numeric:",
        len(numeric_features)
    )

    print(
        "Categorical:",
        len(categorical_features)
    )

    # -----------------------------------------------------
    # Numeric preprocessing
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Categorical preprocessing
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Preprocessor
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Logistic regression
    # -----------------------------------------------------

    model = LogisticRegression(
        max_iter=1000,
        solver="lbfgs"
    )

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

    # -----------------------------------------------------
    # Train
    # -----------------------------------------------------

    print("\nTraining...")

    pipeline.fit(
        X_train,
        y_train
    )

    print(
        "Training complete."
    )

    # -----------------------------------------------------
    # Predictions
    # -----------------------------------------------------

    test_prob = pipeline.predict_proba(
        X_test
    )[:, 1]

    # -----------------------------------------------------
    # Metrics
    # -----------------------------------------------------

    roc = roc_auc_score(
        y_test,
        test_prob
    )

    pr_auc = average_precision_score(
        y_test,
        test_prob
    )

    brier = brier_score_loss(
        y_test,
        test_prob
    )

    loss = log_loss(
        y_test,
        test_prob
    )

    print("\nTEST")

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
        "model": name,
        "features": X_data.shape[1],
        "roc_auc": roc,
        "pr_auc": pr_auc,
        "brier": brier,
        "log_loss": loss
    }


# =========================================================
# 6. RUN ALL MODELS
# =========================================================

results = []

for name, dataset in datasets.items():

    result = train_and_evaluate(
        name,
        dataset
    )

    results.append(
        result
    )


# =========================================================
# 7. RESULTS TABLE
# =========================================================

results_df = pd.DataFrame(
    results
)

results_df["delta_auc_vs_thin"] = (
    results_df["roc_auc"]
    - results_df.loc[
        results_df["model"] == "Thin-file",
        "roc_auc"
    ].iloc[0]
)

results_df["delta_pr_auc_vs_thin"] = (
    results_df["pr_auc"]
    - results_df.loc[
        results_df["model"] == "Thin-file",
        "pr_auc"
    ].iloc[0]
)

print("\n")
print("=" * 70)
print("FEATURE ABLATION RESULTS")
print("=" * 70)

print(
    results_df.round(6).to_string(
        index=False
    )
)


# =========================================================
# 8. SAVE RESULTS
# =========================================================

results_df.to_csv(
    "kavach_feature_ablation_results.csv",
    index=False
)

print(
    "\nSaved:"
)

print(
    "  kavach_feature_ablation_results.csv"
)

print(
    "\n"
    + "=" * 70
)

print(
    "FEATURE ABLATION COMPLETE"
)

print(
    "=" * 70
)
