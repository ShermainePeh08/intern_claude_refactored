# %% [markdown]
# # Stage 2b — Forecasting Brent returns
#
# Target: next-step log return, log(P_t+1 / P_t), converted back to a price for
# reporting with P_hat = P_t * exp(y_hat).

# %%
import json
import os
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")
pd.set_option("display.width", 150)
pd.set_option("display.max_columns", 60)

REPORTS, METRICS, PROCESSED = "results/reports", "results/metrics", "datasets/processed"
for d in (REPORTS, METRICS):
    os.makedirs(d, exist_ok=True)

from src.data.loaders import attach_weekly
from src.features.build import build_feature_frame

TEST_START = pd.Timestamp("2026-02-24")
CONFLICT_ONSET = pd.Timestamp("2026-03-16")
LAGS = [1, 2, 3, 5, 10]

# %%
HORIZONS = (1,)
MODEL_KEYS = ['elasticnet', 'random_forest']
N_ITER = 6
REFIT_ORIGINS = 5
USE_REGIME = False
print("horizons", HORIZONS, " roster", MODEL_KEYS)

# %% [markdown]
# ## Load the model frame
#
# Built by `04_feature_build.py`. Rebuilt here if that has not been run, so this
# notebook is runnable on its own.

# %%
frame_path = f"{PROCESSED}/model_frame.csv"
if os.path.exists(frame_path):
    frame = pd.read_csv(frame_path, parse_dates=["date"]).set_index("date")
    ycols = [c for c in frame.columns if c.startswith("h") and c[1:].isdigit()]
    X, y = frame.drop(columns=ycols), frame[ycols]
    print("loaded", frame_path, frame.shape)
else:
    daily = pd.read_csv(f"{PROCESSED}/master_daily.csv", parse_dates=["date"]).set_index("date").sort_index()
    weekly = pd.read_csv(f"{PROCESSED}/master_weekly.csv", parse_dates=["week_start"]).set_index("week_start").sort_index()
    merged = attach_weekly(daily, weekly).drop(columns=["published_on"], errors="ignore")
    merged = merged.select_dtypes("number").ffill().dropna()
    X, y = build_feature_frame(merged, price_col="brent_close", lags=LAGS, horizons=HORIZONS)
    print("rebuilt feature frame", X.shape)

daily_px = pd.read_csv(f"{PROCESSED}/master_daily.csv", parse_dates=["date"]).set_index("date").sort_index()
price = daily_px["brent_close"].reindex(X.index)
regime = pd.Series(X.index >= CONFLICT_ONSET, index=X.index)
REGIME_MASK = regime if USE_REGIME else None

print("lags used:", LAGS)
print("X", X.shape, " targets", list(y.columns))
print("conflict share of the sample:", round(float(regime.mean()), 3))

# %% [markdown]
# ## Walk-forward split
#
# Chronological expanding origins with a purge gap between the end of training
# and the forecast origin. No shuffle, no KFold, no train_test_split. Every
# model, benchmarks included, is scored on the same origins.

# %%
from src.models.walkforward import SplitSpec, build_results_table, run_walk_forward

spec_preview = SplitSpec(test_start=TEST_START, purge=10, min_train=120, horizon=1)
origins = spec_preview.origins(X.index)
train_end = spec_preview.train_slice(X.index, origins[0])[-1]
print(f"{len(origins)} forecast origins, {origins[0].date()} .. {origins[-1].date()}")
print("training begins", X.index[0].date(), " first training block ends", train_end.date())
print("purge gap:", spec_preview.purge, "trading days")
print("origins in the conflict regime:", int(regime.reindex(origins).sum()),
      " outside:", int((~regime.reindex(origins)).sum()))

# %%
fig, ax = plt.subplots(figsize=(9, 2.2))
ax.plot(price.index, price, lw=.8, color="#678")
ax.axvspan(X.index[0], train_end, alpha=.15, color="tab:blue", label="training")
ax.axvspan(train_end, origins[0], alpha=.3, color="tab:red", label="purge gap")
ax.axvspan(origins[0], origins[-1], alpha=.15, color="tab:green", label="test origins")
ax.axvline(CONFLICT_ONSET, color="crimson", ls="--", lw=.8)
ax.legend(fontsize=7, ncol=3)
ax.set_title("walk-forward layout")
plt.tight_layout()

