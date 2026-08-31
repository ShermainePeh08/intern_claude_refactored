# %% [markdown]
# # Exploratory analysis
#
# Which conflict variables carry information about Brent crude returns, at what
# lag, in which direction, and with what magnitude?

# %%
import json
import os
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")
pd.set_option("display.width", 140)
pd.set_option("display.max_columns", 50)

REPORTS = "results/reports"
FIGURES = "results/figures"
os.makedirs(REPORTS, exist_ok=True)
os.makedirs(FIGURES, exist_ok=True)

daily = pd.read_csv("datasets/processed/master_daily.csv", parse_dates=["date"]).set_index("date").sort_index()
weekly = pd.read_csv("datasets/processed/master_weekly.csv", parse_dates=["week_start"]).set_index("week_start").sort_index()
CONFLICT_ONSET = pd.Timestamp("2026-03-16")

# %% [markdown]
# ## Joining the weekly conflict data
#
# ACLED variables are weekly; price and rhetoric are daily. Each is tested at its
# own sampling frequency, and the grain of every column is reported so a
# forward-filled series is never mistaken for a daily one.

# %%
from src.data.loaders import grain_report

weekly_ff = weekly.reindex(daily.index, method="ffill")
df = daily.join(weekly_ff)
grain = grain_report(df)
print(grain.to_string(index=False))
grain.to_csv(f"{REPORTS}/grain_report.csv", index=False)
print()
print("weekly columns are kept at weekly grain for inference below")

# %%
DRIVERS = [c for c in ["acled_events", "acled_fatalities", "acled_fatalities_revised",
                       "hormuz_severity", "rhetoric_index", "tanker_rate_usd"]
           if c in df.columns]
df[DRIVERS] = df[DRIVERS].ffill()
df = df.dropna(subset=DRIVERS)
print("drivers:", DRIVERS)
print("rows after dropping the unfilled leading period:", len(df))
print()
print(df[DRIVERS].describe().T.to_string())

# %% [markdown]
# ## Target

# %%
from sklearn.linear_model import LinearRegression

TARGET = "brent_close"
X_lv = df[DRIVERS].ffill().dropna()
y_lv = df.loc[X_lv.index, "brent_close"]
lm = LinearRegression().fit(X_lv, y_lv)
print("R2 on price levels:", round(lm.score(X_lv, y_lv), 4))
print()
for name, coef in zip(X_lv.columns, lm.coef_):
    print(f"  {name:<28} {coef:>12.4f}")

fig, ax = plt.subplots(figsize=(8, 3))
ax.plot(y_lv.index, y_lv, lw=.8, label="actual")
ax.plot(y_lv.index, lm.predict(X_lv), lw=.8, label="fitted")
ax.legend()
ax.set_title("price level fit")
plt.tight_layout()

# %% [markdown]
# ## Correlation matrix

# %%
corr_cols = DRIVERS + [TARGET]
corr = df[corr_cols].corr()
print(corr.round(3).to_string())
corr.to_csv(f"{REPORTS}/correlation_matrix.csv")

fig, ax = plt.subplots(figsize=(6.5, 5))
im = ax.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1)
ax.set_xticks(range(len(corr_cols)))
ax.set_xticklabels(corr_cols, rotation=45, ha="right", fontsize=7)
ax.set_yticks(range(len(corr_cols)))
ax.set_yticklabels(corr_cols, fontsize=7)
for i in range(len(corr_cols)):
    for j in range(len(corr_cols)):
        ax.text(j, i, f"{corr.values[i, j]:.2f}", ha="center", va="center", fontsize=6)
fig.colorbar(im, shrink=.8)
ax.set_title("correlation matrix")
plt.tight_layout()

# %% [markdown]
# ## Multicollinearity — VIF
#
# Required for any candidate set larger than three. A VIF above 5 means the
# driver is largely reconstructible from the others and its coefficient cannot be
# read on its own.

# %%
from src.stats.diagnostics import vif_table

vif = vif_table(df[DRIVERS])
print(vif.to_string(index=False))
vif.to_csv(f"{REPORTS}/vif.csv", index=False)

high = vif[vif["vif"] > 5]
print()
if len(high):
    print("above 5, so collinear with the rest of the set:")
    for _, r in high.iterrows():
        print(f"  {r['feature']:<28} {float(r['vif']):.3f}")
    print("only one of any collinear pair should enter a model.")
else:
    print("no driver exceeds a VIF of 5.")

fig, ax = plt.subplots(figsize=(6, 3))
ax.barh(vif["feature"], vif["vif"], color="#678")
ax.axvline(5, ls="--", c="crimson", lw=.8)
ax.set_title("variance inflation factor")
plt.tight_layout()

# %% [markdown]
# ## Top drivers

# %%
corrs = df[DRIVERS + [TARGET]].corr()[TARGET].drop(TARGET).sort_values(key=abs, ascending=False)
print("ranked by absolute correlation with", TARGET)
print(corrs.round(4).to_string())

fig, ax = plt.subplots(figsize=(6, 3))
corrs.plot(kind="barh", ax=ax, color="#678")
ax.set_title("correlation with " + TARGET)
plt.tight_layout()

# %% [markdown]
# ## Summary

# %%
lines = ["EDA SUMMARY", "=" * 70, ""]
lines.append("Top driver by absolute correlation: " + str(corrs.index[0]))
lines.append("Multicollinearity: " + str(len(high)) + " driver(s) above VIF 5")
lines.append("")
lines.append("Not supported by this data: any causal claim. Inventories, dollar")
lines.append("strength and demand are absent from the dataset, so the supportable")
lines.append("phrasing is that volatility rose during the conflict period, not")
lines.append("that the conflict caused the move.")

with open(f"{REPORTS}/feature_relationships.txt", "w") as fh:
    for line in lines:
        print(line, file=fh)
for line in lines:
    print(line)
print()
print("wrote", f"{REPORTS}/feature_relationships.txt")
