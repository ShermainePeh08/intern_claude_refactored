paths: datasets/**
description: Sampling-grain contract for the Brent and conflict datasets

# Daily vs. weekly data conventions

Loaded whenever anything under `datasets/` is read or written.

## Which file holds what

- ACLED / conflict variables → `datasets/processed/master_weekly.csv`
- Price, VIX, sentiment, rhetoric → `datasets/processed/master_daily.csv`
- Feature definitions → `datasets/processed/feature_dictionary.md`

## Rules

1. **Never merge daily and weekly data into a single frame for inference.**
   Test each variable at its own native frequency.
2. Conflict columns that appear in `master_daily.csv` are **forward-filled** from
   the Tuesday after the week closes. Treat them as step functions, not as daily
   observations.
3. When reporting any statistic computed on a forward-filled column at daily
   frequency, state the number of distinct **update events** alongside the row
   count. Five rows carrying one fact is one observation, not five.
4. `hormuz_severity_delta` structurally loses information under weekly
   aggregation. Keep Hormuz daily and ACLED weekly, and say which you used.
5. Weeks are Tuesday-anchored, matching ACLED's publication cadence. Do not
   re-anchor to Monday; `src/utils/calendar.py` has the helpers.
6. Never write to `datasets/raw/`. It is the immutable record of what was
   downloaded.

## Output destinations

- Written results → `results/reports/*.txt`
- Figures → `results/figures/*.png`
- Machine-readable metrics → `results/metrics/*.json`
- All notebooks → `notebooks/*.ipynb`