import pandas as pd
import numpy as np

print("=" * 70)
print("KAVACH PULSE — SYNTHETIC ALTERNATIVE DATA GENERATOR v2")
print("=" * 70)

# =========================================================
# CONFIGURATION
# =========================================================

INPUT_FILE = "application_train.csv"
OUTPUT_FILE = "kavach_synthetic_alternative_data.csv"

RANDOM_SEED = 42

rng = np.random.default_rng(RANDOM_SEED)

# =========================================================
# 1. LOAD ORIGINAL DATA
# =========================================================

print("\n[1] Loading Home Credit dataset...")

df = pd.read_csv(INPUT_FILE)

print(f"Original dataset: {df.shape}")

# =========================================================
# 2. IMPORTANT METHODOLOGICAL RULE
# =========================================================
#
# TARGET IS NEVER USED TO GENERATE ALTERNATIVE FEATURES.
#
# TARGET is only copied at the very end so that we can
# evaluate the synthetic alternative-data model against
# the real historical outcome.
#
# =========================================================

target = df["TARGET"].copy()

# =========================================================
# 3. BASIC PRE-APPLICATION VARIABLES
# =========================================================

print("\n[2] Preparing pre-application variables...")

# Income
income = (
    df["AMT_INCOME_TOTAL"]
    .fillna(df["AMT_INCOME_TOTAL"].median())
    .clip(lower=1)
)

# Age
age_years = (
    -df["DAYS_BIRTH"] / 365.25
)

age_years = (
    age_years
    .replace([np.inf, -np.inf], np.nan)
    .fillna(age_years.median())
    .clip(18, 90)
)

# Employment duration
employment_days = (
    df["DAYS_EMPLOYED"]
    .replace(365243, np.nan)
)

employment_years = (
    employment_days.abs() / 365.25
)

employment_years = (
    employment_years
    .replace([np.inf, -np.inf], np.nan)
    .fillna(employment_years.median())
    .clip(0, 50)
)

# Loan annuity
annuity = (
    df["AMT_ANNUITY"]
    .fillna(df["AMT_ANNUITY"].median())
    .clip(lower=0)
)

# =========================================================
# 4. LOG-INCOME NORMALIZATION
# =========================================================

print("\n[3] Creating normalized applicant characteristics...")

log_income = np.log1p(income)

income_z = (
    log_income - log_income.mean()
) / log_income.std()

age_z = (
    age_years - age_years.mean()
) / age_years.std()

employment_z = (
    employment_years - employment_years.mean()
) / employment_years.std()

# =========================================================
# 5. AFFORDABILITY SIGNAL
# =========================================================

# This is used only as an input to the synthetic generator.
# It is NOT itself included as an alternative-data feature.

annuity_to_income = (
    annuity /
    income
)

annuity_to_income = (
    annuity_to_income
    .replace([np.inf, -np.inf], np.nan)
    .fillna(annuity_to_income.median())
    .clip(0, 2)
)

burden_z = (
    annuity_to_income -
    annuity_to_income.mean()
) / annuity_to_income.std()

# =========================================================
# 6. LATENT STABILITY PROXY
# =========================================================
#
# This is an artificial latent variable representing
# underlying financial stability.
#
# IMPORTANT:
# TARGET IS NOT USED.
#
# It is generated from pre-outcome characteristics only.
#
# =========================================================

print("\n[4] Creating latent stability proxy...")

stability = (
    0.40 * income_z
    + 0.20 * age_z
    + 0.25 * employment_z
    - 0.35 * burden_z
)

stability = (
    stability - stability.mean()
) / stability.std()

# Add some independent noise so the synthetic signals
# are not perfectly determined by the latent variable.

stability_noisy = (
    0.85 * stability
    + 0.15 * rng.normal(
        0,
        1,
        len(df)
    )
)

stability_noisy = (
    stability_noisy -
    stability_noisy.mean()
) / stability_noisy.std()

# =========================================================
# 7. PLATFORM TENURE
# =========================================================

print("\n[5] Generating platform behavior...")

platform_tenure_months = (
    12
    + 5.0 * stability_noisy
    + rng.normal(
        0,
        6,
        len(df)
    )
)

platform_tenure_months = np.clip(
    platform_tenure_months,
    1,
    60
)

# =========================================================
# 8. ACTIVE MONTHS
# =========================================================

active_months_12m = (
    7
    + 2.5 * stability_noisy
    + rng.normal(
        0,
        2.2,
        len(df)
    )
)

active_months_12m = np.clip(
    np.round(active_months_12m),
    1,
    12
)

# =========================================================
# 9. ACTIVE DAYS
# =========================================================

active_days_avg = (
    18
    + 3.5 * stability_noisy
    + rng.normal(
        0,
        4,
        len(df)
    )
)

