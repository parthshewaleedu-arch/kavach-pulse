import numpy as np
import pandas as pd

print("=" * 70)
print("KAVACH PULSE — REALISTIC THIN-FILE SIMULATION")
print("=" * 70)


# =========================================================
# CONFIGURATION
# =========================================================

SEED = 42

rng = np.random.default_rng(SEED)

N_APPLICANTS = 5000

MAX_HISTORY_MONTHS = 12


# =========================================================
# 1. APPLICANT POPULATION
# =========================================================

print("\n[1] Creating applicant population...")

applicants = pd.DataFrame({

    "applicant_id":
        np.arange(N_APPLICANTS),

    # How many months of usable history the applicant has.
    #
    # Intentionally heterogeneous.
    #
    "history_months":
        rng.choice(
            np.arange(1, 13),
            size=N_APPLICANTS,
            p=np.array([
            0.05,
            0.06,
            0.08,
            0.08,
            0.09,
            0.09,
            0.09,
            0.09,
            0.09,
            0.08,
            0.07,
            0.04
        ]) / np.array([
            0.05,
            0.06,
            0.08,
            0.08,
            0.09,
            0.09,
            0.09,
            0.09,
            0.09,
            0.08,
            0.07,
            0.04
        ]).sum()
    )
})


print(
    "\nHistory distribution:"
)

print(
    applicants[
        "history_months"
    ].value_counts().sort_index()
)

# =========================================================
# 2. APPLICANT LATENT CHARACTERISTICS
# =========================================================

print(
    "\n[2] Creating latent applicant characteristics..."
)

applicants[
    "base_income"
] = np.clip(
    rng.lognormal(
        mean=np.log(30000),
        sigma=0.45,
        size=N_APPLICANTS
    ),
    5000,
    250000
)


applicants[
    "base_stability"
] = np.clip(
    rng.normal(
        0.60,
        0.15,
        N_APPLICANTS
    ),
    0.10,
    0.95
)


applicants[
    "base_payment_strength"
] = np.clip(
    rng.beta(
        12,
        1.5,
        N_APPLICANTS
    ),
    0.50,
    1.00
)


# =========================================================
# 3. GENERATE MONTHLY RECORDS
# =========================================================

print(
    "\n[3] Generating heterogeneous monthly histories..."
)

records = []


for _, applicant in applicants.iterrows():

    applicant_id = int(
        applicant["applicant_id"]
    )

    history_months = int(
        applicant["history_months"]
    )

    base_income = float(
        applicant["base_income"]
    )

    stability = float(
        applicant["base_stability"]
    )

    payment_strength = float(
        applicant["base_payment_strength"]
    )


    # -----------------------------------------------------
    # Applicant-specific income volatility
    # -----------------------------------------------------

    income_cv = np.clip(
        0.08
        +
        (1 - stability) * 0.45
        +
        rng.normal(0, 0.03),
        0.03,
        0.80
    )


    # -----------------------------------------------------
    # Applicant-specific income trend
    # -----------------------------------------------------

    income_trend = np.clip(
        rng.normal(
            0,
            0.015
        )
        +
        (stability - 0.60) * 0.08,
        -0.15,
        0.15
    )


    # -----------------------------------------------------
    # Generate only the history available to applicant
    # -----------------------------------------------------

    previous_income = base_income

    for month in range(
        history_months
    ):

        # Month-level trend
        trend_multiplier = (
            1
            +
            income_trend
            *
            (
                month / max(
                    history_months - 1,
                    1
                )
            )
        )


        # Monthly noise
        noise_multiplier = np.exp(
            rng.normal(
                0,
                income_cv
            )
            * 0.35
        )


        income = np.clip(
            base_income
            *
            trend_multiplier
            *
            noise_multiplier,
            3000,
            500000
        )


        # -------------------------------------------------
        # Platform activity
        # -------------------------------------------------

        activity_probability = np.clip(
            0.55
            +
            stability * 0.35,
            0.40,
            0.95
        )

        active_days = rng.binomial(
            30,
            activity_probability
        )

        active_days = max(
            1,
            active_days
        )


        # -------------------------------------------------
        # Bank inflow
        # -------------------------------------------------

        inflow = (
            income
            *
            rng.uniform(
                0.90,
                1.15
            )
        )


        # -------------------------------------------------
        # Spending pressure
        # -------------------------------------------------

        spending_ratio = np.clip(
            0.55
            +
            (1 - stability) * 0.25
            +
            rng.normal(
                0,
                0.05
            ),
            0.30,
            0.95
        )


        outflow = (
            inflow
            *
            spending_ratio
        )


        # -------------------------------------------------
        # Payment behaviour
        # -------------------------------------------------

        missed_probability = np.clip(
            1
            -
            payment_strength
            +
            (1 - stability) * 0.08,
            0.005,
            0.50
        )


        payment_missed = int(
            rng.random()
            <
            missed_probability
        )


        # -------------------------------------------------
        # Cash-flow noise
        # -------------------------------------------------

        net_cashflow = (
            inflow
            -
            outflow
        )


        records.append({

            "applicant_id":
                applicant_id,

            "month_index":
                month + 1,

            "income":
                income,

            "bank_inflow":
                inflow,

            "bank_outflow":
                outflow,

            "net_cashflow":
                net_cashflow,

            "active_days":
                active_days,

            "payment_missed":
                payment_missed
        })


