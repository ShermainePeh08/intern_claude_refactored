---
description: Run the full Stage-1 exploratory pipeline and write the report
---

# Stage 1 — Exploratory analysis

Run in order. Do not restate the standards in your own words; the rule files and
the agent files already carry them.

1. Confirm `datasets/processed/master_daily.csv` and `master_weekly.csv` exist and
   report the last date in each. If either is missing, say so and stop — do not
   analyse data that is not there, and do not regenerate it without being asked.

2. Use the `data-prep` subagent. It owns the profiling, the grain report, the
   publication-date anchor and the effective sample size. Do not restate its
   procedure in your prompt to it; that is what its file is for.

3. If `data-prep` reports anything malformed, stop and report it. Do not continue
   into analysis on data that has just been flagged.

4. Use the `eda-explorer` subagent. It owns stationarity, the lag structure, the
   VIF, the regime split and the ranked driver table.

5. When it returns, working only from the two agents' summaries and the files
   they wrote, assemble `notebooks/02_eda_correlation.ipynb`:
   - the data profile, with effective sample size beside row count for every
     forward-filled series
   - the ADF/KPSS table with statistic, p-value and lag order for both tests
   - cross-correlation plots with the significance band, and the sign convention
     stated in text above them
   - the VIF table
   - the regime split, saying whether the mean or the variance moved
   - the ranked driver table: driver, lag, direction, magnitude, p-value

6. Close with the headline in one sentence, and a second sentence naming the
   strongest claim the data does **not** support.

7. Confirm every number in the notebook also appears in a file under
   `results/reports/`.

Deliver plots inline in the notebook. Do not write a `.py` script alongside it and
do not dump figures to `results/figures/`.
