# %% [markdown]
# # Stage 1a — Data audit
#
# Profile both source files before any analysis touches them: shape, coverage,
# dtypes, missingness and duplicates.

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

CONFLICT_ONSET = pd.Timestamp("2026-03-16")

daily = pd.read_csv("datasets/processed/master_daily.csv", parse_dates=["date"]).set_index("date").sort_index()
weekly = pd.read_csv("datasets/processed/master_weekly.csv", parse_dates=["week_start"]).set_index("week_start").sort_index()

print("daily ", daily.shape, daily.index.min().date(), "..", daily.index.max().date())
print("weekly", weekly.shape, weekly.index.min().date(), "..", weekly.index.max().date())

# %% [markdown]
# ## Coverage, dtypes and missingness

# %%
def profile(frame, name):
    rows = []
    for col in frame.columns:
        s = frame[col]
        rows.append({
            "column": col,
            "dtype": str(s.dtype),
            "n": int(s.shape[0]),
            "nulls": int(s.isna().sum()),
            "null_pct": round(100 * float(s.isna().mean()), 2),
            "n_unique": int(s.nunique()),
            "min": s.min() if pd.api.types.is_numeric_dtype(s) else None,
            "max": s.max() if pd.api.types.is_numeric_dtype(s) else None,
        })
    out = pd.DataFrame(rows)
    print()
    print(name)
    print(out.to_string(index=False))
    return out

prof_daily = profile(daily, "master_daily.csv")
prof_weekly = profile(weekly, "master_weekly.csv")

print()
print("duplicate index values  daily:", int(daily.index.duplicated().sum()),
      " weekly:", int(weekly.index.duplicated().sum()))
print("index monotonic         daily:", daily.index.is_monotonic_increasing,
      " weekly:", weekly.index.is_monotonic_increasing)

gaps = daily.index.to_series().diff().dt.days.value_counts().sort_index()
print()
print("spacing between consecutive daily rows (days -> count):")
print(gaps.to_string())

# %% [markdown]
# ## Distributions

# %%
print(daily.describe().T.to_string())
print()
print(weekly.describe().T.to_string())

# %% [markdown]
# ## Sampling grain per column
#
# A column that changes on fewer than half of its rows is forward-filled, not
# daily. Treating it as daily inflates every sample size downstream.

# %%
from src.data.loaders import grain_report

weekly_ff = weekly.reindex(daily.index, method="ffill")
combined = daily.join(weekly_ff)
grain = grain_report(combined)
print(grain.to_string(index=False))
grain.to_csv(f"{REPORTS}/grain_report.csv", index=False)

print()
print("ACLED columns are weekly and forward-filled. They are tested at weekly")
print("frequency in the analysis notebook rather than resampled to daily.")

# %% [markdown]
# ## Series plots

# %%
fig, axes = plt.subplots(3, 1, figsize=(9, 7), sharex=True)
axes[0].plot(daily.index, daily["brent_close"], lw=.8)
axes[0].set_ylabel("Brent close")
axes[0].axvline(CONFLICT_ONSET, color="crimson", ls="--", lw=.8)
ret = np.log(daily["brent_close"]).diff()
axes[1].plot(daily.index, ret, lw=.6, color="#444")
axes[1].set_ylabel("realised return")
axes[1].axvline(CONFLICT_ONSET, color="crimson", ls="--", lw=.8)
axes[2].plot(daily.index, ret.rolling(21).std(), lw=1, color="#c44")
axes[2].set_ylabel("21d volatility")
axes[2].axvline(CONFLICT_ONSET, color="crimson", ls="--", lw=.8)
axes[2].set_xlabel("date")
fig.suptitle("Brent: level, return, realised volatility")
plt.tight_layout()

# %%
fig, axes = plt.subplots(1, 2, figsize=(9, 3))
axes[0].hist(ret.dropna(), bins=50, color="#678")
axes[0].set_title("distribution of realised returns")
axes[1].plot(weekly.index, weekly["acled_events"], marker=".", lw=.8, label="events")
axes[1].plot(weekly.index, weekly["hormuz_severity"] * 10, marker=".", lw=.8, label="severity x10")
axes[1].axvline(CONFLICT_ONSET, color="crimson", ls="--", lw=.8)
axes[1].legend(fontsize=7)
axes[1].set_title("weekly conflict series")
plt.tight_layout()

print("skew", round(float(ret.skew()), 4), " kurtosis", round(float(ret.kurtosis()), 4))

# %%
with open(f"{REPORTS}/data_audit.txt", "w") as fh:
    print("DATA AUDIT", file=fh)
    print("=" * 70, file=fh)
    print(file=fh)
    print(f"daily  {daily.shape}  {daily.index.min().date()} .. {daily.index.max().date()}", file=fh)
    print(f"weekly {weekly.shape}  {weekly.index.min().date()} .. {weekly.index.max().date()}", file=fh)
    print(file=fh)
    print("master_daily.csv", file=fh)
    print(prof_daily.to_string(index=False), file=fh)
    print(file=fh)
    print("master_weekly.csv", file=fh)
    print(prof_weekly.to_string(index=False), file=fh)
    print(file=fh)
    print("duplicate index values: daily " + str(int(daily.index.duplicated().sum()))
          + ", weekly " + str(int(weekly.index.duplicated().sum())), file=fh)
    print(file=fh)
    print("GRAIN", file=fh)
    print(grain.to_string(index=False), file=fh)

print("wrote", f"{REPORTS}/data_audit.txt")
