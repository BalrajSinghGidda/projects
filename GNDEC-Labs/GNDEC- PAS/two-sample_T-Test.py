import numpy as np
from scipy.stats import ttest_ind

g1 = np.array([5.1, 4.9, 5.0, 5.2, 5.3])
g2 = np.array([4.7, 4.8, 4.9, 5.0, 4.6])

t_stat_welch, p_value_welch = ttest_ind(g1, g2, equal_var=False)  # Welch's
t_stat_student, p_value_student = ttest_ind(g1, g2, equal_var=True)  # Student's

print("Two-sample t-test (Welch's)")
print("---------------------------")
print(f"Group1 mean = {g1.mean():.4f}, n1 = {len(g1)}")
print(f"Group2 mean = {g2.mean():.4f}, n2 = {len(g2)}")
print(f"Welch t-statistic = {t_stat_welch:.4f}")
print(f"Welch p-value = {p_value_welch:.4f}")

