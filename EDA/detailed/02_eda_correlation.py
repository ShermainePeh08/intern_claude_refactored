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
#
# log_return at t is log(P_t+1 / P_t), the return realised over the next step.
# Price levels are not modelled: an R-squared near 0.99 on levels means the model
# has learned that today's price is close to yesterday's and has identified
# nothing.

# %%
df["log_return"] = np.log(df["brent_close"].shift(-1) / df["brent_close"])
df["realised_return"] = np.log(df["brent_close"] / df["brent_close"].shift(1))
df = df.dropna(subset=["log_return"])
TARGET = "log_return"

print(df[TARGET].describe().to_string())
print()
print("annualised vol:", round(float(df[TARGET].std() * np.sqrt(252)), 4))
print("share of up days:", round(float((df[TARGET] > 0).mean()), 4))

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
# ## Stationarity — ADF and KPSS
#
# The two tests have opposite nulls, so they can disagree. Both are reported with
# statistic, p-value and lag order, and the verdict names any disagreement rather
# than quietly reporting whichever is convenient.

# %%
from src.stats.diagnostics import stationarity_table

stat_cols = [c for c in [TARGET, "brent_close", "realised_return"] + DRIVERS if c in df.columns]
stat_cols = list(dict.fromkeys(stat_cols))
stat = stationarity_table(df[stat_cols])
print(stat.to_string(index=False))
stat.to_csv(f"{REPORTS}/stationarity.csv", index=False)

disagree = stat[stat["verdict"].str.startswith("disagree")]
print()
print(f"{len(disagree)} of {len(stat)} series give a disagreement between ADF and KPSS:")
for _, r in disagree.iterrows():
    print(f"  {r['column']:<28} {r['verdict']}")

with open(f"{REPORTS}/stationarity_report.txt", "w") as fh:
    print("STATIONARITY — ADF and KPSS", file=fh)
    print("statistic, p-value and lag order reported for both tests", file=fh)
    print(file=fh)
    print(stat.to_string(index=False), file=fh)

# %%
fig, axes = plt.subplots(1, 2, figsize=(9, 3))
axes[0].bar(range(len(stat)), stat["adf_p"], color="#678")
axes[0].axhline(.05, ls="--", c="crimson", lw=.8)
axes[0].set_xticks(range(len(stat)))
axes[0].set_xticklabels(stat["column"], rotation=60, ha="right", fontsize=6)
axes[0].set_title("ADF p-value (low = stationary)")
axes[1].bar(range(len(stat)), stat["kpss_p"], color="#867")
axes[1].axhline(.05, ls="--", c="crimson", lw=.8)
axes[1].set_xticks(range(len(stat)))
axes[1].set_xticklabels(stat["column"], rotation=60, ha="right", fontsize=6)
axes[1].set_title("KPSS p-value (low = non-stationary)")
plt.tight_layout()

# %% [markdown]
# ## Weekly-native testing
#
# The ACLED variables are tested against a weekly-aggregated target, so the test
# uses one observation per actual observation rather than one per forward-filled
# daily row.

# %%
from scipy import stats as _st

weekly_target = df[TARGET].resample("W-MON").sum().rename("weekly_return")
weekly_join = weekly.join(weekly_target, how="inner").dropna()
print("weekly observations available for inference:", len(weekly_join))
print()

wk_rows = []
for col in [c for c in weekly.columns if c in weekly_join.columns]:
    pair = weekly_join[[col, "weekly_return"]].dropna()
    if len(pair) > 10:
        r, p = _st.pearsonr(pair[col], pair["weekly_return"])
        wk_rows.append({"driver": col, "grain": "weekly", "pearson_r": round(float(r), 4),
                        "p_value": round(float(p), 4), "n": len(pair)})
weekly_tests = pd.DataFrame(wk_rows)
print(weekly_tests.to_string(index=False))
weekly_tests.to_csv(f"{REPORTS}/weekly_native_tests.csv", index=False)
print()
print("n here is weekly observations, not the daily row count.")

