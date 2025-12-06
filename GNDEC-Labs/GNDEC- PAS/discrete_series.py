
import numpy as np
from scipy import stats

# Discrete Series: Data points (x) and their corresponding frequencies (f)
x = np.array([10, 20, 30, 40, 50])
f = np.array([5, 12, 15, 8, 3])

# To work with this data, we create the full list of observations
data = np.repeat(x, f)

print(f"Discrete Series Data (x): {x}")
print(f"Frequencies (f): {f}")
print("-------------------------------------")

# --- Mean ---
# For a discrete series, the mean is sum(f*x) / sum(f).
# np.average with the 'weights' parameter does this efficiently.
mean_value = np.average(x, weights=f)
print(f"Mean: {mean_value}")

# --- Median ---
# The median is the middle value. We can find it from the repeated data array.
median_value = np.median(data)
print(f"Median: {median_value}")

# --- Mode ---
# The mode is the observation with the highest frequency.
# We can find the index of the max frequency and get the corresponding x value.
mode_value = x[np.argmax(f)]
print(f"Mode: {mode_value} (with frequency {np.max(f)})")
