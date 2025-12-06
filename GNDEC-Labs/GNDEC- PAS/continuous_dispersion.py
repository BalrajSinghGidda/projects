import numpy as np

intervals = [(0, 10), (10, 20), (20, 30), (30, 40), (40, 50)]
frequency = np.array([5, 15, 25, 8, 7])

midpoints = np.array([(low + high) / 2 for low, high in intervals])
lower_bounds = np.array([low for low, high in intervals])
upper_bounds = np.array([high for low, high in intervals])

print(f"Intervals: {intervals}")
print(f"Frequencies: {frequency}")
print("-------------------------------------")

range_value = upper_bounds.max() - lower_bounds.min()
print(f"Range: {range_value}")

mean_value = np.average(midpoints, weights=frequency)

variance_value = np.average((midpoints - mean_value)**2, weights=frequency)
print(f"Variance: {variance_value:.2f}")

std_deviation_value = np.sqrt(variance_value)
print(f"Standard Deviation: {std_deviation_value:.2f}")

if mean_value != 0:
    coeff_variation = (std_deviation_value / mean_value) * 100
    print(f"Coefficient of Variation: {coeff_variation:.2f}%")
else:
    print("Coefficient of Variation: Not applicable (mean is zero)")
