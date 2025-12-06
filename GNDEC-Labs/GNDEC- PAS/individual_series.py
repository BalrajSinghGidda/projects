
import numpy as np
from scipy import stats

# Individual Series: A simple list of numbers
data = [1, 2, 2, 3, 4, 5, 5, 5, 6, 7]

# --- Mean ---
# The arithmetic average of the data.
mean_value = np.mean(data)
print(f"Individual Series Data: {data}")
print(f"Mean: {mean_value}")

# --- Median ---
# The middle value of the sorted dataset.
median_value = np.median(data)
print(f"Median: {median_value}")

# --- Mode ---
# The value that appears most frequently.
# scipy.stats.mode returns the mode and its count.
mode_result = stats.mode(data)
print(f"Mode: {mode_result.mode} (appears {mode_result.count} times)")
