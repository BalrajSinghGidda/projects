import numpy as np
from scipy import stats

# Create a sample dataset
data = [1, 2, 2, 3, 4, 5, 5, 5, 6, 7, 8, 8, 8, 8, 9]

# Calculate the mean
mean = np.mean(data)
print(f"Mean: {mean}")

# Calculate the median
median = np.median(data)
print(f"Median: {median}")

# Calculate the mode
mode = stats.mode(data)
print(f"Mode: {mode.mode}")
