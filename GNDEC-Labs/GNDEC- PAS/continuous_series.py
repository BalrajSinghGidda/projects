
import numpy as np

# Continuous Series: Class intervals and their frequencies
# We represent intervals as a list of tuples
intervals = [(0, 10), (10, 20), (20, 30), (30, 40), (40, 50)]
frequency = np.array([5, 15, 25, 8, 7])

# --- Midpoints ---
# Calculate the midpoint for each class interval
midpoints = np.array([(low + high) / 2 for low, high in intervals])

print(f"Intervals: {intervals}")
print(f"Frequencies: {frequency}")
print(f"Midpoints: {midpoints}")
print("-------------------------------------")


# --- Mean ---
# Mean for continuous series is sum(f*midpoint) / sum(f)
mean_value = np.average(midpoints, weights=frequency)
print(f"Mean: {mean_value:.2f}")

# --- Median ---
# Formula: L + [ (N/2 - cf) / f ] * h
N = np.sum(frequency)
cumulative_frequency = np.cumsum(frequency)
median_class_index = np.where(cumulative_frequency >= N/2)[0][0]

L = intervals[median_class_index][0]
cf = cumulative_frequency[median_class_index - 1] if median_class_index > 0 else 0
f = frequency[median_class_index]
h = intervals[median_class_index][1] - intervals[median_class_index][0]

median_value = L + ((N/2 - cf) / f) * h
print(f"Median: {median_value:.2f}")

# --- Mode ---
# Formula: L + [ (f1 - f0) / (2*f1 - f0 - f2) ] * h
modal_class_index = np.argmax(frequency)

L_mode = intervals[modal_class_index][0]
f1 = frequency[modal_class_index]
f0 = frequency[modal_class_index - 1] if modal_class_index > 0 else 0
f2 = frequency[modal_class_index + 1] if modal_class_index < len(frequency) - 1 else 0
h_mode = intervals[modal_class_index][1] - intervals[modal_class_index][0]

mode_value = L_mode + ((f1 - f0) / (2*f1 - f0 - f2)) * h_mode
print(f"Mode: {mode_value:.2f}")
