
import pandas as pd
import matplotlib.pyplot as plt

alcohol = pd.read_excel("data/alcohol.xlsx")  
#print(alcohol.head())
#print(alcohol.info())

'''policies = pd.read_excel("data/alcohol_policies.xlsx")
print(policies.head())'''

mpi = pd.read_excel("data/mpi.xlsx")
#print(mpi.head())

merged = alcohol.merge(mpi, on=["setting", "date"], how="inner")

'''print(merged.head())
print(merged.info())'''


print(merged["subgroup_x"].unique())


pivot = merged.pivot_table(
    values="estimate_x",
    index=["setting", "date"],
    columns="subgroup_x"
).reset_index()


avg_by_year = pivot.groupby("date")[["Male", "Female"]].mean()

plt.plot(avg_by_year.index, avg_by_year["Male"], label="Male", color="blue")
plt.plot(avg_by_year.index, avg_by_year["Female"], label="Female", color="red")
plt.legend()
plt.title("Global average alcohol consumption by gender")
plt.xlabel("Year")
plt.ylabel("Litres per capita")
plt.show()

pivot["diff_male_female"] = pivot["Male"] - pivot["Female"]

avg_diff = pivot.groupby("setting")["diff_male_female"].mean().sort_values()

plt.barh(avg_diff.index, avg_diff.values)
plt.axvline(0, color="black", linewidth=1)
plt.title("Average gender difference in alcohol consumption")
plt.xlabel("Difference (Male - Female)")
plt.ylabel("Country")
plt.show()


