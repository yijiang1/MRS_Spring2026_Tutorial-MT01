# Writing a Claude Code Skill

**MRS Spring 2026 — Tutorial MT01**

A skill is the simplest way to give Claude a packaged capability. The whole
"installation" is putting a markdown file in the right folder. No Python
project, no config server, no manifest — just markdown.

This guide shows you how to write one in five minutes, and the patterns that
matter when you go further.

---

## TL;DR — what is a skill, exactly?

A skill is a directory containing at minimum one file: `SKILL.md`.

```
my-skill/
└── SKILL.md
```

The file has YAML frontmatter (description, optional config) and a markdown
body (instructions Claude follows when the skill is active).

That's the whole format.

---

## Where to put it

| Scope | Location | When to use |
|---|---|---|
| Personal | `~/.claude/skills/<name>/SKILL.md` | Your own workflow tools, across all projects |
| Project | `.claude/skills/<name>/SKILL.md` (in repo root) | Group-specific skills you commit to git so collaborators get them automatically |

**`<name>` matters**: it becomes the slash command (`/my-skill`). Use
lowercase letters, digits, hyphens. Max 64 chars.

---

## Anatomy of `SKILL.md`

```markdown
---
name: extract-synthesis-recipe
description: Extracts synthesis procedures and parameters from materials-science
  papers or documents. Use when analyzing synthesis protocols, material
  preparation steps, or experimental procedures.
allowed-tools: Read Bash(grep *)
---

## Task
Extract the synthesis recipe from the provided text or file.

## Output format
Provide the recipe as:
1. **Materials**: list reagents with quantities and suppliers if mentioned
2. **Equipment**: instruments and conditions
3. **Procedure**: step-by-step with temperatures, times, atmospheres
4. **Characterization**: methods used to verify the product (XRD, SEM, ...)
5. **Yield & Properties**: final yield, purity, key properties

## Guidelines
- Preserve exact temperatures, times, chemical formulas verbatim
- Flag ambiguous or missing parameters as `(unspecified)`
- Note any safety warnings explicitly
```

### Frontmatter fields

| Field | Required | What it does |
|---|---|---|
| `name` | No (defaults to dir name) | The slash command (`/<name>`) |
| `description` | **Recommended** | Text Claude uses to decide *when to invoke this skill automatically*. Front-load the trigger; this is the most important field you write. |
| `when_to_use` | No | Extra trigger context, appended to `description` for matching |
| `allowed-tools` | No | Space-separated list of tools Claude can use *without prompting* (e.g. `Read Bash(git *)`) |
| `disable-model-invocation` | No | `true` = manual `/<name>` only. Default `false` (Claude can auto-invoke). |
| `argument-hint`, `arguments` | No | Document what `/<name> <args>` expects |

The combined `description` + `when_to_use` text is **capped at 1,536
characters**, so be specific but not verbose. The most important sentence is
the first one — Claude scans it first.

---

## How invocation works

There are two ways a skill gets used:

1. **User invocation**: you type `/<skill-name>` (with optional args). Always
   works regardless of frontmatter.
2. **Model invocation**: Claude *itself* decides to invoke the skill because
   your message matches the `description`. Disabled by setting
   `disable-model-invocation: true`.

**Rule of thumb:**
- For **knowledge** skills (extract data, look something up, follow a
  recipe): leave model invocation enabled. Claude will use them when relevant.
- For **action** skills with side effects (deploy, commit, send a message):
  set `disable-model-invocation: true` so they only fire when *you* type the
  command.

---

## Adding scripts and reference data

A skill directory is a regular folder. Put any supporting files alongside
`SKILL.md` and **link to them from the markdown body** so Claude knows they
exist.

```
microscopy-particle-analysis/
├── SKILL.md
├── analyze.py        ← actual analysis code
└── examples.md       ← reference outputs
```

Inside `SKILL.md`:

```markdown
## How to run

Execute the analysis with:

```bash
python "${CLAUDE_PROJECT_DIR}/.claude/skills/microscopy-particle-analysis/analyze.py" <image_path>
```

For sample expected outputs, see [examples.md](examples.md).
```

That's it. Claude reads the markdown, sees the bash snippet, and runs
`analyze.py` when appropriate. No registration, no plugin manifest.

**Keep `SKILL.md` short** (under ~500 lines). Put long reference material in
sibling files and link them — Claude only loads the linked files when it
decides they're relevant, which keeps your context window healthy.

---

## A 5-minute exercise: write your first skill

1. Pick a task you keep doing manually. Examples:
   - "Look up a chemical in our group's lab inventory spreadsheet"
   - "Format a beamtime proposal section to ANL house style"
   - "Convert a CIF file into our standard report template"

2. Make a folder and a `SKILL.md`:

   ```bash
   mkdir -p ~/.claude/skills/my-task
   $EDITOR ~/.claude/skills/my-task/SKILL.md
   ```

3. Frontmatter (only `description` matters at this stage):

   ```yaml
   ---
   description: Does X. Use when the user asks about Y or wants to Z.
   ---
   ```

4. Body: write the *instructions you'd give a smart assistant* doing this
   task for the first time. Step by step. Include any conventions, file
   paths, gotchas.

5. Restart Claude Code in any project. Type a message that matches the
   description. Watch Claude pick up the skill automatically.

6. Iterate the description until Claude reliably invokes it on the right
   prompts and stays out on irrelevant ones.

---

## Common patterns

**Skills as documented procedures.** Many of the most useful skills are just
checklists Claude follows. "When the user asks for a code review, do X, then
Y, then Z." No code, no scripts. Just discipline.

**Skills as glue around scripts.** When you have a working analysis script,
wrap it: tell Claude *when* to run it, *how* to interpret the output, and
*what* to report back. The Python stays as-is; the skill teaches Claude when
it applies.

**Skills as library indices.** Long documentation? Put the table of contents
in `SKILL.md` and the body in sibling files. Claude reads the index first and
fetches the relevant chapter on demand. (This is the pattern used by
Anthropic's official `skill-creator`, `argo-gateway`, and others.)

---

## Pitfalls

- **Vague descriptions** → Claude either invokes the skill all the time or
  never. Be specific about *which user prompts* should trigger it.
- **Skill directory not found** → check `~/.claude/skills/<name>/SKILL.md`
  exact spelling and capitalization. The filename is `SKILL.md` (not
  `skill.md`, not `Skill.md`).
- **Stale skills** → Claude Code caches the skill list at session start.
  Restart the session after editing `SKILL.md` (or a new skill won't appear).
- **`disable-model-invocation` confusion** → if your skill never fires
  automatically, check this isn't set to `true`.
- **Hard-coded paths** → use `${CLAUDE_PROJECT_DIR}` rather than absolute
  paths so the skill works in anyone's checkout.

---

## Where to read more

- Skills docs: <https://code.claude.com/docs/en/skills.md>
- Two ready-to-copy skills are in `example_skills/` next to this file.
- The `/init` command in Claude Code can scaffold a `CLAUDE.md`; the
  `/skill` (or `skill-creator`) skill can scaffold a new `SKILL.md`.