# %% [markdown]
# ## Fit
#
# Benchmarks first: the naive random walk and the drift model are fitted and
# scored before anything else in the roster. Each roster model is tuned by
# randomised search on blocked time-series cross-validation with a purge gap, and
# the CV score is reported next to the test score.

# %%
from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit
from src.models.roster import ROSTER, simplest_setting

# Trim the tree search spaces: the walk-forward loop refits at every origin, so a
# 800-tree grid multiplies out into thousands of fits for no gain at this sample
# size. The search itself is unchanged.
if "random_forest" in ROSTER:
    ROSTER["random_forest"]["param_dist"]["est__n_estimators"] = [60, 120]
if "gradient_boosting" in ROSTER:
    ROSTER["gradient_boosting"]["param_dist"]["est__n_estimators"] = [60, 120]

for k in MODEL_KEYS:
    print(k, "->", ROSTER[k]["param_dist"])
print()
print("cv:", TimeSeriesSplit(n_splits=5, gap=10), " n_iter:", N_ITER)
print()
print(f"estimators are refitted every {REFIT_ORIGINS} origins on the expanding window.")
print("Between refits the model is older, never better informed: no model ever")
print("sees data past its own forecast origin, and the scored origins are unchanged.")

# %%
records = []
cv_notes = []
for h in HORIZONS:
    spec = SplitSpec(test_start=TEST_START, purge=10, min_train=120, horizon=h)
    res = run_walk_forward(X, y[f"h{h}"], spec, model_keys=MODEL_KEYS,
                           n_iter=N_ITER, refit_every=10_000,
                           model_refit_every=REFIT_ORIGINS)
    records += build_results_table(res, price, regime_mask=REGIME_MASK)
    for r in res:
        if r.cv_score is not None:
            cv_notes.append({"model": r.model, "horizon": h, "cv_rmse": round(r.cv_score, 6),
                             "picked_simplest": r.picked_simplest, "params": r.best_params})
            print(f"h={h} {r.model:<20} cv_rmse={r.cv_score:.6f} "
                  f"simplest={r.picked_simplest} {r.best_params}")
    globals()["last_res"] = res

print()
print(len(records), "result records")
simplest_count = sum(1 for c in cv_notes if c["picked_simplest"])
print(f"{simplest_count} of {len(cv_notes)} tuned fits chose the most-regularised setting on offer.")
if simplest_count:
    print("That is cross-validation saying the added complexity is not paying for")
    print("itself. It is a finding, not a footnote.")

# %% [markdown]
# ## Model comparison
#
# The benchmark sits on the first row. RMSE is reported in log-return units and
# in USD/bbl, derived from the same predictions, because rankings can differ
# between the two.

# %%
table = pd.DataFrame([r for r in records if r.get("regime") == "all"])
cols = [c for c in ["model", "horizon", "n", "rmse_logret", "rmse_usd", "mae_logret",
                    "r2", "diracc", "cv_rmse", "dm_stat", "dm_pvalue", "verdict"]
        if c in table.columns]
table = table[cols]
print(table.to_string(index=False))

# %%
for h in sorted(table["horizon"].unique()):
    sub = table[table["horizon"] == h]
    print()
    print(f"--- horizon h={h} ---")
    print(sub[[c for c in ["model", "n", "rmse_logret", "rmse_usd", "r2", "diracc"] if c in sub.columns]]
          .to_string(index=False))
    bench = sub[sub["model"] == "naive_random_walk"]
    if len(bench):
        b = float(bench["rmse_logret"].iloc[0])
        for _, r in sub.iterrows():
            delta = 100 * (float(r["rmse_logret"]) - b) / b
            print(f"  {r['model']:<20} {delta:+.2f}% RMSE vs the benchmark")

# %%
fig, ax = plt.subplots(figsize=(7, 3))
piv = table.pivot_table(index="model", columns="horizon", values="rmse_logret")
piv.plot(kind="bar", ax=ax)
ax.set_ylabel("RMSE (log return)")
ax.set_title("error by model and horizon")
plt.tight_layout()

# %% [markdown]
# ## Diebold-Mariano against the naive benchmark
#
# An RMSE difference is not a result. The sign convention is stated so the
# verdict cannot be read backwards.

