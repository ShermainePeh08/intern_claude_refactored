## Main Layer --- Base Project Structure

The main layer compares EDA generated using **short vs. detailed
prompts**, both with and without explicit project rules. The aim is to
observe Claude's default behaviour and determine how much structure
needs to be explicitly specified.

### Key Observations

**1. Without rules, the project structure is inconsistent**

When no structural rules are provided, Claude decides how to organise
the outputs on its own. This makes the resulting project structure
relatively unpredictable.

For example, the short-prompt run places the Python script, generated
figures, reports and CSV outputs together in the same directory. The
detailed prompt improves this slightly by introducing a `results/`
folder and separating figures and reports, but this organisation comes
from Claude's own interpretation rather than a consistent predefined
structure.

This means that **prompt detail alone can improve organisation, but does
not guarantee a predictable project structure**.

**2. Claude defaults heavily towards `.py` scripts and standalone `.png`
outputs**

Without being explicitly instructed otherwise, the analysis is primarily
generated as Python (`.py`) scripts. Visualisations are also exported as
individual `.png` files.

While technically usable, this makes exploratory analysis harder to
review because the code, explanation and resulting visualisation are
separated. A user has to locate and open each figure individually
instead of viewing the analysis sequentially alongside its outputs.

**3. Adding rules produces a more usable analysis structure**

When rules explicitly specify the expected project organisation, the
outputs become noticeably more structured. The rules-based runs
introduce dedicated locations such as:

-   `notebooks/` for the analysis
-   `results/figures/` for visualisations
-   `results/reports/` for analysis outputs

Notebook (`.ipynb`) versions are also generated, making the EDA easier
to inspect because code and outputs can be reviewed together.

The improvement is therefore less about changing the analysis itself and
more about making the generated project **predictable, navigable and
easier to review**.

**4. Short prompts result in visibly less comprehensive EDA**

The difference is not limited to file organisation. The short prompt
also performs substantially fewer analytical checks.

The basic short-prompt output mainly contains the data audit,
correlation analysis, feature relationships and five figures. In
comparison, the detailed runs expand into additional checks such as
stationarity testing, significance testing, regime comparisons, Granger
causality, driver ranking and other diagnostics.

This suggests that Claude does not automatically infer the full scope of
an EDA from a broad instruction. A short prompt leaves more decisions to
the agent, causing potentially important checks to be omitted.

**5. Existing project files may be modified without explicit safeguards**

One issue observed in this layer was that the existing project
`README.md` was **wiped out on two separate runs**.

The README was not part of the requested EDA task, yet without an
explicit rule governing how existing Markdown files should be handled,
Claude still modified or replaced it.

It highlights a limitation of relying only on task-level instructions:
**if a file or behaviour is not explicitly protected, Claude may make
unintended changes while completing the task.**

This issue becomes an important motivation for testing persistent
project-level rules in the following layer.

### Main Takeaway

The base layer shows two separate effects:

**Prompt detail determines how much Claude investigates, while explicit
rules determine how consistently the work is structured.**

A detailed prompt produces a more comprehensive analysis, but without
rules the output format and organisation are still largely left to
Claude. Adding rules for notebooks, folders and output locations makes
the project considerably easier to navigate and reproduce.

Therefore, relying on Claude's default behaviour is possible, but the
result is relatively random: **short prompts risk incomplete analysis,
while missing structural rules lead to inconsistent and less reviewable
outputs.**
