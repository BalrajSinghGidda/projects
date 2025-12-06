import numpy as np
import pandas as pd
from scipy.stats import skew, kurtosis

# Individual series data
data = np.array([2, 3, 4, 5, 6, 7, 8, 9, 10])

print(f"Individual Series Data: {data}")
print("----------------------------------")

# Calculate skewness and kurtosis
skewness = skew(data)
kurt = kurtosis(data)

print(f"Skewness: {skewness:.4f}")
print(f"Kurtosis (Excess): {kurt:.4f}")