# %%
from src.stats.tests import SIGN_CONVENTION

print(SIGN_CONVENTION)
print()
dm = table[table["model"] != "naive_random_walk"]
print(dm[[c for c in ["model", "horizon", "n", "dm_stat", "dm_pvalue", "verdict"] if c in dm.columns]]
      .to_string(index=False))

beat = [r for r in records if r.get("regime") == "all" and r.get("dm_pvalue") is not None
        and r["dm_pvalue"] < 0.05 and (r.get("dm_stat") or 0) < 0]
HEADLINE = ("Nothing beat the naive random walk at the 5% level."
            if not beat else f"{len(beat)} model-horizon combination(s) beat the benchmark.")
print()
print("HEADLINE:", HEADLINE)

underpowered = [r for r in records if r.get("regime") == "all"
                and isinstance(r.get("n_origins"), int) and r["n_origins"] < 20]
if underpowered:
    print()
    print(f"{len(underpowered)} comparison(s) run on fewer than 20 origins. A DM test on")
    print("that few cannot separate a real edge from luck in either direction.")

# %% [markdown]
# ## Residual diagnostics
#
# A model can post a respectable RMSE and still be misspecified. These check that
# the errors look like noise rather than like structure the model missed.

# %%
from statsmodels.stats.diagnostic import acorr_ljungbox

res_obj = globals().get("last_res")
if res_obj:
    target_model = [r for r in res_obj if r.model not in ("naive_random_walk", "drift")]
    if target_model:
        r0 = target_model[0]
        resid = (r0.actuals - r0.predictions).dropna()
        print("model:", r0.model, " residuals:", len(resid))
        print("mean", round(float(resid.mean()), 6), " std", round(float(resid.std()), 6))
        print("skew", round(float(resid.skew()), 4), " kurtosis", round(float(resid.kurtosis()), 4))
        lb = acorr_ljungbox(resid, lags=[5, 10], return_df=True)
        print()
        print("Ljung-Box on residuals (low p = leftover autocorrelation):")
        print(lb.round(4).to_string())

        fig, axes = plt.subplots(1, 3, figsize=(11, 3))
        axes[0].plot(resid.index, resid, lw=.7)
        axes[0].axhline(0, c="k", lw=.6)
        axes[0].set_title("residuals over time")
        axes[1].hist(resid, bins=30, color="#678")
        axes[1].set_title("residual distribution")
        axes[2].scatter(r0.predictions.reindex(resid.index), resid, s=10, alpha=.6)
        axes[2].axhline(0, c="k", lw=.6)
        axes[2].set_xlabel("predicted"); axes[2].set_ylabel("residual")
        axes[2].set_title("residual vs fitted")
        plt.tight_layout()

# %%
if res_obj:
    bench = [r for r in res_obj if r.model == "naive_random_walk"][0]
    fig, ax = plt.subplots(figsize=(9, 3))
    ax.plot(bench.actuals.index, bench.actuals, lw=.9, label="actual", color="#333")
    for r in res_obj:
        if r.model != "naive_random_walk":
            ax.plot(r.predictions.index, r.predictions, lw=.8, alpha=.8, label=r.model)
    ax.axhline(0, c="k", lw=.5)
    ax.legend(fontsize=7, ncol=3)
    ax.set_title("predictions against realised log return, test block")
    plt.tight_layout()

# %% [markdown]
# ## Write results

# %%
with open(f"{METRICS}/forecast_results.json", "w") as fh:
    json.dump(records, fh, indent=2, default=str)

with open(f"{REPORTS}/dm_test_results.txt", "w") as fh:
    print("FORECAST RESULTS", file=fh)
    print("=" * 70, file=fh)
    print(file=fh)
    print(table.to_string(index=False), file=fh)
    print(file=fh)
    print(SIGN_CONVENTION, file=fh)
    print(file=fh)
    print("HEADLINE: " + HEADLINE, file=fh)

print("wrote", f"{METRICS}/forecast_results.json", "and", f"{REPORTS}/dm_test_results.txt")
print()
print("records:", len(records),
      " models:", sorted(set(r["model"] for r in records)),
      " regimes:", sorted(set(str(r.get("regime")) for r in records)))
