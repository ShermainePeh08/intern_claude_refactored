# forecast-builder — L5-FC-01

Stage-2 harness and scored comparison. The remit is to make it impossible to
report a model result without the benchmark beside it.

## Design

- Horizons: [np.int64(1), np.int64(5)], direct rather than recursive
- Models: naive_random_walk, drift, elasticnet, random_forest, gradient_boosting
- Origins per model: [72]
- Chronological expanding origins with a purge gap; no shuffle, no KFold

## Results

| model | horizon | n | rmse_logret | rmse_usd | r2 | diracc | cv_rmse |
|---|---|---|---|---|---|---|---|
| naive_random_walk | 1 | 72 | 0.022213 | 1.9276 | -0.0204 | 0.0 | nan |
| drift | 1 | 72 | 0.022352 | 1.9386 | -0.0333 | 0.4306 | nan |
| elasticnet | 1 | 72 | 0.022342 | 1.9377 | -0.0324 | 0.4583 | 0.011940309901829784 |
| random_forest | 1 | 72 | 0.022308 | 1.9354 | -0.0292 | 0.5 | 0.011790089564953624 |
| gradient_boosting | 1 | 72 | 0.023096 | 2.014 | -0.1032 | 0.5417 | 0.01212336877646196 |
| naive_random_walk | 5 | 72 | 0.046083 | 3.8572 | -0.1592 | 0.0 | nan |
| drift | 5 | 72 | 0.047526 | 3.9679 | -0.233 | 0.4444 | nan |
| elasticnet | 5 | 72 | 0.047552 | 3.9705 | -0.2343 | 0.4583 | 0.03079757970816942 |
| random_forest | 5 | 72 | 0.049874 | 4.1518 | -0.3578 | 0.3333 | 0.02925341051395767 |
| gradient_boosting | 5 | 72 | 0.048882 | 4.0758 | -0.3043 | 0.4028 | 0.03283194417335337 |

- h=1 `drift`: +0.63% RMSE against the benchmark
- h=1 `elasticnet`: +0.58% RMSE against the benchmark
- h=1 `random_forest`: +0.43% RMSE against the benchmark
- h=1 `gradient_boosting`: +3.98% RMSE against the benchmark
- h=5 `drift`: +3.13% RMSE against the benchmark
- h=5 `elasticnet`: +3.19% RMSE against the benchmark
- h=5 `random_forest`: +8.23% RMSE against the benchmark
- h=5 `gradient_boosting`: +6.07% RMSE against the benchmark

## Diebold-Mariano

DM > 0 means the model has higher loss than the benchmark, so the model is
worse. DM < 0 means better. The p-value is two-sided.

| model | horizon | n | dm_stat | dm_pvalue | verdict |
|---|---|---|---|---|---|
| drift | 1 | 72 | 1.621 | 0.1095 | no significant difference from benchmark |
| elasticnet | 1 | 72 | 1.5047 | 0.1368 | no significant difference from benchmark |
| random_forest | 1 | 72 | 0.2925 | 0.7708 | no significant difference from benchmark |
| gradient_boosting | 1 | 72 | 1.0525 | 0.2961 | no significant difference from benchmark |
| drift | 5 | 72 | 1.4035 | 0.1648 | no significant difference from benchmark |
| elasticnet | 5 | 72 | 1.4375 | 0.155 | no significant difference from benchmark |
| random_forest | 5 | 72 | 1.7147 | 0.0908 | no significant difference from benchmark |
| gradient_boosting | 5 | 72 | 2.0617 | 0.0429 | model loses to benchmark |

**Headline: nothing beat the naive random walk at the 5% level.**

## By regime

| model | horizon | regime | n | rmse_logret | dm_stat | dm_pvalue |
|---|---|---|---|---|---|---|
| naive_random_walk | 1 | conflict | 58 | 0.02361 | nan | nan |
| naive_random_walk | 1 | non_conflict | 14 | 0.015104 | nan | nan |
| drift | 1 | conflict | 58 | 0.023751 | 1.541 | 0.1288 |
| drift | 1 | non_conflict | 14 | 0.015251 | 0.5132 | 0.6164 |
| elasticnet | 1 | conflict | 58 | 0.023739 | 1.4389 | 0.1556 |
| elasticnet | 1 | non_conflict | 14 | 0.015245 | 0.47 | 0.6461 |
| random_forest | 1 | conflict | 58 | 0.023741 | 0.3674 | 0.7147 |
| random_forest | 1 | non_conflict | 14 | 0.01498 | -0.1301 | 0.8985 |
| gradient_boosting | 1 | conflict | 58 | 0.024576 | 0.9953 | 0.3238 |
| gradient_boosting | 1 | non_conflict | 14 | 0.015531 | 0.448 | 0.6615 |
| naive_random_walk | 5 | conflict | 58 | 0.049414 | nan | nan |
| naive_random_walk | 5 | non_conflict | 14 | 0.028383 | nan | nan |

The smaller slice holds 14 origins. A comparison at that size is
descriptive, not a test.

## Tuning

Randomised search on blocked time-series cross-validation with a purge gap.
The CV score sits next to the test score above.

## Scope

- The ranking is an output, not a decision. No model was selected on test-set
  performance and then presented as if chosen in advance.
- No model is described as beating the benchmark unless the test says so.
- If every model loses to the naive random walk, that is the result.

## Checked

- every model scored on an identical set of origins
- naive benchmark fitted and scored before the roster
- error reported in log-return units and in USD/bbl from the same predictions
- benchmark comparison decided by a test, not by an RMSE difference
- test block scored separately for conflict and non-conflict
- hyperparameters tuned on time-aware cross-validation


---
