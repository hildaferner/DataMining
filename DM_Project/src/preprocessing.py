import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

alcohol = pd.read_excel("data/alcohol.xlsx") 
alcohol_filtered = alcohol[
    alcohol["indicator_name"] == "Alcohol, total per capita (15+) consumption (SDG Indicator 3.5.2) (in litres of pure alcohol)"
]
alcohol_filtered = alcohol_filtered[alcohol_filtered["subgroup"].isin(["Male", "Female"])]

mpi = pd.read_excel("data/mpi.xlsx")
mpi_filtered = mpi[mpi["indicator_name"] == "Multidimensional Poverty Index"]
mpi_10_plus = mpi_filtered[mpi_filtered["subgroup"].isin(["10-17 years", "18+ years"])]

merged = alcohol_filtered.merge(mpi_10_plus, on=["setting", "date"], how="inner")

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