# %% [markdown]
# ## Significance of the driver-target links
#
# Every relationship carries a p-value and the significance band. A correlation
# coefficient on its own is not a finding.

# %%
from scipy import stats as sps

rows = []
for col in DRIVERS:
    pair = df[[col, TARGET]].dropna()
    r, p = sps.pearsonr(pair[col], pair[TARGET])
    rho, rho_p = sps.spearmanr(pair[col], pair[TARGET])
    band = 1.96 / np.sqrt(len(pair))
    rows.append({"driver": col, "pearson_r": round(float(r), 4), "pearson_p": round(float(p), 4),
                 "spearman_rho": round(float(rho), 4), "spearman_p": round(float(rho_p), 4),
                 "band": round(float(band), 4), "significant": bool(abs(r) > band), "n": len(pair)})
sig = pd.DataFrame(rows).sort_values("pearson_p").reset_index(drop=True)
print(sig.to_string(index=False))
sig.to_csv(f"{REPORTS}/significance.csv", index=False)

n_sig = int(sig["significant"].sum())
print()
print(f"{n_sig} of {len(sig)} drivers clear the band at the 5% level.")

# %% [markdown]
# ## Lag structure — cross-correlation and Granger
#
# Sign convention: a bar at a POSITIVE lag means the driver moved first and the
# target followed, which is the only configuration that supports a forecast. A
# spike at lag 0 is co-movement and supports nothing.

# %%
from src.stats.diagnostics import cross_correlation, granger_table

ccf_frames = {}
for col in DRIVERS:
    ccf_frames[col] = cross_correlation(df[col], df[TARGET], max_lag=7)

n_cols = 2
n_rows = int(np.ceil(len(DRIVERS) / n_cols))
fig, axes = plt.subplots(n_rows, n_cols, figsize=(10, 2.2 * n_rows), squeeze=False)
for ax, col in zip(axes.ravel(), DRIVERS):
    cc = ccf_frames[col]
    ax.bar(cc["lag"], cc["ccf"], color=["#c44" if s else "#bbb" for s in cc["significant"]])
    ax.axhline(float(cc["band"].iloc[0]), ls="--", lw=.7, c="k")
    ax.axhline(-float(cc["band"].iloc[0]), ls="--", lw=.7, c="k")
    ax.axvline(0, lw=.7, c="k")
    ax.set_title(col, fontsize=8)
    ax.tick_params(labelsize=6)
for ax in axes.ravel()[len(DRIVERS):]:
    ax.axis("off")
fig.suptitle("cross-correlation with " + TARGET + "  (positive lag = driver leads)")
plt.tight_layout()

# %%
for col in DRIVERS:
    cc = ccf_frames[col]
    lead = cc[cc["lag"] > 0]
    best = lead.iloc[lead["ccf"].abs().to_numpy().argmax()]
    at_zero = float(cc[cc["lag"] == 0]["ccf"].iloc[0])
    print(f"{col:<28} best lead lag {int(best['lag']):+d}  ccf {float(best['ccf']):+.4f}  "
          f"sig {bool(best['significant'])}   lag0 {at_zero:+.4f}")

# %%
granger_rows = []
for col in DRIVERS:
    gt = granger_table(df[col], df[TARGET], max_lag=7)
    if len(gt):
        best = gt.loc[gt["p_value"].idxmin()]
        granger_rows.append({"driver": col, "best_lag": int(best["lag"]),
                             "f_stat": float(best["f_stat"]), "p_value": float(best["p_value"]),
                             "n": int(best["n"])})
granger = pd.DataFrame(granger_rows).sort_values("p_value")
print(granger.to_string(index=False))
granger.to_csv(f"{REPORTS}/granger.csv", index=False)
print()
print("Granger gives predictive precedence, not causation. These read as 'precedes'.")

