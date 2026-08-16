import pandas as pd
import numpy as np

print("=" * 70)
print("KAVACH PULSE — BEHAVIORAL FEATURE ENGINE")
print("=" * 70)

# =========================================================
# CONFIGURATION
# =========================================================

RANDOM_SEED = 42
N_APPLICANTS = 5000
MONTHS = 12

rng = np.random.default_rng(RANDOM_SEED)


# =========================================================
# 1. GENERATE SYNTHETIC CONSENTED MONTHLY DATA
# =========================================================
#
# This represents the type of longitudinal data Kavach
# could receive after valid applicant authorization.
#
# It is SYNTHETIC.
#
# We are NOT training a credit model here.
#
# =========================================================

print("\n[1] Generating synthetic monthly financial history...")

rows = []

for applicant_id in range(N_APPLICANTS):

    # -----------------------------------------------------
    # Latent behavioral characteristics
    # -----------------------------------------------------
    #
    # These are simulation variables only.
    #
    # -----------------------------------------------------

    base_income = rng.lognormal(
        mean=np.log(30000),
        sigma=0.45
    )

    income_stability = rng.uniform(
        0.05,
        0.35
    )

    spending_ratio = rng.uniform(
        0.55,
        0.90
    )

    starting_balance = rng.uniform(
        3000,
        30000
    )

    platform_tenure = rng.integers(
        3,
        61
    )

    for month in range(1, MONTHS + 1):

        # -------------------------------------------------
        # Income
        # -------------------------------------------------

        income_noise = rng.normal(
            0,
            income_stability
        )

        income = (
            base_income
            * (1 + income_noise)
        )

        income = max(
            income,
            3000
        )

        # -------------------------------------------------
        # Bank inflow
        # -------------------------------------------------

        bank_inflow = (
            income
            * rng.normal(
                1.02,
                0.05
            )
        )

        bank_inflow = max(
            bank_inflow,
            1000
        )

        # -------------------------------------------------
        # Spending
        # -------------------------------------------------

        outflow_ratio = (
            spending_ratio
            + rng.normal(
                0,
                0.05
            )
        )

        outflow_ratio = np.clip(
            outflow_ratio,
            0.30,
            1.10
        )

        bank_outflow = (
            income
            * outflow_ratio
        )

        # -------------------------------------------------
        # Balance movement
        # -------------------------------------------------

        balance_change = (
            bank_inflow
            - bank_outflow
        )

        ending_balance = (
            starting_balance
            + balance_change
        )

        ending_balance = max(
            ending_balance,
            0
        )

        # -------------------------------------------------
        # Payment behavior
        # -------------------------------------------------

        payment_probability = (
            0.92
            + rng.normal(
                0,
                0.04
            )
        )

        payment_probability = np.clip(
            payment_probability,
            0.60,
            0.999
        )

        payment_on_time = (
            rng.random()
            < payment_probability
        )

        # -------------------------------------------------
        # Active days
        # -------------------------------------------------

        active_days = (
            18
            + rng.normal(
                0,
                4
            )
        )

        active_days = np.clip(
            active_days,
            1,
            31
        )

        # -------------------------------------------------
        # Save row
        # -------------------------------------------------

        rows.append({

            "applicant_id":
                applicant_id,

            "month":
                month,

            "platform_tenure_months":
                platform_tenure,

            "platform_income":
                income,

            "bank_inflow":
                bank_inflow,

            "bank_outflow":
                bank_outflow,

            "ending_balance":
                ending_balance,

            "active_days":
                active_days,

            "payment_on_time":
                int(payment_on_time)
        })

        starting_balance = ending_balance


monthly = pd.DataFrame(
    rows
)

print(
    "Monthly dataset:",
    monthly.shape
)


# =========================================================
# 2. FEATURE ENGINEERING
# =========================================================

print("\n[2] Deriving behavioral features...")


def safe_cv(series):

    mean = series.mean()

    if mean == 0:
        return 0

    return series.std() / mean


def calculate_trend(series):

    values = series.to_numpy()

    if len(values) < 2:
        return 0

    x = np.arange(
        len(values)
    )

    slope = np.polyfit(
        x,
        values,
        1
    )[0]

    mean = np.mean(
        values
    )

    if mean == 0:
        return 0

    return slope / mean


features = []


