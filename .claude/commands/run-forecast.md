---
description: Run the full Stage-2 forecasting pipeline and audit it
---

# Stage 2 — Forecasting

Run in order.

1. Confirm Stage 1 has been run in this repository: `results/reports/` should
   contain `data_audit.txt`, `stationarity.csv` and `driver_ranking.csv`. If any
   is missing, say so and stop — do not forecast on data that has not been
   profiled.

2. Use the `feature-engineer` subagent. It owns the model frame, the lags and the
   leakage check. Note the longest lookback it reports; the purge gap in step 3
   must be at least that long.

3. Use the `forecast-builder` subagent. It owns the split, the benchmark, the
   roster and the Diebold-Mariano comparison. Do not restate the harness design
   in your prompt to it; that is what its file is for.

4. Use the `feature-importance` subagent on the fitted models. It owns the
   coefficients and their stability across refits.

5. Use the `backtest-auditor` subagent on the harness. Wait for the verdict.

6. If the auditor returns `FAIL`, report the blockers and stop. Do not present
   results from a harness that failed audit, and do not patch the harness
   yourself — re-invoke `forecast-builder` with the blockers named.

7. If the verdict is `PASS` or `PASS WITH NOTES`, working only from the returned
   summaries, write the results section into
   `notebooks/05_forecast_walkforward.ipynb`:
   - the model comparison table with RMSE in both unit systems, R-squared,
     directional accuracy, DM statistic and p-value
   - the naive benchmark on the first row, always
   - the conflict versus non-conflict split
   - the audit verdict reproduced verbatim, including the `UNCHECKED` line

8. Close with the headline in one sentence. If nothing beat the benchmark, the
   headline says so.

9. Confirm `results/metrics/forecast_results.json` exists and its numbers match
   the notebook.

Deliver plots inline in the notebook. Do not write a `.py` script alongside it and
do not dump figures to `results/figures/`.
