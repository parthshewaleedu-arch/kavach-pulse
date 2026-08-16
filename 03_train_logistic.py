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
    log_loss,
    confusion_matrix
)

print("=" * 70)
print("KAVACH PULSE — BASELINE LOGISTIC REGRESSION")
print("=" * 70)

# ---------------------------------------------------------
# 1. LOAD
# ---------------------------------------------------------

df = pd.read_csv("kavach_traditional_baseline.csv")
# Load original applicant IDs only for prediction traceability.
# SK_ID_CURR is NOT used as a model feature.
original_ids = pd.read_csv(
    "application_train.csv",
    usecols=["SK_ID_CURR"]
)

if len(original_ids) != len(df):
    raise ValueError(
        f"Row count mismatch: baseline={len(df)}, "
        f"application={len(original_ids)}"
    )
print("\nDataset shape:", df.shape)

# ---------------------------------------------------------
# 2. REMOVE REDUNDANT RAW DATE-DERIVED FEATURES
# ---------------------------------------------------------

raw_features_to_remove = [
    "DAYS_BIRTH",
    "DAYS_EMPLOYED",
    "DAYS_REGISTRATION",
    "DAYS_ID_PUBLISH"
]

df = df.drop(
    columns=raw_features_to_remove,
    errors="ignore"
)

# ---------------------------------------------------------
# 3. SPLIT FEATURES / TARGET
# ---------------------------------------------------------

X = df.drop(columns=["TARGET"])
y = df["TARGET"]

print("Features:", X.shape[1])
print("Target rate:", round(y.mean() * 100, 2), "%")

# ---------------------------------------------------------
# 4. IDENTIFY COLUMN TYPES
# ---------------------------------------------------------

categorical_features = X.select_dtypes(
    include=["object", "category"]
).columns.tolist()

numeric_features = X.select_dtypes(
    include=np.number
).columns.tolist()

print("\nNumeric features:", len(numeric_features))
print("Categorical features:", len(categorical_features))

# ---------------------------------------------------------
# 5. TRAIN / VALIDATION / TEST SPLIT
# ---------------------------------------------------------

X_train, X_temp, y_train, y_temp = train_test_split(
    X,
    y,
    test_size=0.30,
    stratify=y,
    random_state=42
)

X_val, X_test, y_val, y_test = train_test_split(
    X_temp,
    y_temp,
    test_size=0.50,
    stratify=y_temp,
    random_state=42
)

print("\nSplit sizes:")
print("Train:", X_train.shape)
print("Validation:", X_val.shape)
print("Test:", X_test.shape)

# ---------------------------------------------------------
# 6. NUMERICAL PIPELINE
# ---------------------------------------------------------

numeric_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="median")
        ),
        (
            "scaler",
            StandardScaler()
        )
    ]
)

# ---------------------------------------------------------
# 7. CATEGORICAL PIPELINE
# ---------------------------------------------------------

categorical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="most_frequent")
        ),
        (
            "onehot",
            OneHotEncoder(
                handle_unknown="ignore"
            )
        )
    ]
)

# ---------------------------------------------------------
# 8. PREPROCESSOR
# ---------------------------------------------------------

preprocessor = ColumnTransformer(
    transformers=[
        (
            "num",
            numeric_pipeline,
            numeric_features
        ),
        (
            "cat",
            categorical_pipeline,
            categorical_features
        )
    ]
)

# ---------------------------------------------------------
# 9. MODEL
# ---------------------------------------------------------

model = LogisticRegression(
    max_iter=1000,
    class_weight=None,
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

# ---------------------------------------------------------
# 10. TRAIN
# ---------------------------------------------------------

print("\nTraining Logistic Regression...")

pipeline.fit(
    X_train,
    y_train
)

print("Training complete.")

# ---------------------------------------------------------
# 11. PREDICT PROBABILITIES
# ---------------------------------------------------------

train_prob = pipeline.predict_proba(X_train)[:, 1]
val_prob = pipeline.predict_proba(X_val)[:, 1]
test_prob = pipeline.predict_proba(X_test)[:, 1]

# ---------------------------------------------------------
# 12. EVALUATION FUNCTION
# ---------------------------------------------------------

def evaluate(name, y_true, probability):

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

    print(f"\n{name}")
    print("-" * 40)
    print(f"ROC-AUC : {roc:.4f}")
    print(f"PR-AUC  : {pr_auc:.4f}")
    print(f"Brier   : {brier:.4f}")
    print(f"LogLoss : {loss:.4f}")

    return roc, pr_auc, brier, loss


# ---------------------------------------------------------
# 13. EVALUATE
# ---------------------------------------------------------

train_metrics = evaluate(
    "TRAIN",
    y_train,
    train_prob
)

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

# ---------------------------------------------------------
# 14. SIMPLE 10% RISK THRESHOLD
# ---------------------------------------------------------

threshold = 0.10

test_prediction = (
    test_prob >= threshold
).astype(int)

cm = confusion_matrix(
    y_test,
    test_prediction
)

print("\nConfusion Matrix @ 10% PD threshold")
print("-" * 40)
print(cm)

# ---------------------------------------------------------
# 15. RISK DISTRIBUTION
# ---------------------------------------------------------

print("\nPredicted PD distribution:")
print(
    pd.Series(test_prob).describe(
        percentiles=[
            0.50,
            0.75,
            0.90,
            0.95,
            0.99
        ]
    )
)

print("\n" + "=" * 70)
print("BASELINE MODEL COMPLETE")
print("=" * 70)
import joblib

joblib.dump(
    pipeline,
    "kavach_logistic_baseline.joblib"
)

# Recover original applicant IDs using the preserved dataframe index.
test_ids = original_ids.iloc[
    X_test.index
]["SK_ID_CURR"].values

test_predictions = X_test.copy()

test_predictions["SK_ID_CURR"] = test_ids
test_predictions["ACTUAL_TARGET"] = y_test.values
test_predictions["PREDICTED_PD"] = test_prob

test_predictions.to_csv(
    "kavach_logistic_test_predictions.csv",
    index=False
)

print("\nSaved:")
print("  kavach_logistic_baseline.joblib")
print("  kavach_logistic_test_predictions.csv")