# %% [markdown]
# ## Regime split at conflict onset
#
# A break is half a finding until it says whether the mean or the variance moved.

# %%
from src.stats.diagnostics import structural_break

brk = structural_break(df[TARGET], CONFLICT_ONSET)
for k, v in brk.items():
    print(f"{k:>14}: {v}")
print()
print("WHAT MOVED:", brk["what_moved"])
with open(f"{REPORTS}/regime_split.json", "w") as fh:
    json.dump(brk, fh, indent=2)

# %%
pre = df[df.index < CONFLICT_ONSET]
post = df[df.index >= CONFLICT_ONSET]
print(f"pre-onset  n={len(pre)}   post-onset n={len(post)}")
print()
comp = pd.DataFrame({
    "pre_mean": pre[DRIVERS + [TARGET]].mean(),
    "post_mean": post[DRIVERS + [TARGET]].mean(),
    "pre_std": pre[DRIVERS + [TARGET]].std(),
    "post_std": post[DRIVERS + [TARGET]].std(),
})
comp["std_ratio"] = (comp["post_std"] / comp["pre_std"]).round(3)
print(comp.round(5).to_string())
comp.to_csv(f"{REPORTS}/regime_comparison.csv")

# %%
fig, axes = plt.subplots(1, 2, figsize=(9, 3))
axes[0].plot(df.index, df[TARGET], lw=.6)
axes[0].axvline(CONFLICT_ONSET, color="crimson", ls="--")
axes[0].set_title(TARGET + " with regime boundary")
axes[1].hist(pre[TARGET].dropna(), bins=40, alpha=.6, label="pre", density=True)
axes[1].hist(post[TARGET].dropna(), bins=40, alpha=.6, label="post", density=True)
axes[1].legend(fontsize=7)
axes[1].set_title("distribution by regime")
plt.tight_layout()

# %% [markdown]
# ## Ranked drivers
#
# Every row carries direction, magnitude, lag and a p-value. Three of four is not
# a result.

# %%
from src.stats.diagnostics import driver_ranking

ranking = driver_ranking(df[DRIVERS], df[TARGET], max_lag=7)
print(ranking.to_string(index=False))
ranking.to_csv(f"{REPORTS}/driver_ranking.csv", index=False)

# %%
if len(ranking):
    fig, ax = plt.subplots(figsize=(7, 3))
    colours = ["#c44" if d == "positive" else "#468" for d in ranking["direction"]]
    ax.barh(ranking["driver"], ranking["magnitude"], color=colours)
    ax.axvline(float(ranking["band"].iloc[0]), ls="--", c="k", lw=.8)
    ax.set_xlabel("absolute ccf at best lead lag; dashed line is the significance band")
    ax.set_title("ranked drivers, red = positive direction")
    plt.tight_layout()

    for _, r in ranking.iterrows():
        verdict = "supports a forecast" if r["ccf_significant"] else "within noise"
        print(f"{r['driver']:<28} lag {int(r['best_lead_lag']):+d}  "
              f"{r['direction']:<8} magnitude {float(r['magnitude']):.4f}  "
              f"granger p {r['granger_min_p']}  -> {verdict}")

# %% [markdown]
# ## Summary

# %%
lines = ["EDA SUMMARY", "=" * 70, ""]
if len(ranking):
    top = ranking.iloc[0]
    lines.append("Top driver: " + str(top["driver"]) + " at lag "
                 + str(int(top["best_lead_lag"])) + ", " + str(top["direction"])
                 + ", magnitude " + str(top["magnitude"])
                 + ", granger p " + str(top["granger_min_p"]))
else:
    lines.append("No driver produced a usable lead relationship.")
lines.append("Stationarity: " + str(len(disagree)) + " of " + str(len(stat)) + " series give an ADF/KPSS disagreement")
lines.append("Significance: " + str(n_sig) + " of " + str(len(sig)) + " drivers clear the band")
lines.append("Regime break at onset: " + brk["what_moved"])
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
