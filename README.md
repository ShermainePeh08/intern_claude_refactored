# Layer 4 — Subagents (`.claude/agents/`)

This layer tests whether splitting the workflow across **dedicated subagents** improves the consistency and completeness of the analysis.

Instead of relying on one main Claude session to remember and perform every requirement, different stages of the workflow are assigned to specialised agents with their own instructions and context.

## Key Observations

### 1. Subagents improved how consistently required steps were completed

The clearest improvement was in the number of required checks that were actually performed.

With `CLAUDE.md` and the existing rules alone, some requirements were still skipped even though they had already been specified.

After introducing subagents:

- EDA increased from **5/10 to 9/10** required checks completed.
- Forecasting increased from **6/12 to 12/12** required checks completed.

The recovered steps were mainly procedural tasks such as lag analysis, regime splitting, multiple forecast horizons, baseline comparison, tuning and notebook delivery.

This suggests that **having a rule present does not necessarily mean Claude will execute it**. Assigning a stage to a dedicated subagent makes that requirement part of a specific procedure rather than another instruction competing for attention in the main context.

### 2. The workflow became more clearly separated by responsibility

Each subagent handles a specific part of the analysis, such as feature engineering, forecasting, feature importance or backtest auditing.

The agents also produce their own reports, making it clearer which stage generated a particular result or finding.

Compared with having one agent perform the entire workflow, this creates a more traceable structure where each stage has a clearer responsibility.

### 3. Subagents reduced pressure on the main context window

Using subagents increased the **total number of tokens used**, but reduced the **peak context held in the main session**.

For EDA, peak context decreased from approximately **128k to 98k**, while forecasting decreased from approximately **140k to 101k**.

This happens because each subagent performs its work within its own context and only returns the relevant result to the main agent.

Therefore, intermediate exploration and reasoning do not all need to remain inside one increasingly large context window.

The trade-off is that **subagents may use more tokens overall, but distribute the work across separate context windows**.

### 4. Dedicated agents can also catch issues that the main workflow misses

The backtest auditor identified a limitation involving the effective sample size of forward-filled ACLED features.

Interestingly, this was a check that was not successfully resolved in any of the tested configurations. However, the dedicated auditor still identified and reported the limitation rather than allowing the workflow to appear completely correct.

This shows another benefit of separating responsibilities: a dedicated checking agent can review the outputs independently instead of relying on the same agent that created them to also verify them.

### 5. Subagents introduce additional setup and execution cost

Creating separate agents requires more initial configuration, and the workflow generates more intermediate reports and uses more tokens overall. Forecasting also took longer to complete because additional stages, such as the dedicated audit, were actually performed.

Subagents are therefore most useful when the workflow is sufficiently complex that **consistency, traceability and context management are more important than minimising setup or execution time**.

## Main Takeaway

Subagents mainly improve the **execution of multi-step workflows**.

The earlier layers showed that rules and `CLAUDE.md` can clearly define what Claude is expected to do. However, this layer shows that requirements can still be skipped even when they are present in the context.

Delegating stages to dedicated agents makes the workflow more procedural: each agent has a specific responsibility and its own context in which to complete it.

This improves completion of required checks and reduces pressure on the main context window, although it requires additional setup, tokens and execution time.

The progression across the layers can therefore be extended as:

- **Layer 1:** Rules improve project structure.
- **Layer 2:** Persistent rules improve consistency across runs.
- **Layer 3:** Clearer rules, `CLAUDE.md` and Plan Mode improve precision and cohesion.
- **Layer 4:** Subagents improve execution by separating complex workflows into dedicated stages.

> **Rules define what should happen; subagents make it more likely that each stage actually happens.**