monthly = pd.DataFrame(
    records
)


print(
    "Monthly records:",
    monthly.shape
)


# =========================================================
# 4. INTRODUCE DATA GAPS
# =========================================================

print(
    "\n[4] Introducing realistic missing periods..."
)

monthly[
    "original_record"
] = True


# Missing probability is higher for thin-file applicants.

history_lookup = applicants.set_index(
    "applicant_id"
)[
    "history_months"
]


monthly[
    "history_months"
] = monthly[
    "applicant_id"
].map(
    history_lookup
)


missing_probability = np.where(

    monthly["history_months"] <= 3,

    0.10,

    np.where(

        monthly["history_months"] <= 6,

        0.07,

        0.04
    )
)


missing_mask = (
    rng.random(
        len(monthly)
    )
    <
    missing_probability
)


monthly.loc[
    missing_mask,
    [
        "income",
        "bank_inflow",
        "bank_outflow",
        "net_cashflow",
        "active_days",
        "payment_missed"
    ]
] = np.nan


# Ensure every applicant still has
# at least one usable observation.

valid_counts = monthly.groupby(
    "applicant_id"
)[
    "income"
].count()


zero_history = valid_counts[
    valid_counts == 0
].index


for applicant_id in zero_history:

    idx = monthly[
        monthly["applicant_id"]
        ==
        applicant_id
    ].index

    chosen = rng.choice(
        idx
    )

    monthly.loc[
        chosen,
        [
            "income",
            "bank_inflow",
            "bank_outflow",
            "net_cashflow",
            "active_days",
            "payment_missed"
        ]
    ] = (
        monthly.loc[
            chosen,
            [
                "income",
                "bank_inflow",
                "bank_outflow",
                "net_cashflow",
                "active_days",
                "payment_missed"
            ]
        ].fillna(0)
    )


# =========================================================
# 5. AGGREGATE BEHAVIORAL FEATURES
# =========================================================

print(
    "\n[5] Creating applicant-level features..."
)


def safe_cv(series):

    series = series.dropna()

    if len(series) < 2:
        return np.nan

    mean = series.mean()

    if abs(mean) < 1e-9:
        return 0.0

    return series.std() / abs(mean)


def calculate_trend(group):

    clean = group[
        ["month_index", "income"]
    ].dropna()

    if len(clean) < 2:

        return 0.0

    x = clean[
        "month_index"
    ].values

    y = clean[
        "income"
    ].values

    slope = np.polyfit(
        x,
        y,
        1
    )[0]

    mean_income = (
        np.mean(y)
    )

    if mean_income <= 0:
        return 0.0

    return np.clip(
        slope / mean_income,
        -1,
        1
    )


feature_rows = []


