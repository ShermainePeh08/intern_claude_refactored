paths: "**/*"
description: Never-overwrite list and file placement rules

# File safety

Loaded on every file operation. Deliberately short, because it is paid for often.

- Never overwrite `README.md`, `CLAUDE.md`, or anything under `results/`.
- Never modify anything under `datasets/raw/`.
- Never modify anything under `experiments/snapshots/` or
  `experiments/transcripts/` — they are the evidence base for the study.
- New files go in the folder their type belongs to. Nothing is written to the
  project root.
- Before creating a file, check whether one already exists for that purpose.
  Prefer editing over creating a near-duplicate with a different name.
- If you believe an existing file must be replaced, say so and wait. Do not
  replace it and mention it afterwards.