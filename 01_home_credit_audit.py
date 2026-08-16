import pandas as pd
import numpy as np

DATA_PATH = "application_train.csv"

print("=" * 70)
print("KAVACH PULSE — HOME CREDIT DATA AUDIT")
print("=" * 70)

# ---------------------------------------------------------
# 1. LOAD DATA
# ---------------------------------------------------------

print("\n[1] Loading dataset...")

df = pd.read_csv(DATA_PATH)

print(f"Rows    : {df.shape[0]:,}")
print(f"Columns : {df.shape[1]:,}")

# ---------------------------------------------------------
# 2. TARGET
# ---------------------------------------------------------

print("\n[2] TARGET DISTRIBUTION")
print("-" * 40)

target_counts = df["TARGET"].value_counts()
target_pct = df["TARGET"].value_counts(normalize=True) * 100

print(target_counts)
print("\nPercentage:")
print(target_pct.round(2))

# ---------------------------------------------------------
# 3. DATA TYPES
# ---------------------------------------------------------

print("\n[3] DATA TYPES")
print("-" * 40)

numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
categorical_cols = df.select_dtypes(
    include=["object", "category"]
).columns.tolist()

print(f"Numeric columns    : {len(numeric_cols)}")
print(f"Categorical columns: {len(categorical_cols)}")

# ---------------------------------------------------------
# 4. MISSING VALUES
# ---------------------------------------------------------

print("\n[4] MISSING VALUES")
print("-" * 40)

missing = df.isnull().sum()
missing_pct = (missing / len(df)) * 100

missing_table = pd.DataFrame({
    "missing_count": missing,
    "missing_percent": missing_pct
})

missing_table = missing_table[
    missing_table["missing_count"] > 0
].sort_values(
    "missing_percent",
    ascending=False
)

print(f"Columns with missing values: {len(missing_table)}")
print("\nTop 30:")
print(missing_table.head(30).round(2))

# ---------------------------------------------------------
# 5. UNIQUE VALUES
# ---------------------------------------------------------

print("\n[5] LOW-CARDINALITY COLUMNS")
print("-" * 40)

low_cardinality = []

for col in df.columns:
    unique = df[col].nunique(dropna=True)

    if unique <= 10:
        low_cardinality.append(
            (col, unique)
        )

low_cardinality_df = pd.DataFrame(
    low_cardinality,
    columns=["column", "unique_values"]
)

print(low_cardinality_df.to_string(index=False))

# ---------------------------------------------------------
# 6. CONSTANT COLUMNS
# ---------------------------------------------------------

print("\n[6] CONSTANT COLUMNS")
print("-" * 40)

constant_cols = [
    col for col in df.columns
    if df[col].nunique(dropna=False) <= 1
]

if constant_cols:
    print(constant_cols)
else:
    print("No constant columns found.")

# ---------------------------------------------------------
# 7. DUPLICATES
# ---------------------------------------------------------

print("\n[7] DUPLICATES")
print("-" * 40)

duplicates = df.duplicated().sum()

print(f"Duplicate rows: {duplicates:,}")

# ---------------------------------------------------------
# 8. TARGET RATE BY SELECTED CATEGORICAL VARIABLES
# ---------------------------------------------------------

print("\n[8] TARGET RATE — SELECTED CATEGORICAL VARIABLES")
print("-" * 40)

selected_categorical = [
    "NAME_CONTRACT_TYPE",
    "NAME_INCOME_TYPE",
    "NAME_EDUCATION_TYPE",
    "NAME_FAMILY_STATUS",
    "NAME_HOUSING_TYPE",
    "OCCUPATION_TYPE"
]

for col in selected_categorical:

    if col not in df.columns:
        continue

    print(f"\n--- {col} ---")

    result = (
        df.groupby(col)["TARGET"]
        .agg(["count", "mean"])
        .sort_values("mean", ascending=False)
    )

    result["default_rate_percent"] = result["mean"] * 100

    print(
        result[
            ["count", "default_rate_percent"]
        ].round(2).to_string()
    )

# ---------------------------------------------------------
# 9. IMPORTANT NUMERICAL VARIABLES
# ---------------------------------------------------------

print("\n[9] NUMERICAL FEATURE SUMMARY")
print("-" * 40)

important_numeric = [
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
    "EXT_SOURCE_3"
]

available_numeric = [
    col for col in important_numeric
    if col in df.columns
]

print(
    df[available_numeric]
    .describe()
    .T
    .round(2)
)

# ---------------------------------------------------------
# 10. SPECIAL ANOMALY CHECK
# ---------------------------------------------------------

print("\n[10] DAYS_EMPLOYED ANOMALY CHECK")
print("-" * 40)

if "DAYS_EMPLOYED" in df.columns:

    print(
        df["DAYS_EMPLOYED"]
        .value_counts()
        .head(10)
    )

    print(
        "\nMaximum DAYS_EMPLOYED:",
        df["DAYS_EMPLOYED"].max()
    )

# ---------------------------------------------------------
# 11. SAVE AUDIT REPORT
# ---------------------------------------------------------

print("\n[11] SAVING AUDIT REPORT")
print("-" * 40)

missing_table.to_csv(
    "home_credit_missing_values.csv"
)

low_cardinality_df.to_csv(
    "home_credit_low_cardinality.csv",
    index=False
)

print("Saved:")
print("  home_credit_missing_values.csv")
print("  home_credit_low_cardinality.csv")

print("\n" + "=" * 70)
print("AUDIT COMPLETE")
print("=" * 70)
