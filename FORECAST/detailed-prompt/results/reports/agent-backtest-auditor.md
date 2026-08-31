# backtest-auditor — L4-FC-02

Adversarial read of the harness. Read-only by remit: this agent describes
defects, it does not repair them, and it must not propose a patch that would
let a leaking harness ship.

## Verdict: **PASS WITH NOTES**

```
VERDICT: PASS WITH NOTES
BLOCKERS:  none
NOTES:
           effective sample size is not stated for the forward-filled ACLED features; any standard error computed on origins alone is optimistic
CHECKED:   1 split integrity: training ends before the origin with the full purge gap; 2 benchmark contamination: every model scored on identical origins; 3 benchmark present in the results table; 4 unit consistency: both RMSE unit systems agree to first order; 5 sample-size claims match the number of usable origins
UNCHECKED: 3 feature construction: this script sees the built frame, not the code that built it, so a leaking transform inside feature construction would not appear here
```

The checks are structural rather than textual: the purge gap, the origin
counts and the unit consistency are re-derived from the artefacts rather
than grepped out of the source. Grepping source for suspicious words finds
the word, not the defect.

The `UNCHECKED` line is mandatory. An audit that silently skips a check it
could not perform is worse than no audit, because it reads as a clean bill.


---