active_days_avg = np.clip(
    np.round(active_days_avg),
    1,
    31
)

# =========================================================
# 10. PLATFORM INCOME
# =========================================================
#
# IMPORTANT:
# We use Home Credit income only as an anchor.
#
# We do NOT directly copy it.
#
# We introduce noise and cap extreme values to avoid
# unrealistic synthetic gig-worker incomes.
#
# =========================================================

print("\n[6] Generating synthetic platform income...")

platform_income_avg = (
    income
    * rng.lognormal(
        mean=-0.05,
        sigma=0.20,
        size=len(df)
    )
)

platform_income_avg = (
    platform_income_avg
    * (
        1
        + 0.05 * stability_noisy
    )
)

# Conservative simulation bounds
platform_income_avg = np.clip(
    platform_income_avg,
    5000,
    500000
)

# =========================================================
# 11. PLATFORM INCOME VOLATILITY
# =========================================================

platform_income_volatility = (
    0.28
    - 0.045 * stability_noisy
    + rng.normal(
        0,
        0.05,
        len(df)
    )
)

platform_income_volatility = np.clip(
    platform_income_volatility,
    0.03,
    0.80
)

# =========================================================
# 12. INCOME TREND
# =========================================================

income_trend = (
    0.01 * stability_noisy
    + rng.normal(
        0,
        0.08,
        len(df)
    )
)

income_trend = np.clip(
    income_trend,
    -0.40,
    0.40
)

# =========================================================
# 13. BANK INFLOW
# =========================================================

print("\n[7] Generating synthetic bank cash-flow data...")

bank_inflow_avg = (
    platform_income_avg
    * rng.lognormal(
        mean=0.02,
        sigma=0.10,
        size=len(df)
    )
)

bank_inflow_avg = np.clip(
    bank_inflow_avg,
    5000,
    600000
)

# =========================================================
# 14. BANK OUTFLOW
# =========================================================
#
# Outflows are related to inflows but contain substantial
# independent noise.
#
# =========================================================

bank_outflow_ratio = (
    0.72
    + 0.08 * burden_z
    + rng.normal(
        0,
        0.08,
        len(df)
    )
)

bank_outflow_ratio = np.clip(
    bank_outflow_ratio,
    0.30,
    1.10
)

bank_outflow_avg = (
    bank_inflow_avg *
    bank_outflow_ratio
)

bank_outflow_avg = np.clip(
    bank_outflow_avg,
    500,
    600000
)

# =========================================================
# 15. CASH-FLOW VOLATILITY
# =========================================================

cashflow_volatility = (
    0.22
    - 0.035 * stability_noisy
    + rng.normal(
        0,
        0.05,
        len(df)
    )
)

cashflow_volatility = np.clip(
    cashflow_volatility,
    0.03,
    0.70
)

# =========================================================
# 16. CASH BUFFER
# =========================================================
#
# Approximate monthly surplus plus a noisy reserve component.
#
# =========================================================

cash_buffer = (
    bank_inflow_avg -
    bank_outflow_avg
)

cash_buffer += (
    platform_income_avg
    * (
        0.05
        + 0.025 * stability_noisy
    )
)

cash_buffer += rng.normal(
    0,
    platform_income_avg * 0.05,
    len(df)
)

cash_buffer = np.clip(
    cash_buffer,
    0,
    1000000
)

# =========================================================
# 17. PAYMENT CONSISTENCY
# =========================================================

print("\n[8] Generating payment behavior...")

payment_consistency = (
    0.88
    + 0.035 * stability_noisy
    + rng.normal(
        0,
        0.035,
        len(df)
    )
)

payment_consistency = np.clip(
    payment_consistency,
    0.50,
    0.999
)

# =========================================================
# 18. MISSED PAYMENT RATE
# =========================================================

missed_payment_rate = (
    1 -
    payment_consistency
)

missed_payment_rate = np.clip(
    missed_payment_rate,
    0,
    0.50
)

# =========================================================
# 19. CREATE OUTPUT DATAFRAME
# =========================================================

print("\n[9] Creating final synthetic alternative-data table...")

alternative = pd.DataFrame({

    # Platform behavior
    "platform_tenure_months":
        platform_tenure_months,

    "active_months_12m":
        active_months_12m,

    "active_days_avg":
        active_days_avg,

    # Platform earnings
    "platform_income_avg":
        platform_income_avg,

    "platform_income_volatility":
        platform_income_volatility,

    "income_trend":
        income_trend,

    # Bank cash flow
    "bank_inflow_avg":
        bank_inflow_avg,

    "bank_outflow_avg":
        bank_outflow_avg,

    "cashflow_volatility":
        cashflow_volatility,

    "cash_buffer":
        cash_buffer,

    # Payment behavior
    "payment_consistency":
        payment_consistency,

})

