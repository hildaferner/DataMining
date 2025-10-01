
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


alcohol = pd.read_excel("data/alcohol.xlsx")  
#print(alcohol.head())
#print(alcohol.info())

alcohol_filtered = alcohol[
    alcohol["indicator_name"] == "Alcohol, total per capita (15+) consumption (SDG Indicator 3.5.2) (in litres of pure alcohol)"
]

# bara könsspecifika
alcohol_filtered = alcohol_filtered[alcohol_filtered["subgroup"].isin(["Male", "Female"])]


print(alcohol_filtered[["setting", "date", "subgroup", "estimate"]].head())


mpi = pd.read_excel("data/mpi.xlsx")
#print(mpi.head())

mpi_filtered = mpi[mpi["indicator_name"] == "Multidimensional Poverty Index"]

mpi_10_plus = mpi_filtered[mpi_filtered["subgroup"].isin(["10-17 years", "18+ years"])]
avg_mpi_10_plus = mpi_10_plus.groupby("date")["estimate"].mean()

mpi_18_plus = mpi_filtered[mpi_filtered["subgroup"] == "18+ years"]
avg_mpi_18_plus = mpi_18_plus.groupby("date")["estimate"].mean()

'''plt.figure(figsize=(10,6))

plt.plot(avg_mpi_10_plus.index, avg_mpi_10_plus.values, label="10+ years (global avg)", color="green")
plt.plot(avg_mpi_18_plus.index, avg_mpi_18_plus.values, label="18+ years (global avg)", color="blue")

plt.title("Global MPI trends by age group")
plt.xlabel("Year")
plt.ylabel("MPI (average across countries)")
plt.legend()
plt.grid(True)
plt.show()'''

merged = alcohol_filtered.merge(mpi_10_plus, on=["setting", "date"], how="inner")

'''print(merged.head())
print(merged.info())'''


print(merged["subgroup_x"].unique())


pivot = merged.pivot_table(
    values="estimate_x",
    index=["setting", "date"],
    columns="subgroup_x"
).reset_index()


'''avg_by_year = pivot.groupby("date")[["Male", "Female"]].mean()

plt.plot(avg_by_year.index, avg_by_year["Male"], label="Male", color="blue")
plt.plot(avg_by_year.index, avg_by_year["Female"], label="Female", color="red")
plt.legend()
plt.title("Global average alcohol consumption by gender")
plt.xlabel("Year")
plt.ylabel("Litres per capita")
plt.show()

pivot["diff_male_female"] = pivot["Male"] - pivot["Female"]



avg_diff = pivot.groupby("setting")["diff_male_female"].mean().sort_values()

plt.figure(figsize=(8, 20)) 
plt.barh(avg_diff.index, avg_diff.values)
plt.axvline(0, color="black", linewidth=1)
plt.title("Average gender difference in alcohol consumption")
plt.xlabel("Difference (Male - Female)")
plt.ylabel("Country")
plt.tight_layout()  # gör så att etiketter inte klipps av
plt.show()

'''

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

# MPI range
bins = np.linspace(0, pivot["estimate_y"].max(), 15)  # nr of intervals = 15-1
pivot["mpi_bin"] = pd.cut(pivot["estimate_y"], bins)

# avg gender diff by mpi range
avg_diff_by_mpi = pivot.groupby("mpi_bin")["diff_male_female"].mean()

plt.figure(figsize=(8,6))
avg_diff_by_mpi.plot(kind="barh", color="purple")
plt.axvline(0, color="black", linewidth=1)
plt.title("Gender difference in alcohol consumption by MPI level")
plt.xlabel("Difference (Male - Female, litres per capita)")
plt.ylabel("MPI range")
plt.tight_layout()
plt.show()

# scetter plot for gender diff, mpi over time
plt.figure(figsize=(10,6))
sc = plt.scatter(
    pivot["date"], pivot["estimate_y"],
    c=pivot["diff_male_female"], cmap="coolwarm", s=50, alpha=0.7
)
plt.colorbar(sc, label="Difference (Male - Female)")
plt.title("Gender difference in alcohol consumption across MPI and time")
plt.xlabel("Year")
plt.ylabel("MPI")
plt.show()