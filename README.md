# Layer 3 --- Plan Mode + `CLAUDE.md`

This layer tests the effect of combining **clearer persistent rules,
`CLAUDE.md`, and Plan Mode**. Compared with the earlier layers, the
focus is on whether giving Claude clearer project-level expectations
reduces unnecessary outputs and produces a more cohesive analysis.

## Key Observations

### 1. Clearer rules produce a more precise final project structure

In the earlier layers, instructing Claude to use notebooks improved the
structure, but Claude could still generate additional `.py` versions of
the analysis.

With the help of the CLAUDE.md in this layer, the intended output format is
more explicitly defined. The analysis is kept in `.ipynb` notebooks
without also generating redundant `.py` analysis files.

This is an improvement over simply requesting notebooks because the rule
does not only state **what should be created**, but also makes clearer
**what should not be created**. This could also be added more clearly in the rules.md files.

As a result, the final project contains fewer unnecessary duplicate
outputs and is easier to navigate.

### 2. Plan Mode produces a more cohesive execution

All runs in this layer were performed using **Plan Mode**.

Compared with immediately executing the task, Plan Mode encourages
Claude to consider the overall workflow and project structure before
making changes. The resulting analysis tends to feel more cohesive, with
the different analytical steps fitting together more clearly.

There are also slightly more explanations around the analysis and why
particular steps are being performed, rather than the output feeling
like a collection of independently generated checks.

### 3. `CLAUDE.md` provides broader persistent project context

`CLAUDE.md` provides Claude with project-level context that remains
available beyond the individual command.

Together with the persistent rules, this reduces the amount of project
structure and behavioural guidance that needs to be repeated in every
prompt.

This builds on the previous layer: persistent rules help ensure that
conventions survive across runs, while `CLAUDE.md` provides a broader
description of how Claude should approach the project as a whole.

### 4. Combining Plan Mode, `CLAUDE.md` and clearer rules reduces agent discretion

Across the earlier layers, many output decisions were left for Claude to
infer, such as whether to use `.py` or `.ipynb`, whether both formats
should be generated, how outputs should be organised, and how much
explanation should accompany the analysis.

In this layer, more of these decisions are explicitly defined before
execution.

The result is a more predictable project that more closely matches the
intended workflow.

### 5. Detailed prompts still produce more complete analysis

Despite the additional structure provided by Plan Mode, `CLAUDE.md` and
clearer rules, the difference between short and detailed prompts remains
visible.

A short prompt still provides less analytical direction, meaning Claude
has to infer which checks are necessary. The detailed prompt gives
clearer expectations about what should be investigated and therefore
tends to produce a more comprehensive and explanatory result.

This reinforces the finding from the previous layers: **project-level
instructions improve execution, but they do not replace task-level
analytical detail.**

### 6. Project instructions are more reliable when separated by purpose

As an additional test, the same setup was run using only `CLAUDE.md` as the main source of project rules (EDA --> short-no-rules), without separately and explicitly reinforcing the notebook output requirements.

In this case, Claude reverted to generating the analysis as a `.py` file.

This suggests that simply placing **all instructions into one `CLAUDE.md` file does not guarantee that every requirement will be followed consistently**. As the file becomes longer and contains a mixture of project context, workflow instructions, output requirements and other conventions, individual rules may become less prominent.

The solution is therefore not to continuously add every new instruction into a single increasingly long rules file. Instead, instructions should be **separated according to their purpose and placed where they are most relevant**.

For example:
* `CLAUDE.md` → overall project context, objectives and workflow guidance
* `RULES.md` → persistent behavioural and structural requirements
* Task prompt → specific analytical requirements for the current task

This keeps each source of instruction focused and makes important requirements more explicit without unnecessarily expanding a single context file.

## Main Takeaway

This layer shows that the benefit of project-level guidance increases
when the instructions become more explicit.

Simply requesting notebooks can result in notebooks being generated **in
addition to** Python scripts. Clearly defining the notebook as the
intended analysis format prevents the unnecessary `.py` version from
being created and produces a cleaner final project.

At the same time, using **Plan Mode together with `CLAUDE.md` and
persistent rules** results in a more cohesive workflow, with slightly
more explanation and stronger consistency between the different stages
of the analysis.

The progression across the layers can therefore be summarised as:

-   **Layer 1:** Rules improve the structure of the generated project.
-   **Layer 2:** Persistent rules make that structure and project
    behaviour more reliable across runs.
-   **Layer 3:** Clearer persistent rules, `CLAUDE.md` and Plan Mode
    further reduce unnecessary agent decisions and produce a more
    cohesive final analysis.

However, the detailed prompt remains important. These mechanisms control
**how Claude approaches, structures and preserves the work**, but the
prompt still determines **how much analytical direction Claude
receives**.

> **Persistent rules improve consistency, clearer rules improve
> precision, and Plan Mode improves cohesion --- but detailed prompts
> are still needed to define the depth of the analysis.**