# =========================================================
# 20. ADD TARGET ONLY FOR EVALUATION
# =========================================================

alternative["TARGET"] = target.values

# =========================================================
# 21. SANITY CHECKS
# =========================================================

print("\n[10] Running sanity checks...")

# ---------------------------------------------------------
# Check 1 — Shape
# ---------------------------------------------------------

print(
    "\nDataset shape:",
    alternative.shape
)

# ---------------------------------------------------------
# Check 2 — Missing values
# ---------------------------------------------------------

missing_count = (
    alternative.isna()
    .sum()
    .sum()
)

print(
    "Total missing values:",
    missing_count
)

# ---------------------------------------------------------
# Check 3 — Infinite values
# ---------------------------------------------------------

numeric_data = alternative.select_dtypes(
    include=np.number
)

infinite_count = (
    np.isinf(
        numeric_data.to_numpy()
    ).sum()
)

print(
    "Infinite values:",
    infinite_count
)

# ---------------------------------------------------------
# Check 4 — Range checks
# ---------------------------------------------------------

print("\nRange checks:")

checks = {

    "platform_tenure_months":
        (
            alternative["platform_tenure_months"].min(),
            alternative["platform_tenure_months"].max()
        ),

    "active_months_12m":
        (
            alternative["active_months_12m"].min(),
            alternative["active_months_12m"].max()
        ),

    "active_days_avg":
        (
            alternative["active_days_avg"].min(),
            alternative["active_days_avg"].max()
        ),

    "platform_income_avg":
        (
            alternative["platform_income_avg"].min(),
            alternative["platform_income_avg"].max()
        ),

    "platform_income_volatility":
        (
            alternative["platform_income_volatility"].min(),
            alternative["platform_income_volatility"].max()
        ),

    "income_trend":
        (
            alternative["income_trend"].min(),
            alternative["income_trend"].max()
        ),

    "bank_inflow_avg":
        (
            alternative["bank_inflow_avg"].min(),
            alternative["bank_inflow_avg"].max()
        ),

    "bank_outflow_avg":
        (
            alternative["bank_outflow_avg"].min(),
            alternative["bank_outflow_avg"].max()
        ),

    "cashflow_volatility":
        (
            alternative["cashflow_volatility"].min(),
            alternative["cashflow_volatility"].max()
        ),

    "cash_buffer":
        (
            alternative["cash_buffer"].min(),
            alternative["cash_buffer"].max()
        ),

    "payment_consistency":
        (
            alternative["payment_consistency"].min(),
            alternative["payment_consistency"].max()
        ),


}

for feature, (minimum, maximum) in checks.items():

    print(
        f"{feature:32s}"
        f"min={minimum:12.4f} "
        f"max={maximum:12.4f}"
    )

# =========================================================
# 22. SUMMARY STATISTICS
# =========================================================

print("\n[11] Summary statistics:")

print(
    alternative.describe()
    .T
    .round(3)
)

# =========================================================
# 23. CORRELATION WITH TARGET
# =========================================================
#
# IMPORTANT:
# This is only exploratory.
#
# We are NOT using this to generate the features.
#
# =========================================================

print("\n[12] Exploratory correlations with TARGET:")

correlations = (
    alternative.corr(numeric_only=True)["TARGET"]
    .drop("TARGET")
    .sort_values()
)

print(
    correlations.round(4).to_string()
)

# =========================================================
# 24. CORRELATION BETWEEN ALTERNATIVE FEATURES
# =========================================================

print("\n[13] Alternative-feature correlations:")

feature_columns = [
    c for c in alternative.columns
    if c != "TARGET"
]

feature_corr = (
    alternative[feature_columns]
    .corr()
)

print(
    feature_corr.round(2)
    .to_string()
)

# =========================================================
# 25. SAVE
# =========================================================

print("\n[14] Saving dataset...")

alternative.to_csv(
    OUTPUT_FILE,
    index=False
)

print(
    f"Saved:\n  {OUTPUT_FILE}"
)

# =========================================================
# 26. FINAL STATUS
# =========================================================

print("\n" + "=" * 70)

if (
    missing_count == 0
    and infinite_count == 0
):

    print(
        "SANITY CHECK: PASSED"
    )

else:

    print(
        "SANITY CHECK: FAILED"
    )

print("=" * 70)

print(
    "\nIMPORTANT METHODOLOGY NOTE:"
)

print(
    "The alternative features are SYNTHETIC."
)

print(
    "TARGET was NOT used to generate them."
)

print(
    "They are for controlled experimentation only."
)

print(
    "They must NOT be presented as real gig-worker data."
)

print("=" * 70)
print("SYNTHETIC DATA GENERATION COMPLETE")
print("=" * 70)
