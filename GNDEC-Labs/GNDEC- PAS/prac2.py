
import numpy as np

# Create a sample dataset
data = [15, 22, 34, 41, 53, 66, 72, 81, 88, 99]

# Calculate the range
data_range = np.ptp(data)
print(f"Range: {data_range}")

# Calculate the variance
variance = np.var(data)
print(f"Variance: {variance}")

# Calculate the standard deviation
std_dev = np.std(data)
print(f"Standard Deviation: {std_dev}")

# Calculate the coefficient of variation
mean = np.mean(data)
if mean != 0:
    coefficient_of_variation = (std_dev / mean) * 100
    print(f"Coefficient of Variation: {coefficient_of_variation:.2f}%")
else:
    print("Cannot calculate Coefficient of Variation because the mean is zero.")