for applicant_id, group in monthly.groupby(
    "applicant_id"
):

    group = group.sort_values(
        "month"
    )

    # -----------------------------------------------------
    # Income features
    # -----------------------------------------------------

    income_mean = (
        group["platform_income"]
        .mean()
    )

    income_std = (
        group["platform_income"]
        .std()
    )

    income_cv = safe_cv(
        group["platform_income"]
    )

    income_min = (
        group["platform_income"]
        .min()
    )

    income_max = (
        group["platform_income"]
        .max()
    )

    income_trend = calculate_trend(
        group["platform_income"]
    )

    # -----------------------------------------------------
    # Cash-flow features
    # -----------------------------------------------------

    inflow_mean = (
        group["bank_inflow"]
        .mean()
    )

    outflow_mean = (
        group["bank_outflow"]
        .mean()
    )

    net_cashflow = (
        group["bank_inflow"]
        -
        group["bank_outflow"]
    )

    net_cashflow_mean = (
        net_cashflow.mean()
    )

    net_cashflow_std = (
        net_cashflow.std()
    )

    cashflow_cv = safe_cv(
        net_cashflow.abs()
    )

    # -----------------------------------------------------
    # Balance features
    # -----------------------------------------------------

    balance_mean = (
        group["ending_balance"]
        .mean()
    )

    balance_min = (
        group["ending_balance"]
        .min()
    )

    balance_max = (
        group["ending_balance"]
        .max()
    )

    # -----------------------------------------------------
    # Payment behavior
    # -----------------------------------------------------

    payment_success_rate = (
        group["payment_on_time"]
        .mean()
    )

    missed_payments = (
        1 -
        payment_success_rate
    )

    # -----------------------------------------------------
    # Activity behavior
    # -----------------------------------------------------

    active_days_mean = (
        group["active_days"]
        .mean()
    )

    # -----------------------------------------------------
    # History
    # -----------------------------------------------------

    history_months = (
        group["month"]
        .nunique()
    )

    platform_tenure = (
        group[
            "platform_tenure_months"
        ]
        .iloc[0]
    )

    # -----------------------------------------------------
    # Cash-flow coverage
    # -----------------------------------------------------

    if outflow_mean > 0:

        inflow_to_outflow_ratio = (
            inflow_mean /
            outflow_mean
        )

    else:

        inflow_to_outflow_ratio = np.nan

    # -----------------------------------------------------
    # Save applicant-level features
    # -----------------------------------------------------

    features.append({

        "applicant_id":
            applicant_id,

        "history_months":
            history_months,

        "platform_tenure_months":
            platform_tenure,

        "income_mean":
            income_mean,

        "income_std":
            income_std,

        "income_cv":
            income_cv,

        "income_min":
            income_min,

        "income_max":
            income_max,

        "income_trend":
            income_trend,

        "bank_inflow_mean":
            inflow_mean,

        "bank_outflow_mean":
            outflow_mean,

        "net_cashflow_mean":
            net_cashflow_mean,

        "net_cashflow_std":
            net_cashflow_std,

        "cashflow_cv":
            cashflow_cv,

        "balance_mean":
            balance_mean,

        "balance_min":
            balance_min,

        "balance_max":
            balance_max,

        "payment_success_rate":
            payment_success_rate,

        "missed_payment_rate":
            missed_payments,

        "active_days_mean":
            active_days_mean,

        "inflow_to_outflow_ratio":
            inflow_to_outflow_ratio
    })


behavioral = pd.DataFrame(
    features
)


# =========================================================
# 3. SANITY CHECKS
# =========================================================

print(
    "\n[3] Running sanity checks..."
)

print(
    "Applicant-level dataset:",
    behavioral.shape
)

print(
    "Missing values:",
    behavioral.isna()
    .sum()
    .sum()
)

print(
    "Infinite values:",
    np.isinf(
        behavioral
        .select_dtypes(
            include=np.number
        )
        .to_numpy()
    ).sum()
)


# =========================================================
# 4. SUMMARY
# =========================================================

print(
    "\n[4] Behavioral feature summary:"
)

print(
    behavioral
    .describe()
    .T
    .round(3)
    .to_string()
)


# =========================================================
# 5. EXAMPLE APPLICANTS
# =========================================================

print(
    "\n[5] Example applicants:"
)

display_columns = [

    "applicant_id",

    "history_months",

    "income_mean",

    "income_cv",

    "income_trend",

    "net_cashflow_mean",

    "balance_min",

    "payment_success_rate",

    "active_days_mean",

    "inflow_to_outflow_ratio"
]

print(
    behavioral[
        display_columns
    ]
    .head(10)
    .round(3)
    .to_string(
        index=False
    )
)


# =========================================================
# 6. SAVE
# =========================================================

monthly.to_csv(
    "kavach_synthetic_monthly_history.csv",
    index=False
)

behavioral.to_csv(
    "kavach_behavioral_features.csv",
    index=False
)

print(
    "\nSaved:"
)

print(
    "  kavach_synthetic_monthly_history.csv"
)

print(
    "  kavach_behavioral_features.csv"
)


# =========================================================
# 7. FINAL MESSAGE
# =========================================================

print("\nIMPORTANT:")
print(
    "These records and features are SYNTHETIC."
)

print(
    "They demonstrate the Kavach feature-engineering"
)

print(
    "pipeline and must NOT be presented as real applicant data."
)

print("=" * 70)
print("BEHAVIORAL FEATURE ENGINE COMPLETE")
print("=" * 70)
