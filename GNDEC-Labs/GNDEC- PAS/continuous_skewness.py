import numpy as np
from scipy.stats import skew, kurtosis

# Class intervals and frequencies
intervals = [(0,10), (10,20), (20,30), (30,40), (40,50)]
frequency = np.array([5, 15, 25, 8, 7])

# Calculate midpoints
midpoints = np.array([(low + high) / 2 for low, high in intervals])
data = np.repeat(midpoints, frequency)

print(f"Intervals: {intervals}")
print(f"Frequencies: {frequency}")
print("----------------------------------")

# Calculate skewness and kurtosis
skewness = skew(data)
kurt = kurtosis(data)

print(f"Skewness: {skewness:.4f}")
print(f"Kurtosis (Excess): {kurt:.4f}")

