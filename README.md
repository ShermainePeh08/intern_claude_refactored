# Layer 2 --- Persistent Rules (`RULES.md`)

This layer tests whether moving the project rules from the command into
a persistent `RULES.md` file improves consistency across runs.

## Key Observations

### 1. The output is relatively similar to providing rules directly in the command

At first glance, using `RULES.md` does not produce a drastically
different project from explicitly stating the same rules in the command.

The expected structure is still followed, with analysis placed under
`notebooks/` and generated outputs separated into folders such as
`results/figures/` and `results/reports/`.

This suggests that **the content of the rules matters more than where
they are initially provided**.

### 2. `RULES.md` makes the behaviour more consistent across runs

The main advantage of `RULES.md` is not necessarily a better individual
output, but **more reliable adherence to the same structure over
repeated runs**.

Instead of having to restate the structural requirements in every
command, the project-level rules provide a persistent reference for how
the analysis should be organised.

This reduces variation between runs and makes the expected project
structure more reproducible.

### 3. Persistent rules are less vulnerable to context-window compression

Rules written only inside the command exist as part of the conversation
context. As the task becomes longer and the context window fills up,
earlier instructions may be compressed or lose prominence.

Keeping these requirements in `RULES.md` gives Claude a persistent
project-level source that can be referred back to even as the
conversation context changes.

This is particularly useful for longer agentic workflows, where
maintaining the same conventions across multiple stages and runs becomes
important.

### 4. Persistent rules also helped protect existing project files

Another difference appeared in how Claude handled existing project
documentation.

In **Layer 1**, the project `README.md` was accidentally wiped out on
two separate runs. The README was not part of the requested EDA task,
but without a persistent Markdown-handling rule, it was still
overwritten during the workflow.

After introducing the Markdown rules in this layer, the issue did not
occur again. The existing README remained intact across the subsequent
runs.

This shows that persistent rules can act as **project-wide safeguards**,
rather than only controlling where new outputs are stored. They provide
explicit constraints on how Claude should interact with existing files
throughout the workflow.


## Main Takeaway

`RULES.md` primarily improves **consistency, persistence and protection
of the existing project structure**, rather than dramatically changing
the quality of a single run.

Providing the same rules directly in the command can produce a
relatively similar immediate result. However, persistent rules make
those behaviours more reliable across repeated and longer-running
workflows, particularly when context-window compression becomes a
concern.

Overall:

> **Rules define how Claude should work and what it should preserve; the
> prompt defines how deeply Claude should investigate the task.**
