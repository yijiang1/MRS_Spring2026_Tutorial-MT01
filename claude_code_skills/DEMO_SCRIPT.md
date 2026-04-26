# Live Demo Script — Claude Code + Skills

**MRS Spring 2026 — Tutorial MT01**
Target length: **8-10 minutes**.
Format: live terminal demo, audience watches your screen.

---

## Why this demo (the framing slide)

The audience has just spent 30+ minutes in notebooks watching code run.
Now you're going to show what it looks like when an LLM **drives your
filesystem instead of your kernel**. The pitch is one sentence:

> *"Everything you just did in notebooks, you can also do at the
> command line — and there it can read your data, write code, and run
> things on your behalf."*

The wow moment is **beat 7** (skills are just markdown). Don't blow it early.

---

## Pre-flight (do BEFORE you walk on stage)

1. **Terminal ready in `claude_code_skills/starter_pack/`.** Font size 18+
   for the back row.
2. **Both example skills installed and verified.** Run once:
   ```bash
   mkdir -p ~/.claude/skills
   cp -R claude_code_skills/example_skills/* ~/.claude/skills/
   ls ~/.claude/skills/
   # expect: extract-synthesis-recipe  microscopy-particle-analysis
   ```
3. **Smoke-test both skills before the talk.** Open Claude Code in
   `starter_pack/`, type `/` to confirm both names appear in the picker, then
   actually run each one with a real prompt. Iterate the description in
   `SKILL.md` if auto-invocation doesn't fire on the prompts in
   `starter_pack/PROMPTS.md`.
