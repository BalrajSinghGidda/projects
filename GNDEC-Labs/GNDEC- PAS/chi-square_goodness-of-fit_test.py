import numpy as np
from scipy.stats import chisquare
 
# Observed and expected frequencies
observed = np.array([8, 9, 10, 12, 11, 10])
expected = np.array([10, 10, 10, 10, 10, 10])  # Fair die expectation (60/6 = 10 each)
 
chi_stat, p_value = chisquare(f_obs=observed, f_exp=expected)
 
print("Chi-Square Goodness-of-Fit Test")
print("--------------------------------")
print(f"Observed: {observed}")
print(f"Expected: {expected}")
print(f"Chi-square statistic = {chi_stat:.4f}")
print(f"p-value = {p_value:.4f}")

