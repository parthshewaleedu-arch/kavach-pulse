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
print("KAVACH PULSE — THIN-FILE BASELINE")
print("=" * 70)

# ---------------------------------------------------------
# 1. LOAD
# ---------------------------------------------------------

df = pd.read_csv("kavach_traditional_baseline.csv")

print("\nOriginal dataset:", df.shape)

# ---------------------------------------------------------
# 2. REMOVE FEATURES THAT REPRESENT STRONGER
#    EXTERNAL / CREDIT-HISTORY EVIDENCE
# ---------------------------------------------------------

thin_file_remove = [
    "EXT_SOURCE_1",
    "EXT_SOURCE_2",
    "EXT_SOURCE_3",

    "AMT_REQ_CREDIT_BUREAU_HOUR",
    "AMT_REQ_CREDIT_BUREAU_DAY",
    "AMT_REQ_CREDIT_BUREAU_WEEK",
    "AMT_REQ_CREDIT_BUREAU_MON",
    "AMT_REQ_CREDIT_BUREAU_QRT",
    "AMT_REQ_CREDIT_BUREAU_YEAR",
]

df = df.drop(
    columns=thin_file_remove,
    errors="ignore"
)

# ---------------------------------------------------------
# 3. REMOVE REDUNDANT RAW DATE FEATURES
# ---------------------------------------------------------

raw_remove = [
    "DAYS_BIRTH",
    "DAYS_EMPLOYED",
    "DAYS_REGISTRATION",
    "DAYS_ID_PUBLISH",
]

df = df.drop(
    columns=raw_remove,
    errors="ignore"
)

# ---------------------------------------------------------
# 4. FEATURES / TARGET
# ---------------------------------------------------------

X = df.drop(columns=["TARGET"])
y = df["TARGET"]

print("Thin-file features:", X.shape[1])
print("Target rate:", round(y.mean() * 100, 2), "%")

# ---------------------------------------------------------
# 5. COLUMN TYPES
# ---------------------------------------------------------

categorical_features = X.select_dtypes(
    include=["object"]
).columns.tolist()

numeric_features = X.select_dtypes(
    include=np.number
).columns.tolist()

print("\nNumeric features:", len(numeric_features))
print("Categorical features:", len(categorical_features))

# ---------------------------------------------------------
# 6. TRAIN / VALIDATION / TEST
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
# 7. PREPROCESSING
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
# 8. MODEL
# ---------------------------------------------------------

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

# ---------------------------------------------------------
# 9. TRAIN
# ---------------------------------------------------------

print("\nTraining thin-file Logistic Regression...")

pipeline.fit(
    X_train,
    y_train
)

print("Training complete.")

# ---------------------------------------------------------
# 10. PREDICTIONS
# ---------------------------------------------------------

val_prob = pipeline.predict_proba(
    X_val
)[:, 1]

test_prob = pipeline.predict_proba(
    X_test
)[:, 1]

# ---------------------------------------------------------
# 11. EVALUATION
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
# 12. SAVE MODEL
# ---------------------------------------------------------

import joblib

joblib.dump(
    pipeline,
    "kavach_thin_file_model.joblib"
)

# ---------------------------------------------------------
# 13. SAVE TEST PREDICTIONS
# ---------------------------------------------------------

predictions = X_test.copy()

predictions["ACTUAL_TARGET"] = y_test.values
predictions["PREDICTED_PD"] = test_prob

predictions.to_csv(
    "kavach_thin_file_predictions.csv",
    index=False
)

print("\nSaved:")
print("  kavach_thin_file_model.joblib")
print("  kavach_thin_file_predictions.csv")

print("\n" + "=" * 70)
print("THIN-FILE BASELINE COMPLETE")
print("=" * 70)
