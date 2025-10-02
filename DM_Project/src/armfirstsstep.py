import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pyfpgrowth

# Preprocessing

# Columns and rows of interest
alcohol = pd.read_excel("data/alcohol.xlsx")
alcohol_filtered = alcohol[alcohol["indicator_name"] == "Alcohol, total per capita (15+) consumption (SDG Indicator 3.5.2) (in litres of pure alcohol)"]
alcohol_filtered = alcohol_filtered[alcohol_filtered["subgroup"].isin(["Male", "Female"])]
alcohol_filtered.drop(['source', 'population', 'flag', 'iso3', 'favourable_indicator', 'whoreg6', 'update', 'dataset_id', 'ordered_dimension', 'subgroup_order', 'reference_subgroup'], axis=1, inplace=True)

# Remove unsure datapoints
# alcohol_filtered_dp = alcohol_filtered[alcohol_filtered["ci_lb"] != 0].copy()  # Where lower bound could be 0
alcohol_filtered["rel_ci_width"] = (alcohol_filtered["ci_ub"] - alcohol_filtered["ci_lb"] )/ alcohol_filtered["estimate"]

x_alcohol = 2
alcohol_filtered = alcohol_filtered[alcohol_filtered["rel_ci_width"] < x_alcohol].copy()

# Columns and rows of interest
mpi = pd.read_excel("data/mpi.xlsx")
mpi_filtered = mpi[mpi["indicator_abbr"] == "mpi"]
mpi_10_plus = mpi_filtered[mpi_filtered["subgroup"].isin(["10-17 years", "18+ years"])]
mpi_10_plus = mpi_10_plus.copy()
mpi_10_plus.drop(['source', 'indicator_name', 'population', 'flag', 'favourable_indicator', 'ordered_dimension', 'subgroup_order', 'reference_subgroup', 'whoreg6', 'dataset_id', 'update'], axis=1, inplace=True)

x_mpi = 0.01255
mpi_10_plus = mpi_10_plus[mpi_10_plus["se"] < x_mpi].copy()

merged = alcohol_filtered.merge(mpi_10_plus, on=["setting", "date"], how="inner")

# Pivots

pivot = merged.pivot_table(
    values="estimate_x",
    index=["setting", "date"],
    columns="subgroup_x"
).reset_index()


pivot = merged.pivot_table(
    values=["estimate_x", "estimate_y"],  # to keep both alcohol and api
    index=["setting", "date", "subgroup_x"],
).reset_index()


pivot = pivot.pivot_table(
    values="estimate_x",
    index=["setting", "date", "estimate_y"],
    columns="subgroup_x"
).reset_index()

pivot["diff_male_female"] = pivot["Male"] - pivot["Female"]
pivot["totalcon"] = pivot["Male"] + pivot["Female"]
pivot["diff_male_female_proc"] = (pivot["Male"] - pivot["Female"]) / (pivot["Male"] + pivot["Female"])

# Asocciaction Rule Mining

# Discrete variables (5 for each variable, 20% of datapoints in each)

# These 3 are kind of the same? but could be used, i guess
#pivot["Female_cat"] = pd.qcut(pivot["Female"], q=5, labels=["low_Female", "mediumlow_Female", "medium_Female", "mediumhigh_Female", "high_Female"])
#pivot["Male_cat"] = pd.qcut(pivot["Male"], q=5, labels=["low_Male", "mediumlow_Male", "medium_Male", "mediumhigh_Male", "high_Male"])
#pivot["Diff_proc_cat"] = pd.qcut(pivot["diff_male_female_proc"], q=5, labels=["low_DiffProc", "mediumlow_DiffProc", "medium_DiffProc", "mediumhigh_DiffProc", "high_DiffProc"])


pivot["Total_cat"] = pd.qcut(pivot["totalcon"], q=5, labels=["low_Total", "mediumlow_Total", "medium_Total", "mediumhigh_Total", "high_Total"])
pivot["Diff_cat"] = pd.qcut(pivot["diff_male_female"], q=5, labels=["low_Diff", "mediumlow_Diff", "medium_Diff", "mediumhigh_Diff", "high_Diff"])
pivot["MPI_cat"] = pd.qcut(pivot["estimate_y"], q=5, labels=["low_MPI", "mediumlow_MPI", "medium_MPI", "mediumhigh_MPI", "high_MPI"])

# Convert the Query column to a list of lists
# associations = pivot[["Female_cat", "Male_cat", "Total_cat", "Diff_cat", "MPI_cat"]].apply(lambda row: row.astype(str).tolist(), axis=1).tolist()
associations = pivot[["Total_cat", "Diff_cat", "MPI_cat"]].apply(lambda row: row.astype(str).tolist(), axis=1).tolist()

print(f' len of associations = {len(associations)}')

nr_records = len(associations)
min_support = 0.07
sigma = min_support * nr_records
print(f'Min support = {min_support}')

# the function find_frequent_patterns takes SIGMA as second parameter
patterns = pyfpgrowth.find_frequent_patterns(associations, sigma)

# number of frequent itemsets found
num_frequent_itemsets = len(patterns)

# maximum size of frequent itemsets
max_itemset_size = max(len(itemset) for itemset in patterns)
print(f'Number of frequent itemsets: {num_frequent_itemsets}')
print(f'Maximum size of frequent itemsets: {max_itemset_size}')
# the support of an itemset is the fraction of records containing the items in the itemset (in this case, the keywords)
support = {key: value / len(associations) for key, value in patterns.items()}

most_frequent_item = max(patterns.items(), key=lambda x: x[1])
print("Most frequent itemset:", most_frequent_item[0])
print("Support count:", most_frequent_item[1])

'''
# Find relevant values for minimum support

num_records = len(associations)
min_support_values = [0.001, 0.01, 0.05, 0.1, 0.2012]
for min_support in min_support_values:
# the second parameter of the function 'find_frequent_patterns' is the support count, NOT the min-support, so you have to calculate it
    support_count = min_support * num_records
    patterns = pyfpgrowth.find_frequent_patterns(associations, support_count)
    support = {key: value / len(associations) for key, value in patterns.items()}
    print(min_support)
    print(f"Minimum support: {min_support}, Support count: {support_count:.0f}")
    print(f'Found {len(patterns)} patterns')
    #print('Patterns', patterns)
    #print('Support', support)
    print()

'''
    
confidence = 0.8
print(f'Confidence: {confidence}')
patterns = pyfpgrowth.find_frequent_patterns(associations, sigma)
rules = pyfpgrowth.generate_association_rules(patterns, confidence)

num_rules = len(rules)
print(rules)
print(f'Number of rules: {num_rules}')

# Filtrera rules som innehåller MPI
rules_with_mpi = {k: v for k, v in rules.items() 
                  if any('MPI' in item for item in k) or any('MPI' in item for item in v[0])}

print(f'Number of rules containing MPI: {len(rules_with_mpi)}')
print(rules_with_mpi)
