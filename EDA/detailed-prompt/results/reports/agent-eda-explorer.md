# eda-explorer — L4-EDA-02

Stage-1 exploratory report. The remit is to make it impossible to name a
driver without its lag, direction, magnitude and p-value attached.

## Stationarity

ADF and KPSS on 9 series. 0 disagreement(s).

| column | adf_p | adf_lag | kpss_p | kpss_lag | verdict |
|---|---|---|---|---|---|
| log_return | 0.0 | 0 | 0.1 | 2 | stationary (both agree) |
| brent_close | 0.9158 | 0 | 0.0358 | 11 | non-stationary (both agree) |
| realised_return | 0.0 | 0 | 0.1 | 2 | stationary (both agree) |
| acled_events | 0.6121 | 5 | 0.01 | 11 | non-stationary (both agree) |
| acled_fatalities | 0.9372 | 15 | 0.01 | 11 | non-stationary (both agree) |
| acled_fatalities_revised | 0.8992 | 15 | 0.01 | 11 | non-stationary (both agree) |
| hormuz_severity | 0.6981 | 15 | 0.01 | 11 | non-stationary (both agree) |
| rhetoric_index | 0.2831 | 9 | 0.01 | 10 | non-stationary (both agree) |

## Significance

3 of 6 drivers clear the 1.96/sqrt(N) band.

| driver | pearson_r | pearson_p | spearman_rho | significant | n |
|---|---|---|---|---|---|
| acled_events | 0.163 | 0.0014 | 0.103 | True | 381 |
| acled_fatalities_revised | 0.1627 | 0.0014 | 0.0671 | True | 381 |
| acled_fatalities | 0.1537 | 0.0026 | 0.0543 | True | 381 |
| hormuz_severity | 0.0806 | 0.1161 | 0.0551 | False | 381 |
| rhetoric_index | 0.0411 | 0.4235 | -0.0126 | False | 381 |
| tanker_rate_usd | -0.0214 | 0.6772 | -0.0395 | False | 381 |

## Lag structure

Cross-correlation over lags -7 to +7 with the significance band. A positive
lag means the driver moved first; a spike at lag 0 is co-movement and
supports no forecast.

Granger, smallest p-value across the tested lags:

| driver | best_lag | f_stat | p_value | n |
|---|---|---|---|---|
| acled_fatalities_revised | 1 | 8.9728 | 0.0029 | 381 |
| acled_fatalities | 2 | 5.8634 | 0.0031 | 381 |
| acled_events | 1 | 7.3623 | 0.007 | 381 |
| rhetoric_index | 1 | 4.7141 | 0.0305 | 381 |
| hormuz_severity | 3 | 2.7642 | 0.0418 | 381 |
| tanker_rate_usd | 2 | 1.7796 | 0.1701 | 381 |

These read as *precedes*. Nothing here licenses the word *causes*.

## Multicollinearity

| feature | vif |
|---|---|
| acled_fatalities_revised | 58.503 |
| acled_fatalities | 44.543 |
| acled_events | 12.154 |
| hormuz_severity | 2.348 |
| rhetoric_index | 1.528 |
| tanker_rate_usd | 1.055 |

3 driver(s) exceed a VIF of 5 and are largely reconstructible from the rest of the set; only one of any collinear pair should enter a model.

## Regime split

Boundary 2026-03-16; 305 observations before, 76 after.

- Welch p (mean): `0.0415`
- Levene p (variance): `0.0`
- **What moved: mean and variance**

Mean and variance shifts are different findings. For this project the
variance answer is usually the substantive one: conflict periods look like
volatility events rather than directional ones.

## Sensitivity to the boundary date

The verdict was recomputed across a six-week window: 2 distinct outcome(s).

| offset_days | date | welch_p | levene_p | what_moved |
|---|---|---|---|---|
| -21 | 2026-02-23 | 0.0285 | 0.0 | mean and variance |
| -14 | 2026-03-02 | 0.0494 | 0.0 | mean and variance |
| -7 | 2026-03-09 | 0.0657 | 0.0 | variance |
| 0 | 2026-03-16 | 0.0415 | 0.0 | mean and variance |
| 7 | 2026-03-23 | 0.0694 | 0.0 | variance |
| 14 | 2026-03-30 | 0.1756 | 0.0 | variance |
| 21 | 2026-04-06 | 0.2267 | 0.0 | variance |

The verdict moves with the boundary, so it should be quoted with the date
attached rather than as a property of the series.

## Ranked drivers

| driver | best_lead_lag | direction | magnitude | ccf_significant | granger_min_p | n |
|---|---|---|---|---|---|---|
| acled_fatalities_revised | 2 | positive | 0.1621 | True | 0.0029 | 381 |
| acled_events | 6 | positive | 0.1584 | True | 0.007 | 381 |
| acled_fatalities | 3 | positive | 0.1533 | True | 0.0031 | 381 |
| hormuz_severity | 3 | positive | 0.1402 | True | 0.0418 | 381 |
| rhetoric_index | 1 | positive | 0.1116 | True | 0.0305 | 381 |
| tanker_rate_usd | 6 | negative | 0.0544 | False | 0.1701 | 381 |

Strongest lead relationship: **acled_fatalities_revised** at lag `+2`, positive, magnitude `0.1621`.

## Scope

- No causal claim is made. Inventories, dollar strength and demand are absent
  from the dataset, so the supportable phrasing is that volatility rose during
  the conflict period, not that the conflict caused the move.
- Broken data would be reported and left alone, not repaired.
- A null result on a driver the project cares about is reported as the finding.

## Checked

- stationarity tested with both ADF and KPSS before modelling
- every reported relationship carries a p-value
- lag analysis with an explicit sign convention
- multicollinearity checked
- regime split reports which moment moved
- regime verdict tested for sensitivity to the onset date
- ranking carries direction, magnitude, lag and p-value

## Not checked

- effective sample size was not established upstream, so the sample sizes below are row counts and are optimistic for forward-filled variables


---
