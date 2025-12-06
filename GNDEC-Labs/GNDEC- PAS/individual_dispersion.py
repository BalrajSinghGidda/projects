
import numpy as np

# Individual Series: A simple list of numbers
data = np.array([2, 4, 4, 4, 5, 5, 7, 9])

print(f"Individual Series Data: {data}")
print("-------------------------------------")

# --- Range ---
# The difference between the maximum and minimum values.
# np.ptp (peak-to-peak) calculates this directly.
range_value = np.ptp(data)
print(f"Range: {range_value}")

# --- Variance ---
# The average of the squared differences from the Mean.
variance_value = np.var(data)
print(f"Variance: {variance_value:.2f}")

# --- Standard Deviation ---
# The square root of the variance.
std_deviation_value = np.std(data)
print(f"Standard Deviation: {std_deviation_value:.2f}")

# --- Coefficient of Variation ---
# A measure of relative variability. It is the ratio of the standard deviation to the mean.
mean_value = np.mean(data)
# Avoid division by zero if the mean is 0
if mean_value != 0:
    coeff_variation = (std_deviation_value / mean_value) * 100
    print(f"Coefficient of Variation: {coeff_variation:.2f}%")
else:
    print("Coefficient of Variation: Not applicable (mean is zero)")