4. **`claude` already authenticated** (`/login` done in advance).
5. **Network confirmed** — Claude Code needs the API.
6. **Recording running as backup** — see [Backup plan](#backup-plan).
7. **Browser tab open** to the cheat sheet PDF / `WRITING_A_SKILL.md`
   in case you need a visual aid mid-demo.

---

## The script

### Beat 1 — orientation (~30 s)

You: *"This is just my terminal. I'm going to start Claude Code in a folder
that has some toy materials data."*

```bash
cd starter_pack
claude
```

Once the prompt appears, type:

> **What's in this folder?**

Claude reads `CLAUDE.md` and explains the contents.

**Highlight:** "Notice I didn't tell it anything about the folder. It read
the project memory file (`CLAUDE.md`) and figured it out."

---

### Beat 2 — end-to-end image analysis (~2 min)

> **Open `data/sample_microscopy.png`, find the particles, report the count and the mean equivalent radius. Save a 3-panel plot of original / threshold / labels.**

Watch it:
- read the PNG
- write a Python script (numpy + scipy.ndimage)
- run the script
- save the overlay plot
- report 45 particles, mean radius ~13.7 px

When the overlay opens (or if you `open <file>` it), pause.

**Highlight:** "I described the goal. It picked Otsu thresholding and
connected-component labelling on its own. This is the same algorithm we
just saw in notebook 04 — but I didn't have to open a notebook."

---

### Beat 3 — structured extraction over messy text (~2 min)

> **Read `data/sample_synthesis.md`. Extract each synthesis as JSON with the standard fields (material, route, precursors, calcination temp/time/atmosphere, crystallite size). Flag any paragraph that isn't actually a synthesis.**

Expected behaviour:
- Three structured records (BaTiO3 clean, BiFeO3 with nulls + notes, NMC811)
- Paragraph 4 (the GNN paragraph) flagged as "not a synthesis"

**Highlight:** "Same task as notebook 02 — but here Claude is free to read
the file itself, retry if the JSON looks bad, and tell me when something
*isn't* a recipe at all."

---

### Beat 4 — show the skills are loaded (~15 s)

The transition from "general LLM" to "skills". In the Claude Code prompt
type a single forward slash:

```
> /
```

Claude Code shows the slash-command picker. Audience sees
`/extract-synthesis-recipe` and `/microscopy-particle-analysis` listed
alongside built-ins like `/help`, `/init`, `/agents`. **Point at them on screen.**

Press `Esc` to dismiss.

**Highlight:** "These two are mine — installed from the tutorial repo.
They're available in every Claude Code session on this machine because they
live in `~/.claude/skills/`."

---

### Beat 5 — invoke a skill explicitly (~1 min)

Now use the script-bundled skill on the image. Type literally this:

```
> /microscopy-particle-analysis data/sample_microscopy.png
```

In the transcript you'll see Claude:
- read the SKILL.md instructions
- run `python3 ~/.claude/skills/microscopy-particle-analysis/analyze.py data/sample_microscopy.png --min-area 30`
- parse the JSON output
- report ~ *"45 particles, mean equivalent radius 13.7 px (std 4.1 px),
  Otsu threshold 0.19, min_area 30 px"*

**Highlight:** "The same task as a minute ago — but this time the analysis
came from a packaged capability anyone in my group can install. The skill
told Claude *when* to run it and *how* to interpret the JSON it prints."

---

### Beat 6 — auto-invocation by description (~1 min)

Don't use a slash. Just ask in plain language — wording that matches the
skill's `description` field:

```
> Read data/sample_synthesis.md and pull out each synthesis as JSON. Flag any paragraph that isn't actually a recipe.
```

Watch the trace: Claude should auto-invoke `extract-synthesis-recipe`
because the prompt matches its description. You'll see something like
*"Invoking skill: extract-synthesis-recipe"* before the response begins.

Expected output: three structured records (BaTiO3 clean, BiFeO3 with `null`
fields + notes, NMC811), and paragraph 4 flagged as "not a synthesis".

**Highlight:** "I never typed `/extract-synthesis-recipe`. Claude matched
my prompt to the skill's *description* and invoked it on its own. That's
why the description field in the frontmatter matters more than anything
else you'll write — it's how Claude knows when your skill applies."

---

### Beat 7 — the wow moment: skills are just markdown (~2 min)

In the same Claude Code session, run a shell command via the `!` prefix:

```
> !cat ~/.claude/skills/extract-synthesis-recipe/SKILL.md
```

Audience sees ~50 lines of markdown. Frontmatter on top, instructions
below. **No Python, no plugin manifest, no install script.**

**The line to land:**

> *"That's the whole skill. There's no Python project, no manifest, no
> manager process. It's a markdown file. You can write one in 10 minutes,
> drop it in `~/.claude/skills/`, and every Claude Code session uses it
> automatically."*

If you have time, also show the script-bundled version:

```
> !cat ~/.claude/skills/microscopy-particle-analysis/SKILL.md
> !ls ~/.claude/skills/microscopy-particle-analysis/
```

Audience sees `SKILL.md` and `analyze.py` side by side.

**Optional follow-up line:** "When you have a working analysis script,
wrapping it as a skill is just a markdown file next to the script.
The markdown teaches Claude *when* to run it; the script does the work."

---

### Beat 8 — close (~30 s)

> *"To recap — Claude Code does three things notebooks don't: it reads
> your filesystem, it runs commands, and it loads packaged capabilities
> (skills, MCP servers, hooks) you can write yourself or share. Everything
> you just saw is in the `claude_code_skills/` folder of the tutorial repo.
> The starter pack and the two skills are the easiest way to get started."*

Point them at:
- `CLAUDE_CODE_CHEATSHEET.md` for installation and key commands
- `WRITING_A_SKILL.md` for "I want to write my own"
- `starter_pack/PROMPTS.md` for things to try after the talk

---

## Backup plan

Live demos fail. Have these in your back pocket:

1. **Pre-recorded video** of beats 1-7 (record it the day before; even a
   1-minute screen recording per beat is enough). Have the file open in QuickTime
   /VLC/your media player so you can switch to it instantly if the live demo
   stalls.
2. **Pre-saved transcripts** of expected Claude responses, in a file you can
   `cat` if the API call fails. The audience will still see the *flow*.
3. **Skip beat 6 (auto-invocation) if it doesn't fire** on the first try.
   The explicit slash-command version (beat 5) already proves the skill works,
   and beat 7 — the markdown reveal — is the punchline either way.
4. **If `analyze.py` fails** with an import error, fall back to
   `pip install numpy scipy pillow matplotlib` and re-run, or pivot to beat 6
   immediately (the synthesis-extractor skill needs no Python deps).

---

## Things that go wrong (and what to do)

| Symptom | Fix |
|---|---|
| `claude` not found | `npm install -g @anthropic-ai/claude-code` |
| Auth error | `/login`, complete in browser |
| Skill not invoked | Restart Claude Code (it caches skills at session start) |
| `analyze.py` import error | `pip install numpy scipy pillow matplotlib` |
| Overlay PNG doesn't open | `open <path>` (mac), `xdg-open` (linux), or attach in stage screen |
| Claude generates code that errors | Don't fight it on stage — say "in a real session I'd let it iterate; let's move on" |

---

## Optional extensions (only if you have spare time)

- `/agents` to show how subagents work (good for emphasising "you can
  scope the model's behaviour").
- `/hooks` to show automated post-edit linting.
- `/mcp` and `claude mcp add ...` to connect to the MCP server from
  notebook 05.

These are bonus content — don't sacrifice the core 8 beats above for them.
