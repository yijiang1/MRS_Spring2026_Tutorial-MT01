---
name: microscopy-particle-analysis
description: Counts and measures particles in a microscopy image (SEM, TEM, optical). Use when the user asks about particle count, particle size, grain size, size distribution, or wants to analyze blobs/spots in a 2-D micrograph image file.
when_to_use: When the user provides a path to a microscopy image (PNG, TIFF, JPG) and asks how many particles are in it, what their average size is, or how the size is distributed.
allowed-tools: Read Bash(python3 *) Bash(python *) Bash(pip install *)
---

# Microscopy Particle Analysis

## Task

Run the bundled `analyze.py` script on the user's microscopy image and report
the results in plain language.

## How to run

The script lives next to this `SKILL.md`. Invoke it with the user's image
path. The script prints JSON to stdout.

```bash
python3 "${CLAUDE_PROJECT_DIR}/.claude/skills/microscopy-particle-analysis/analyze.py" <image_path> --min-area 30
```

If the user-skill version is installed at `~/.claude/skills/`, use that path
instead:

```bash
python3 "$HOME/.claude/skills/microscopy-particle-analysis/analyze.py" <image_path> --min-area 30
```

## Optional flags

- `--min-area N` — minimum particle area in pixels (default 30). Increase to
  filter noise blobs, decrease to catch small particles.
- `--save-overlay path.png` — write a 3-panel diagnostic plot
  (original / threshold / labels) to the given path. Recommended whenever the
  user might want to verify the segmentation visually.

## Dependencies

The script needs `numpy`, `scipy`, `Pillow` (or `matplotlib`). If a missing
import error appears, install with:

```bash
pip install numpy scipy pillow matplotlib
```

## How to report the result

Parse the JSON the script prints, then write a 2-3 sentence summary covering:

1. Particle count
2. Mean and standard deviation of equivalent radius (in pixels — note the
   user may need to convert via the image scale bar to physical units; if you
   know the scale, do the conversion explicitly)
3. The Otsu threshold value and the `min_area` setting used (so the result is
   reproducible)

If `--save-overlay` was used, end by mentioning the file path so the user can
inspect the segmentation visually.

## When to NOT call this skill

- The user is asking about a 1-D spectrum (XRD pattern, Raman, etc.) — wrong
  pipeline.
- The image is a structural/atomic-resolution micrograph where the goal is
  lattice analysis, not particle counting.
- The user has already segmented the image and just wants statistics — they
  can post-process directly.

In those cases, defer to the user or suggest a more appropriate workflow
rather than forcing this script.
