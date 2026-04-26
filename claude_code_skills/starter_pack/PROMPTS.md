# Prompts to try

Open Claude Code in this folder (`claude` from the `starter_pack/` directory)
and try these in roughly this order. Each is meant to land a different
"this is what makes Claude Code different from a chat window" moment.

---

## 1. Orientation (10 seconds, no setup)

> What's in this folder?

Claude reads `CLAUDE.md` and gives you a guided tour. **The point:** you
didn't have to explain the project. Claude figures it out from the project
memory file.

---

## 2. End-to-end image analysis

> Open `data/sample_microscopy.png`, find the particles, report the count and the mean equivalent radius. Show me the segmentation overlay if you can.

Claude will write Python (likely `numpy + scipy.ndimage + matplotlib`),
install dependencies if needed, run it, and report back. Expect the count to
be 45 and the mean radius around 13.7 px (matches the ground truth in
`CLAUDE.md`).

**Wow moment:** you described the *goal*, not the algorithm. Claude picked
Otsu + labelling on its own.

---

## 3. Structured extraction over messy text

> Read `data/sample_synthesis.md`. For each paragraph, extract the synthesis as JSON with the fields listed in `CLAUDE.md`. Flag the decoy.

The interesting case is paragraph 4 (the GNN training paragraph) — Claude
should mark it as "not a synthesis" rather than fabricating numbers.

---

## 4. Iterative refinement

After the previous prompt:

> Now write the four records to `recipes.csv` and verify by reading it back.

Claude will create the file, read it, and report any mismatches. **The
point:** Claude Code can *act on the filesystem*, not just describe what to do.

---

## 5. Skill auto-invocation (requires example skills installed)

If you've copied the skills from `../example_skills/` into `~/.claude/skills/`:

> Extract the synthesis recipe from `data/sample_synthesis.md`.

Claude should automatically invoke the `extract-synthesis-recipe` skill (you'll
see it in the transcript). Same prompt as #3, but now there's a packaged
recipe driving the behaviour.

> /microscopy-particle-analysis data/sample_microscopy.png

Explicit invocation by slash command. The bundled `analyze.py` runs and Claude
summarises the result.

---

## 6. Bonus — explore Claude Code itself

> What slash commands are available in this session?

> Show me the contents of my CLAUDE.md (the starter pack one).

> What's the difference between `/agents`, `/hooks`, and `/mcp`?

These are good for the audience to develop intuition about Claude Code's own
moving parts during the talk.
