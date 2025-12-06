import numpy as np
from scipy.stats import ttest_1samp

data = np.array([5.1, 4.9, 5.0, 5.2, 5.3])
popmean = 5.0

t_stat, p_value = ttest_1samp(data, popmean)

print("One-sample t-test")
print("------------------")
print(f"Sample mean = {data.mean():.4f}, n = {len(data)}")
print(f"t-statistic = {t_stat:.4f}")
print(f"p-value = {p_value:.4f}")

