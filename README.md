# Layer 5 — Commands (`.claude/commands/`)

This layer tests whether wrapping the existing subagent workflow into reusable **Claude commands** provides additional benefits over invoking the subagents directly.

The commands define a fixed sequence for running the different agents, allowing the same workflow to be triggered using a much shorter instruction.

## Key Observations

### 1. Output quality remained almost identical to Layer 4

The most noticeable result is that introducing commands did **not improve the actual analytical output**.

The completion scores remained the same:

- EDA: **9/10 → 9/10**
- Forecasting: **12/12 → 12/12**

The same subagents are ultimately performing the same analysis, so the resulting notebooks, reports and analytical checks are very similar.

This suggests that commands mainly change **how the workflow is triggered**, rather than improving how the individual analytical stages are performed.

### 2. Commands make the workflow more reproducible

The main advantage is that the sequence of steps no longer needs to be remembered or decided during every run.

Instead, the command already defines which agents should run, in what order, and what should happen if a required stage fails.

This makes the workflow easier to repeat and reduces the chance of stages being accidentally reordered or skipped.

For a fixed and frequently repeated pipeline, this can be useful.

### 3. The benefit is less significant for this data science use case

For this particular project, however, the workflow is relatively straightforward once the subagents from Layer 4 have already been configured.

The EDA and forecasting pipelines are not being repeatedly run by many different users or across many different projects. As a result, manually invoking the required subagents is still manageable.

Since the analytical output remains essentially unchanged, the additional command layer does not feel as necessary here as the introduction of subagents did in Layer 4.

Commands would likely become more useful for a workflow that is **frequently repeated, shared between users, or highly dependent on an exact execution order**.

### 4. Commands can require more context and tokens

Although the output quality stayed the same, the command-based runs used noticeably more resources.

Peak context increased from approximately **98k to 162k for EDA** and **101k to 176k for forecasting**. Total token usage also increased substantially.

This means that the convenience and reproducibility of commands come with additional context and token usage.

For this experiment, that trade-off is difficult to justify when the resulting analysis is almost identical to Layer 4.

### 5. Commands control procedure, not task-specific intent

Commands are useful for defining a fixed workflow, but they cannot contain every detail specific to each individual analysis.

The command can specify that certain agents should run in a particular order, but the actual analytical objective still needs to come from the task prompt and project context.

This is similar to the earlier findings with rules: putting more instructions into the setup does not remove the need to clearly describe the current task.

## Main Takeaway

Commands mainly improve **repeatability rather than analytical quality**.

For this data science workflow, Layer 4 already gains most of the important benefits through dedicated subagents. Adding commands produces almost the same analytical output while introducing another configuration layer and using considerably more context and tokens.

Therefore, commands are useful, but **not particularly necessary for this specific use case**.

They would be more valuable when the same multi-agent workflow needs to be executed repeatedly, by different users, or with a strict sequence that must never be skipped.

The progression across the layers can therefore be extended as:

- **Layer 1:** Rules improve project structure.
- **Layer 2:** Persistent rules improve consistency across runs.
- **Layer 3:** Clearer rules, `CLAUDE.md` and Plan Mode improve precision and cohesion.
- **Layer 4:** Subagents improve execution by separating complex workflows into dedicated stages.
- **Layer 5:** Commands make those workflows easier to repeat, but provide limited additional value for this particular data science task.

> **Subagents improve how the workflow is carried out; commands mainly make the same workflow easier to repeat.**