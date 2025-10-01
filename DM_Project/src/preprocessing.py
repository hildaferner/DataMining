import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


# Columns and rows of interest
alcohol = pd.read_excel("data/alcohol.xlsx")
alcohol_filtered = alcohol[alcohol["indicator_name"] == "Alcohol, total per capita (15+) consumption (SDG Indicator 3.5.2) (in litres of pure alcohol)"]
alcohol_filtered = alcohol_filtered[alcohol_filtered["subgroup"].isin(["Male", "Female"])]
alcohol_filtered.drop(['source', 'population', 'flag', 'iso3', 'favourable_indicator', 'whoreg6', 'update', 'dataset_id', 'ordered_dimension', 'subgroup_order', 'reference_subgroup'], axis=1, inplace=True)


# Columns and rows of interest
mpi = pd.read_excel("data/mpi.xlsx")
mpi_filtered = mpi[mpi["indicator_abbr"] == "mpi"]
mpi_10_plus = mpi_filtered[mpi_filtered["subgroup"].isin(["10-17 years", "18+ years"])]
mpi_10_plus.drop(['source', 'indicator_name', 'population', 'flag', 'favourable_indicator', 'ordered_dimension', 'subgroup_order', 'reference_subgroup', 'whoreg6', 'dataset_id', 'update'], axis=1, inplace=True)


print(alcohol_filtered.head())
print(mpi_10_plus.head())


#print(len(alcohol_filtered))    # = 7866
#print(len(mpi_10_plus))         # = 422


merged = alcohol_filtered.merge(mpi_10_plus, on=["setting", "date"], how="inner")


#estimate_x → alkoholkonsumtion per capita (från alcohol.xlsx)
#estimate_y → Multidimensional Poverty Index (från mpi.xlsx)




pivot = merged.pivot_table(
    values="estimate_x",
    index=["setting", "date"],
    columns="subgroup_x"
).reset_index()


pivot = merged.pivot_table(
    values=["estimate_x", "estimate_y"],  # to keep both alcohol and api
    index=["setting", "date", "subgroup_x"],
).reset_index()


# gender pivot
pivot = pivot.pivot_table(
    values="estimate_x",
    index=["setting", "date", "estimate_y"],
    columns="subgroup_x"
).reset_index()


pivot["diff_male_female"] = pivot["Male"] - pivot["Female"]


#print(pivot.isna().sum()) # Ingen NaN efter pivot (allt har värdet 0) vilket är bra!
