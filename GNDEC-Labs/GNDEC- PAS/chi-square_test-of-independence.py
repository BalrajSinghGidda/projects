import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency
 
# Contingency table
data = np.array([[20, 15, 15],
                 [10, 25, 15]])
 
table = pd.DataFrame(data,
                     index=['Male', 'Female'],
                     columns=['Action', 'Comedy', 'Drama'])
 
chi_stat, p_value, dof, expected = chi2_contingency(table)
 
print("Chi-Square Test of Independence")
print("--------------------------------")
print(table)
print("\nExpected Frequencies:")
print(pd.DataFrame(expected, index=['Male', 'Female'], columns=['Action', 'Comedy', 'Drama']))
print(f"\nChi-square statistic = {chi_stat:.4f}")
print(f"Degrees of freedom = {dof}")
print(f"p-value = {p_value:.4f}")

