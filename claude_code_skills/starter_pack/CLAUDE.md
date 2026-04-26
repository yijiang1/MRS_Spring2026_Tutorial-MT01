# MRS Tutorial — Claude Code Starter Pack

This folder is a sandbox for trying out Claude Code on toy materials-science
data. It was assembled for the MRS Spring 2026 tutorial *Deploying Agentic AI
in Materials Characterization Workflows*.

## What's here

- `data/sample_microscopy.png` — a synthetic microscopy image (512×512, 8-bit
  grayscale) with ~45 bright circular particles on a dark background.
  Ground-truth particle count is **45** with mean equivalent radius **~13.7 px**.
- `data/sample_synthesis.md` — four paragraphs of (fictional) synthesis text:
  one clean BaTiO3 recipe, one incomplete BiFeO3 case, one NMC811 cathode
  description, and one decoy paragraph that is not a synthesis at all.
- `PROMPTS.md` — suggested prompts to try.

## How to drive this folder with Claude Code

You should be able to ask things like:

- *"What's in this folder?"*
- *"Open the sample microscopy image, find the particles, and report the mean radius."*
- *"Read `data/sample_synthesis.md` and extract each synthesis recipe as JSON."*
- *"Extract the synthesis recipes and put them in a CSV."*

Claude Code can read PNG and markdown files directly, write Python in its
sandbox, run `pip install` if needed, and produce plots. You don't have to
specify *how* — just describe the goal.

## Hints for Claude

- For particle analysis on `sample_microscopy.png`, an Otsu threshold +
  connected-component labelling (`scipy.ndimage`) recovers the particles
  cleanly. Use a `min_area` of ~30 px to discard noise blobs.
- For synthesis extraction, structure the output as JSON with fields
  `material`, `route`, `precursors`, `calcination_temp_C`,
  `calcination_time_h`, `atmosphere`, `crystallite_size_nm`. If a value is
  not stated, set it to `null` rather than guessing.
- Paragraph 4 in `sample_synthesis.md` is a decoy and should be flagged as
  "not a synthesis", not extracted as one.

## Related skills

If the audience copies the example skills from `../example_skills/` into
their `~/.claude/skills/` folder, the following slash commands become
available:

- `/extract-synthesis-recipe` — formal extraction of synthesis info
- `/microscopy-particle-analysis` — runs the bundled analysis script