for applicant_id, group in monthly.groupby(
    "applicant_id"
):

    history_months = int(
        group[
            "history_months"
        ].iloc[0]
    )


    available_months = (
        group["income"]
        .notna()
        .sum()
    )


    missing_months = (
        history_months
        -
        available_months
    )


    # -----------------------------------------------------
    # Income
    # -----------------------------------------------------

    income_mean = (
        group["income"]
        .mean()
    )

    income_std = (
        group["income"]
        .std()
    )

    income_cv = safe_cv(
        group["income"]
    )


    income_min = (
        group["income"]
        .min()
    )

    income_max = (
        group["income"]
        .max()
    )


    income_trend = calculate_trend(
        group
    )


    # -----------------------------------------------------
    # Cash flow
    # -----------------------------------------------------

    inflow_mean = (
        group["bank_inflow"]
        .mean()
    )

    outflow_mean = (
        group["bank_outflow"]
        .mean()
    )

    net_cashflow_mean = (
        group["net_cashflow"]
        .mean()
    )

    net_cashflow_std = (
        group["net_cashflow"]
        .std()
    )

    cashflow_cv = safe_cv(
        group["net_cashflow"]
    )


    # -----------------------------------------------------
    # Balance approximation
    # -----------------------------------------------------

    cumulative_balance = (
        group["net_cashflow"]
        .fillna(0)
        .cumsum()
    )

    balance_min = (
        cumulative_balance.min()
    )

    balance_max = (
        cumulative_balance.max()
    )

    balance_mean = (
        cumulative_balance.mean()
    )


    # -----------------------------------------------------
    # Payments
    # -----------------------------------------------------

    payment_observations = (
        group[
            "payment_missed"
        ].dropna()
    )


    if len(
        payment_observations
    ) > 0:

        payment_success_rate = (
            1
            -
            payment_observations.mean()
        )

    else:

        payment_success_rate = np.nan


    missed_payment_rate = (
        1
        -
        payment_success_rate
    )


    # -----------------------------------------------------
    # Activity
    # -----------------------------------------------------

    active_days_mean = (
        group["active_days"]
        .mean()
    )


    # -----------------------------------------------------
    # Coverage
    # -----------------------------------------------------

    if (
        outflow_mean is not None
        and
        outflow_mean > 0
    ):

        inflow_to_outflow_ratio = (
            inflow_mean
            /
            outflow_mean
        )

    else:

        inflow_to_outflow_ratio = np.nan


    feature_rows.append({

        "applicant_id":
            applicant_id,

        "history_months":
            history_months,

        "available_months":
            available_months,

        "missing_months":
            missing_months,

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
            missed_payment_rate,

        "active_days_mean":
            active_days_mean,

        "inflow_to_outflow_ratio":
            inflow_to_outflow_ratio
    })


features = pd.DataFrame(
    feature_rows
)


# =========================================================
# 6. DATA QUALITY FEATURES
# =========================================================

print(
    "\n[6] Calculating evidence quality..."
)


features[
    "history_completeness"
] = (
    features[
        "available_months"
    ]
    /
    features[
        "history_months"
    ]
)


features[
    "history_completeness"
] = (
    features[
        "history_completeness"
    ].clip(
        0,
        1
    )
)


# More history gives more confidence.

history_score = np.clip(
    features[
        "history_months"
    ]
    /
    12,
    0,
    1
)


completeness_score = (
    features[
        "history_completeness"
    ]
)


# ---------------------------------------------------------
# Source coverage
# ---------------------------------------------------------

source_count = np.zeros(
    len(features)
)


source_count += (
    features[
        "income_mean"
    ].notna()
)

source_count += (
    features[
        "bank_inflow_mean"
    ].notna()
)

source_count += (
    features[
        "payment_success_rate"
    ].notna()
)


source_coverage = (
    source_count
    /
    3
)


# ---------------------------------------------------------
# Data recency
# ---------------------------------------------------------
#
# Since this is simulated historical data,
# we use the fraction of the requested history
# that is actually observable.
#
# ---------------------------------------------------------
recency_score = np.clip(
    0.50
    +
    0.50
    *
    features[
        "history_completeness"
    ],
    0,
    1
)
# ---------------------------------------------------------
# Source consistency
# ---------------------------------------------------------

source_consistency = np.clip(

    0.70
    +
    rng.normal(
        0,
        0.08,
        len(features)
    ),

    0.45,

    1.00
)


# ---------------------------------------------------------
# Evidence quality
# ---------------------------------------------------------

features[
    "evidence_quality_score"
] = (

    0.30
    *
    history_score

    +

    0.30
    *
    completeness_score

    +

    0.20
    *
    source_coverage

    +

    0.10
    *
    recency_score

    +

    0.10
    *
    source_consistency

) * 100


features[
    "evidence_quality_score"
] = (
    features[
        "evidence_quality_score"
    ].clip(
        0,
        100
    )
)


# =========================================================
# 7. CONFIDENCE BAND
# =========================================================

def confidence_band(score):

    if score >= 80:
        return "HIGH"

    elif score >= 60:
        return "MEDIUM"

    else:
        return "LOW"


features[
    "confidence_band"
] = (
    features[
        "evidence_quality_score"
    ].apply(
        confidence_band
    )
)


# =========================================================
# 8. BEHAVIORAL STABILITY SCORE
# =========================================================
#
# This remains a prototype score.
#
# It does NOT represent probability of default.
#
# =========================================================

def percentile(series):

    return series.rank(
        pct=True
    )


