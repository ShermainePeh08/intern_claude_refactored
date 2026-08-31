# data-prep — L4-EDA-02

Boundary between the raw files and anything an analysis touches. Every leakage
bug in this project so far entered during a merge, not during modelling.

## Source profile

```
DATA AUDIT
======================================================================
daily  (382, 3)  2025-01-13 .. 2026-06-30
weekly (77, 4)  2025-01-13 .. 2026-06-29
master_daily.csv
         column   dtype   n  nulls  null_pct  n_unique        min        max
```

## Sampling grain

4 of 7 columns are forward-filled rather than daily.

| column | n_rows | n_update_events | change_rate | grain |
|---|---|---|---|---|
| brent_close | 382 | 381 | 0.997 | daily |
| rhetoric_index | 382 | 381 | 0.997 | daily |
| tanker_rate_usd | 382 | 381 | 0.997 | daily |
| acled_events | 382 | 70 | 0.183 | forward-filled (sub-daily) |
| acled_fatalities | 382 | 71 | 0.186 | forward-filled (sub-daily) |
| acled_fatalities_revised | 382 | 76 | 0.199 | forward-filled (sub-daily) |
| hormuz_severity | 382 | 43 | 0.113 | forward-filled (sub-daily) |

Those columns repeat a value across consecutive rows, so a test run on the
daily row count overstates its own sample size.

## Scope

- Raw data untouched; processed data is rebuilt, never patched.
- `acled_fatalities_revised` is a later correction to `acled_fatalities`. Using
  the revised column as a feature uses a number nobody had at the time.
- Broken data is reported, not repaired.

## Checked

- every source file profiled before use
- grain determined per column rather than assumed

## Not checked

- the publication anchor and effective sample size were not established, so every sample size downstream is a row count and is optimistic


---
