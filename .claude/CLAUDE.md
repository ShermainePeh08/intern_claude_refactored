# Brent Crude × Geopolitical Risk — Project Brief

<!-- Loaded automatically into every session in this repository.
     Goal: keep under ~200 lines. Every line here is paid for on every turn.
     Bulk reference material belongs in datasets/processed/feature_dictionary.md,
     which is read on demand instead. -->

## 1. The objective

Explain and, where possible, forecast movements in Brent crude spot prices during
the Iran–US conflict period, using conflict events, Strait of Hormuz status, and
political rhetoric as candidate drivers.

- Target variable: `log_return` = log(P_t+1 / P_t). Never model price levels.
- Sample window: 2025-01-14 to present. Conflict onset: 2026-02.
- Audience: strategic analysts. Feature interpretation matters more than
  point-forecast accuracy. A well-explained null result is a good deliverable;
  an unexplained positive one is not.

## 2. Where things live

| What | Path |
| --- | --- |
| Raw, never modified | `datasets/raw/` |
| Cleaned intermediates | `datasets/interim/` |
| Analysis-ready | `datasets/processed/master_daily.csv`, `master_weekly.csv` |
| Notebooks | `notebooks/NN_name.ipynb` |
| Written results | `results/reports/*.txt` |
| Figures | `results/figures/*.png` |
| Machine-readable metrics | `results/metrics/*.json` |
| Helper code | `src/` |

## 3. Data grain

- ACLED conflict variables are **weekly**. They live in `master_weekly.csv`.
- Price, VIX and rhetoric variables are **daily**. They live in `master_daily.csv`.
- `master_daily.csv` contains forward-filled conflict columns. On roughly four of
  every five trading days those values are a copy of Tuesday's and cannot move
  while price does.
- Never merge daily and weekly data into one frame for inference.
- Any statistic computed on a forward-filled conflict column at daily frequency
  must be reported with an explicit note that the effective sample is the number
  of **update events**, not the number of rows.
- `hormuz_severity_delta` loses its information content under weekly aggregation.
  Use the daily series for Hormuz and the weekly series for ACLED, and say so.

## 4. What must be checked before any model is fitted

- ADF **and** KPSS on every series entering a model. Report both; where they
  disagree, say what the disagreement implies rather than picking the convenient
  one.
- A naive random-walk benchmark is mandatory. No model result is reportable
  without it.
- Train/test splits are chronological with a purge gap. No shuffling, ever.
- Every reported relationship carries four things: direction, magnitude, lag, and
  a p-value or confidence interval.
- Multicollinearity: report VIF or a correlation matrix for any feature set of
  more than three variables.

## 5. When the data is wrong

Report it. Do not repair it silently, do not drop rows to make a test pass, and
do not substitute a different variable because the requested one is awkward.
Write what you found to `results/reports/` and stop for instruction.

## 6. How to finish

- The deliverable is a notebook under `notebooks/`, with plots rendered inline.
  Not a `.py` file plus a folder of PNGs.
- Every numeric result shown in a notebook must also be written to a file under
  `results/`, so it survives the session.
- Close with a short "what this does and does not show" paragraph. State at least
  one limitation that is genuinely present in the work.