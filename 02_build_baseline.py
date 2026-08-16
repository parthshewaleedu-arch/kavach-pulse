import pandas as pd
import numpy as np

DATA_PATH = "application_train.csv"

print("=" * 70)
print("KAVACH PULSE — BASELINE FEATURE ENGINEERING")
print("=" * 70)

# ---------------------------------------------------------
# 1. LOAD
# ---------------------------------------------------------

df = pd.read_csv(DATA_PATH)

print(f"\nOriginal shape: {df.shape}")

# ---------------------------------------------------------
# 2. TARGET
# ---------------------------------------------------------

y = df["TARGET"].copy()

# ---------------------------------------------------------
# 3. SELECT DEFENSIBLE TRADITIONAL FEATURES
# ---------------------------------------------------------

numeric_features = [
    "AMT_INCOME_TOTAL",
    "AMT_CREDIT",
    "AMT_ANNUITY",
    "AMT_GOODS_PRICE",

    "DAYS_BIRTH",
    "DAYS_EMPLOYED",
    "DAYS_REGISTRATION",
    "DAYS_ID_PUBLISH",

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

categorical_features = [
    "NAME_CONTRACT_TYPE",
    "NAME_INCOME_TYPE",
    "NAME_EDUCATION_TYPE",
    "NAME_HOUSING_TYPE",
]

# Keep only columns that actually exist
numeric_features = [
    c for c in numeric_features
    if c in df.columns
]

categorical_features = [
    c for c in categorical_features
    if c in df.columns
]

# ---------------------------------------------------------
# 4. CREATE DERIVED FEATURES
# ---------------------------------------------------------

X = df[numeric_features + categorical_features].copy()

# Age in years
X["AGE_YEARS"] = (-df["DAYS_BIRTH"]) / 365.25

# Employment duration
# Home Credit uses 365243 as a special/anomalous value
X["EMPLOYMENT_INFO_MISSING"] = (
    df["DAYS_EMPLOYED"] == 365243
).astype(int)

X["EMPLOYMENT_YEARS"] = (
    df["DAYS_EMPLOYED"]
    .replace(365243, np.nan)
    .abs()
    / 365.25
)

# Financial ratios
X["CREDIT_TO_INCOME"] = (
    df["AMT_CREDIT"] /
    df["AMT_INCOME_TOTAL"].replace(0, np.nan)
)

X["ANNUITY_TO_INCOME"] = (
    df["AMT_ANNUITY"] /
    df["AMT_INCOME_TOTAL"].replace(0, np.nan)
)

X["GOODS_TO_INCOME"] = (
    df["AMT_GOODS_PRICE"] /
    df["AMT_INCOME_TOTAL"].replace(0, np.nan)
)

# ---------------------------------------------------------
# 5. SANITY CHECK
# ---------------------------------------------------------

print("\nSelected numeric features:")
for c in numeric_features:
    print("  ", c)

print("\nSelected categorical features:")
for c in categorical_features:
    print("  ", c)

print("\nDerived features:")
print("   AGE_YEARS")
print("   EMPLOYMENT_INFO_MISSING")
print("   EMPLOYMENT_YEARS")
print("   CREDIT_TO_INCOME")
print("   ANNUITY_TO_INCOME")
print("   GOODS_TO_INCOME")

print(f"\nFinal feature count: {X.shape[1]}")

# ---------------------------------------------------------
# 6. SAVE
# ---------------------------------------------------------

output = X.copy()
output["TARGET"] = y

output.to_csv(
    "kavach_traditional_baseline.csv",
    index=False
)

print("\nSaved:")
print("  kavach_traditional_baseline.csv")

print("\nFinal shape:", output.shape)

print("\n" + "=" * 70)
print("FEATURE ENGINEERING COMPLETE")
print("=" * 70)
