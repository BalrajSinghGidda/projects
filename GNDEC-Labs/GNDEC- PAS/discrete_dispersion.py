
import numpy as np

# Discrete Series: Data points (x) and their corresponding frequencies (f)
x = np.array([2, 3, 4, 5, 6])
f = np.array([2, 4, 5, 3, 1])

# For calculation, it's often easiest to create the full list of observations
data = np.repeat(x, f)

print(f"Discrete Series Data (x): {x}")
print(f"Frequencies (f): {f}")
print("-------------------------------------")

# --- Range ---
# The difference between the max and min data points.
range_value = np.ptp(x)
print(f"Range: {range_value}")

# --- Variance ---
# The average of the squared differences from the Mean.
# We can calculate it directly on the repeated data array.
variance_value = np.var(data)
print(f"Variance: {variance_value:.2f}")

# --- Standard Deviation ---
# The square root of the variance.
std_deviation_value = np.std(data)
print(f"Standard Deviation: {std_deviation_value:.2f}")

# --- Coefficient of Variation ---
# CV = (Standard Deviation / Mean) * 100
# We must use a weighted average for the mean.
mean_value = np.average(x, weights=f)

if mean_value != 0:
    coeff_variation = (std_deviation_value / mean_value) * 100
    print(f"Coefficient of Variation: {coeff_variation:.2f}%")
else:
    print("Coefficient of Variation: Not applicable (mean is zero)")
