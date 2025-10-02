import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy import stats

# Columns and rows of interest
alcohol = pd.read_excel("data/alcohol.xlsx")
alcohol_filtered = alcohol[alcohol["indicator_name"] == "Alcohol, total per capita (15+) consumption (SDG Indicator 3.5.2) (in litres of pure alcohol)"]
alcohol_filtered = alcohol_filtered[alcohol_filtered["subgroup"].isin(["Male", "Female"])]
alcohol_filtered.drop(['source', 'population', 'flag', 'iso3', 'favourable_indicator', 'whoreg6', 'update', 'dataset_id', 'ordered_dimension', 'subgroup_order', 'reference_subgroup'], axis=1, inplace=True)

print(len(alcohol_filtered))

# Remove unsure datapoints
# alcohol_filtered_dp = alcohol_filtered[alcohol_filtered["ci_lb"] != 0].copy()  # Where lower bound could be 0
alcohol_filtered["rel_ci_width"] = (alcohol_filtered["ci_ub"] - alcohol_filtered["ci_lb"] )/ alcohol_filtered["estimate"]

# Plot in order to choose value for rel_ci_witdh ---> X
plt.hist(alcohol_filtered["rel_ci_width"], bins=50)
plt.xlabel("Relative CI width")
plt.ylabel("Count")
plt.title("Distribution of relative CI width (Data: alcohol)")
plt.show()

x_alcohol = 2
alcohol_filtered = alcohol_filtered[alcohol_filtered["rel_ci_width"] < x_alcohol].copy()
print(len(alcohol_filtered))

# Columns and rows of interest
mpi = pd.read_excel("data/mpi.xlsx")
mpi_filtered = mpi[mpi["indicator_abbr"] == "mpi"]
mpi_10_plus = mpi_filtered[mpi_filtered["subgroup"].isin(["10-17 years", "18+ years"])]
mpi_10_plus = mpi_10_plus.copy()
mpi_10_plus.drop(['source', 'indicator_name', 'population', 'flag', 'favourable_indicator', 'ordered_dimension', 'subgroup_order', 'reference_subgroup', 'whoreg6', 'dataset_id', 'update'], axis=1, inplace=True)

# Plot in order to choose value for SE ---> X
plt.hist(mpi_10_plus["se"], bins=50)
plt.xlabel("Standard Error (SE)")
plt.ylabel("Count")
plt.title("Distribution of Standard Error (Data: MPI)")
plt.show()

print(len(mpi_10_plus))

x_mpi = 0.01255
mpi_10_plus = mpi_10_plus[mpi_10_plus["se"] < x_mpi].copy()

print(len(mpi_10_plus))

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


pivot = pivot.pivot_table(
    values="estimate_x",
    index=["setting", "date", "estimate_y"],
    columns="subgroup_x"
).reset_index()


pivot["diff_male_female"] = pivot["Male"] - pivot["Female"]
pivot["totalcon"] = pivot["Male"] + pivot["Female"]
pivot["diff_male_female_proc"] = (pivot["Male"] - pivot["Female"]) / (pivot["Male"] + pivot["Female"])


#print(pivot.isna().sum()) # Ingen NaN efter pivot (allt har värdet 0) vilket är bra!
print("Missing alcohol:", merged["estimate_x"].isna().sum())
print("Missing MPI:", merged["estimate_y"].isna().sum())

# Inga dubletter
'''duplicates = merged.duplicated(subset=["setting", "date", "subgroup_x"])
print("Antal dubbletter:", duplicates.sum())
dup_rows = merged[duplicates]
print(dup_rows[["setting", "date", "subgroup_x", "estimate_x", "estimate_y"]].sort_values(["setting","date","subgroup_x"]))'''


# Scatterplot för att se fördelningen
'''sns.scatterplot(data=merged, x="estimate_x", y="estimate_y", hue="subgroup_x")
plt.xlabel("Alcohol consumption (litres per capita, 15+)")
plt.ylabel("MPI")
plt.show()'''

# Boxplots för att se outliers
'''fig, axes = plt.subplots(1, 2, figsize=(12, 5))
sns.boxplot(y=merged["estimate_x"], ax=axes[0])
axes[0].set_title("Alcohol")
sns.boxplot(y=merged["estimate_y"], ax=axes[1])
axes[1].set_title("MPI")
plt.show()'''


#test
'''sns.boxplot(data=pivot[["Male", "Female", "diff_male_female", "estimate_y"]])
plt.show()'''

numerical_cols = ["Female", "Male", "estimate_y", "diff_male_female"]
data_std = pivot[numerical_cols].copy()

scaler = StandardScaler()
data_scaled = scaler.fit_transform(data_std)

data_scaled_df = pd.DataFrame(data_scaled, columns=numerical_cols)
print(data_scaled_df.head())

pca = PCA(n_components=2)
pca_result = pca.fit_transform(data_scaled_df)

print("Explained variance ratio:", pca.explained_variance_ratio_)

pca_df = pd.DataFrame(pca_result, columns=["PC1", "PC2"])
pca_df[["setting", "date"]] = pivot[["setting", "date"]].reset_index(drop=True)

print(pd.DataFrame(pca.components_, columns=numerical_cols, index=["PC1", "PC2"]))

# Pearsons
xp = pivot["diff_male_female"]
yp = pivot["estimate_y"]

res_p = stats.pearsonr(xp, yp)
print("Pearson correlation:", res_p[0])

sns.regplot(x=xp, y=yp, ci=None, line_kws={"color": "red"})
plt.xlabel("Difference in alcohol consumption (Male - Female)")
plt.ylabel("MPI")
plt.title(f"Pearson r = {res_p[0]:.4f}")
plt.show()
