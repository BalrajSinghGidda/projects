import numpy as np
import pandas as pd
from scipy.stats import skew, kurtosis

# Discrete data (x) with frequencies (f)
x = np.array([2, 3, 4, 5, 6])
f = np.array([2, 4, 5, 3, 1])

# Expand data according to frequencies
data = np.repeat(x, f)

print(f"Discrete Series Data (x): {x}")
print(f"Frequencies (f): {f}")
print("----------------------------------")

# Calculate skewness and kurtosis
skewness = skew(data)
kurt = kurtosis(data)

print(f"Skewness: {skewness:.4f}")
print(f"Kurtosis (Excess): {kurt:.4f}")

