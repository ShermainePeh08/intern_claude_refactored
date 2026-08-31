# feature-engineer — L5-FC-01

Construction of the model frame. Every transform here is trailing-only: a single
centred window or negative shift invalidates everything downstream of it.

## Feature frame

70 features across 14 base variables; lags [1, 2, 3, 5, 10].

| base | n_features |
|---|---|
| acled_events | 5 |
| acled_events_z21 | 5 |
| acled_fatalities | 5 |
| acled_fatalities_revised | 5 |
| acled_fatalities_revised_z21 | 5 |
| acled_fatalities_z21 | 5 |
| hormuz_severity | 5 |
| hormuz_severity_z21 | 5 |
| realised_return | 5 |
| rhetoric_index | 5 |
| rhetoric_index_z21 | 5 |
| rv21 | 5 |

Sample of the dictionary:

| feature | base | lag | mean | std | nulls |
|---|---|---|---|---|---|
| realised_return_lag1 | realised_return | 1 | -3.2e-05 | 0.015377 | 0 |
| realised_return_lag2 | realised_return | 2 | -0.000114 | 0.015172 | 0 |
| realised_return_lag3 | realised_return | 3 | 0.000107 | 0.015312 | 0 |
| realised_return_lag5 | realised_return | 5 | 0.00013 | 0.015011 | 0 |
| realised_return_lag10 | realised_return | 10 | 0.000603 | 0.015161 | 0 |
| rv21_lag1 | rv21 | 1 | 0.014017 | 0.005359 | 0 |
| rv21_lag2 | rv21 | 2 | 0.013983 | 0.005342 | 0 |
| rv21_lag3 | rv21 | 3 | 0.013954 | 0.005326 | 0 |

Longest lag is 10 rows. Rolling statistics extend the lookback
further, which is what the purge gap downstream has to cover.

## Scope

- Scaling and imputation are not done here. They live inside the model pipeline
  so they refit per fold; fitting them on the full frame is leakage even when
  the split is correct.
- No feature selection on target correlation over the full sample.

## Checked

- feature dictionary written with base variable and lag per feature
- positive lags only; no negative shift


---
