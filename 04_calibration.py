import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.calibration import calibration_curve
from sklearn.metrics import brier_score_loss

print("=" * 70)
print("KAVACH PULSE — PROBABILITY CALIBRATION")
print("=" * 70)

# ---------------------------------------------------------
# 1. LOAD SAVED TEST PREDICTIONS
# ---------------------------------------------------------

df = pd.read_csv(
    "kavach_logistic_test_predictions.csv"
)

y_true = df["ACTUAL_TARGET"]
y_prob = df["PREDICTED_PD"]

print("\nTest observations:", len(df))

# ---------------------------------------------------------
# 2. BRIER SCORE
# ---------------------------------------------------------

brier = brier_score_loss(
    y_true,
    y_prob
)

print(f"\nBrier Score: {brier:.6f}")

# ---------------------------------------------------------
# 3. CALIBRATION CURVE
# ---------------------------------------------------------

fraction_positive, mean_predicted = calibration_curve(
    y_true,
    y_prob,
    n_bins=10,
    strategy="quantile"
)

calibration_table = pd.DataFrame({
    "mean_predicted_pd": mean_predicted,
    "observed_default_rate": fraction_positive
})

calibration_table["calibration_gap"] = (
    calibration_table["observed_default_rate"]
    - calibration_table["mean_predicted_pd"]
)

print("\nCalibration table:")
print(
    calibration_table.round(4).to_string(
        index=False
    )
)

# ---------------------------------------------------------
# 4. SAVE TABLE
# ---------------------------------------------------------

calibration_table.to_csv(
    "kavach_calibration_table.csv",
    index=False
)

# ---------------------------------------------------------
# 5. PLOT
# ---------------------------------------------------------

plt.figure(figsize=(8, 6))

plt.plot(
    [0, 1],
    [0, 1],
    linestyle="--",
    label="Perfect calibration"
)

plt.plot(
    mean_predicted,
    fraction_positive,
    marker="o",
    label="Kavach Logistic Regression"
)

plt.xlabel("Mean predicted probability")
plt.ylabel("Observed default rate")
plt.title("Kavach Probability Calibration")

plt.legend()
plt.grid(True)

plt.tight_layout()

plt.savefig(
    "kavach_calibration_curve.png",
    dpi=200
)

plt.show()

print("\nSaved:")
print("  kavach_calibration_table.csv")
print("  kavach_calibration_curve.png")

print("\n" + "=" * 70)
print("CALIBRATION ANALYSIS COMPLETE")
print("=" * 70)
