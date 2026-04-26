# Claude Code + Skills — Tutorial Materials

**MRS Spring 2026 — Tutorial MT01: Deploying Agentic AI in Materials Characterization Workflows**

This folder is a self-contained set of artifacts for the **Claude Code +
Skills** segment of the tutorial. The notebooks (`../00_*.ipynb` to
`../07_*.ipynb`) cover the API and frameworks; this folder covers the
*interactive CLI* angle — what changes when an LLM can read your filesystem,
run shell commands, and load packaged capabilities you wrote yourself.

## What's here

```
claude_code_skills/
├── CLAUDE_CODE_CHEATSHEET.md         ← one-page reference (install, commands, hooks)
├── WRITING_A_SKILL.md                ← step-by-step skill-authoring guide
├── DEMO_SCRIPT.md                    ← rehearsable 8-10 min live demo script
├── starter_pack/                     ← clone-and-go sandbox for the audience
│   ├── CLAUDE.md                       project memory file Claude reads on entry
│   ├── PROMPTS.md                      suggested prompts to try
│   └── data/
│       ├── sample_microscopy.png       512x512, ~45 particles (ground truth in CLAUDE.md)
│       └── sample_synthesis.md         four paragraphs incl. one decoy
└── example_skills/                   ← copy these into ~/.claude/skills/
    ├── extract-synthesis-recipe/
    │   └── SKILL.md                    pure-prompt skill, no scripts
    └── microscopy-particle-analysis/
        ├── SKILL.md                    skill that wraps a Python script
        └── analyze.py                  the bundled analysis (numpy + scipy)
```

## Suggested teaching order

1. **Open with the live demo** (see `DEMO_SCRIPT.md`) — 8-10 minutes.
2. **Point the audience at this folder** as their take-home reference.
3. **Tell them the install path**: install Claude Code, copy the example
   skills, `cd` into `starter_pack/`, and follow `PROMPTS.md`.
4. **For the curious**: `WRITING_A_SKILL.md` has a 5-minute exercise that
   walks them through writing their first skill from scratch.

## How this maps to the notebooks

| Notebook | CLI counterpart | What's different in Claude Code |
|---|---|---|
| `02_structured_outputs.ipynb` | `/extract-synthesis-recipe` skill | Claude can read the source file directly; the skill packages the schema and rules |
| `04_agent_microscopy.ipynb` | `/microscopy-particle-analysis` skill | `analyze.py` is the same algorithm; the skill teaches Claude when and how to use it |
| `05_mcp_server.ipynb` | `claude mcp add ...` | The MCP server you built in the notebook becomes a real Claude Code integration with one command |

## Audience installation (for the slides)

```bash
# 1. Install Claude Code
npm install -g @anthropic-ai/claude-code

# 2. First-time login
claude
> /login

# 3. Install the example skills
git clone https://github.com/yijiang1/MRS_Spring2026_Tutorial-MT01.git
cp -R MRS_Spring2026_Tutorial-MT01/claude_code_skills/example_skills/* ~/.claude/skills/

# 4. Try the starter pack
cd MRS_Spring2026_Tutorial-MT01/claude_code_skills/starter_pack
claude
> What's in this folder?
```

## Caveats / things to know

- **Skills are cached at session start.** If you edit a `SKILL.md`,
  restart Claude Code or it won't see the change.
- **The example skills assume the standard install path**
  (`~/.claude/skills/<name>/`). If the audience puts them somewhere else,
  the bash invocations in `microscopy-particle-analysis/SKILL.md` will need
  updating.
- **The analyze.py script needs Python 3.7+ and `numpy + scipy + pillow`**
  (or `matplotlib` as a Pillow fallback).
- **Claude Code reads everything below its cwd.** The starter pack only
  contains synthetic, non-sensitive data — but reinforce this point during
  the talk so attendees don't run `claude` in their home directory.
