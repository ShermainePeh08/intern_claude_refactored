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
- Sample window: 2025-01-14 to present. **Conflict onset: 2026-03-16.**
- Forecast test block opens **2026-02-24**. Nothing at or after that date informs
  a training fit.
- Audience: strategic analysts. Feature interpretation matters more than
  point-forecast accuracy. A well-explained null result is a good deliverable;
  an unexplained positive one is not.

The onset is a single date rather than a month because the regime tests split on
it, and a fortnight either way can change the verdict. If it is revised, re-run
the break test in Section 4 and quote the date alongside the finding.

## 2. Where things live

| What | Path |
| --- | --- |
| Raw, never modified | `datasets/raw/` |
| Cleaned intermediates | `datasets/interim/` |
| Analysis-ready | `datasets/processed/master_daily.csv`, `master_weekly.csv` |
| Notebooks | `notebooks/NN_name.ipynb` |
| Written results | `results/reports/` (`.txt`, `.csv`, `.json`) |
| Figures | inline in the notebook |
| Machine-readable metrics | `results/metrics/*.json` |
| Helper code | `src/` |

`src/` already holds the splitter, the Diebold-Mariano test, the publication-lag
join and the diagnostics. Read it before writing new versions of any of them.

## 3. Data grain

- ACLED conflict variables are **weekly**. They live in `master_weekly.csv`.
- Price, VIX and rhetoric variables are **daily**. They live in `master_daily.csv`.
- `master_daily.csv` contains forward-filled conflict columns. On roughly four of
  every five trading days those values are a copy of Tuesday's and cannot move
  while price does.
- Use the daily file for daily-frequency work and the weekly file for inference
  about ACLED. The forward-filled columns exist for plotting and alignment, not
  for computing a p-value.
- **Publication lag.** ACLED publishes a week on the following Tuesday. A weekly
  value must be attached to daily rows from its publication date, not from the
  Monday the week began. Attaching it earlier is lookahead leakage introduced
  during the merge, where no train/test split will catch it.
  `src/data/loaders.attach_weekly` applies the anchor; do not write your own.
- Any statistic computed on a forward-filled conflict column at daily frequency
  must be reported with an explicit note that the effective sample is the number
  of **update events**, not the number of rows. Roughly 380 daily rows carry
  about 75 weekly observations, so a standard error computed on the row count is
  too small by about the square root of the fill factor.
- `hormuz_severity_delta` loses its information content under weekly aggregation.
  Use the daily series for Hormuz and the weekly series for ACLED, and say so.

## 4. What must be checked before any model is fitted

- ADF **and** KPSS on every series entering a model. Report both; where they
  disagree, say what the disagreement implies rather than picking the convenient
  one.
- A naive random-walk benchmark is mandatory. No model result is reportable
  without it, and it belongs on the first row of the results table.
- A benchmark comparison is settled by a **Diebold-Mariano test**, not by an RMSE
  difference. State the sign convention in the output: DM > 0 means the model has
  higher loss than the benchmark, so the model is worse.
- Train/test splits are chronological with a purge gap at least as long as the
  longest feature lookback. No shuffling, ever. Scalers and imputers are fitted
  inside the fold, never once on the full frame.
- Every reported relationship carries four things: direction, magnitude, lag, and
  a p-value or confidence interval.
- Multicollinearity: report VIF or a correlation matrix for any feature set of
  more than three variables.
- Report the origin count beside every comparison. Below about twenty origins a
  DM test cannot separate a real edge from luck in either direction, so a null
  there is weak evidence rather than evidence of no effect.

## 5. Known traps in this data

- `acled_fatalities` is the first print; `acled_fatalities_revised` is the later
  correction and is always higher. Using the revised column as a feature uses a
  number nobody had at the time. A negative coefficient on a fatalities z-score
  is more likely a reporting artefact than an economic finding.
- `hormuz_severity` is hand-assigned with no objective boundary between levels.
  Any result depending on it inherits that subjectivity and must say so.
- Nothing else that moves oil is in this dataset — inventories, dollar strength,
  demand. "The conflict caused X" is unsupported here. "Volatility rose during
  the conflict period" is supported. Use the second phrasing.

## 6. When the data is wrong

Report it. Do not repair it silently, do not drop rows to make a test pass, and
do not substitute a different variable because the requested one is awkward.
Write what you found to `results/reports/` and stop for instruction.

## 7. How to finish

- The deliverable is a notebook under `notebooks/`, with plots rendered inline.
  Not a `.py` file plus a folder of PNGs, and not a notebook whose figures are
  written to disk and linked.
- Every numeric result shown in a notebook must also be written to a file under
  `results/`, so it survives the session.
- State the effective sample behind any figure derived from a forward-filled
  column, in the same sentence as the figure.
- Close with a short "what this does and does not show" paragraph. State at least
  one limitation genuinely present in the work — not a generic caveat about
  sample size, but the specific thing this analysis could not settle.