income_stability = (
    1
    -
    percentile(
        features[
            "income_cv"
        ].fillna(
            features[
                "income_cv"
            ].median()
        )
    )
)


cashflow_stability = (
    1
    -
    percentile(
        features[
            "cashflow_cv"
        ].fillna(
            features[
                "cashflow_cv"
            ].median()
        )
    )
)


payment_strength = (
    features[
        "payment_success_rate"
    ].fillna(
        features[
            "payment_success_rate"
        ].median()
    )
)


balance_strength = percentile(
    features[
        "balance_min"
    ].fillna(
        features[
            "balance_min"
        ].median()
    )
)


coverage_strength = percentile(
    features[
        "inflow_to_outflow_ratio"
    ].fillna(
        features[
            "inflow_to_outflow_ratio"
        ].median()
    )
)


trend_strength = percentile(
    features[
        "income_trend"
    ].fillna(0)
)


features[
    "behavioral_stability_score"
] = (

    0.25
    *
    income_stability

    +

    0.20
    *
    cashflow_stability

    +

    0.20
    *
    payment_strength

    +

    0.15
    *
    balance_strength

    +

    0.10
    *
    coverage_strength

    +

    0.10
    *
    trend_strength

) * 100


# =========================================================
# 9. DATA-QUALITY ADJUSTED CONFIDENCE
# =========================================================

# IMPORTANT:
#
# A high behavioral score does NOT automatically mean
# high confidence.
#
# Confidence is driven by evidence quality.

features[
    "confidence_weight"
] = (
    features[
        "evidence_quality_score"
    ]
    /
    100
)


# =========================================================
# 10. SANITY CHECKS
# =========================================================

print(
    "\n[7] Running sanity checks..."
)


print(
    "\nApplicant dataset:",
    features.shape
)


print(
    "\nMissing values:"
)

print(
    features.isna()
    .sum()
    .sort_values(
        ascending=False
    )
    .head(10)
)


print(
    "\nHistory distribution:"
)

print(
    features[
        "history_months"
    ].value_counts().sort_index()
)

print(
    "\nConfidence distribution:"
)

print(
    features[
        "confidence_band"
    ].value_counts()
)


print(
    "\nEvidence quality:"
)

print(
    features[
        "evidence_quality_score"
    ].describe()
)


print(
    "\nBehavioral stability:"
)

print(
    features[
        "behavioral_stability_score"
    ].describe()
)


# =========================================================
# 11. EXAMPLE APPLICANTS
# =========================================================

print(
    "\n" + "=" * 70
)

print(
    "EXAMPLE APPLICANTS BY HISTORY DEPTH"
)

print(
    "=" * 70
)


for history in [
    2,
    4,
    6,
    9,
    12
]:

    subset = features[
        features[
            "history_months"
        ]
        ==
        history
    ]

    if len(subset) == 0:
        continue

    row = subset.iloc[0]

    print(
        f"""
History: {history} months
Applicant: {int(row['applicant_id'])}
Available months: {int(row['available_months'])}
Missing months: {int(row['missing_months'])}
Evidence quality: {row['evidence_quality_score']:.1f}/100
Confidence: {row['confidence_band']}
Behavioral stability: {row['behavioral_stability_score']:.1f}
"""
    )


# =========================================================
# 12. SAVE
# =========================================================

monthly.to_csv(
    "kavach_thin_file_monthly_history.csv",
    index=False
)


features.to_csv(
    "kavach_thin_file_behavioral_features.csv",
    index=False
)


print(
    "\nSaved:"
)

print(
    "  kavach_thin_file_monthly_history.csv"
)

print(
    "  kavach_thin_file_behavioral_features.csv"
)


# =========================================================
# 13. METHODOLOGY WARNING
# =========================================================

print(
    "\n" + "=" * 70
)

print(
    "METHODOLOGY NOTE"
)

print(
    "=" * 70
)

print(
    """
This dataset is SYNTHETIC.

The purpose is to demonstrate how Kavach
behaves when applicants have different
amounts of available financial history.

The simulation intentionally creates:

1. Very thin files
2. Developing files
3. Established files
4. Missing periods
5. Different evidence quality
6. Different confidence levels

These records are NOT real applicant records.

Behavioral stability is a prototype score.

It is NOT a probability of default.

Production validation requires consented,
real-world behavioral histories linked to
observed repayment outcomes.
"""
)

print(
    "=" * 70
)

print(
    "REALISTIC THIN-FILE SIMULATION COMPLETE"
)

print(
    "=" * 70
)
