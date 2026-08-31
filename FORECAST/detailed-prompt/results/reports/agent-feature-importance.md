# feature-importance — L4-FC-02

Which features the fitted models actually used, and whether that answer is
stable. An importance ranking computed once is a ranking at one point in time.

## Importances

Kind: coefficient, impurity_importance. Coefficients and impurity importances are not
comparable with each other.

| model | kind | rank | feature | value |
|---|---|---|---|---|
| elasticnet | coefficient | 1 | realised_return_lag1 | 0.0 |
| elasticnet | coefficient | 2 | realised_return_lag2 | 0.0 |
| elasticnet | coefficient | 3 | realised_return_lag3 | 0.0 |
| elasticnet | coefficient | 4 | realised_return_lag5 | 0.0 |
| elasticnet | coefficient | 5 | realised_return_lag10 | 0.0 |
| elasticnet | coefficient | 6 | rv21_lag1 | 0.0 |
| elasticnet | coefficient | 7 | rv21_lag2 | 0.0 |
| elasticnet | coefficient | 8 | rv21_lag3 | 0.0 |
| elasticnet | coefficient | 9 | rv21_lag5 | 0.0 |
| elasticnet | coefficient | 10 | rv21_lag10 | 0.0 |
| elasticnet | coefficient | 11 | rhetoric_index_lag1 | 0.0 |
| elasticnet | coefficient | 12 | rhetoric_index_lag2 | 0.0 |

25 of 60 entries are non-zero. Magnitudes should be read
against the residual scale: a large coefficient on a low-variance feature
moves the forecast very little.

## Scope

- Importance is not causation and not significance. It states what the model
  used, which is a statement about the model.
- No re-tuning, re-splitting or re-scoring was done here.

## Checked

- importances written to a file rather than only plotted

## Not checked

- impurity importances are biased toward high-cardinality features
