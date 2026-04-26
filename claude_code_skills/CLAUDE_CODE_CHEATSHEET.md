# Claude Code — One-Page Cheat Sheet

**MRS Spring 2026 — Tutorial MT01**

Claude Code is Anthropic's CLI: a Claude conversation that lives in your
terminal, can read your filesystem, run shell commands, edit code, and call
external tools. It is what you use when "ask the model and paste the result"
stops scaling.

---

## Install & login

```bash
# Install (requires Node 18+)
npm install -g @anthropic-ai/claude-code

# Or via Homebrew on macOS
brew install --cask claude-code

# First run
claude                # opens an interactive session in the cwd
/login                # authenticate with your Anthropic account
```

Pick the directory carefully: Claude Code can read everything below the cwd.
Don't run it in `~/`; do run it in your project root.

---

## Essential keys & slash commands

| Action | How |
|---|---|
| Submit | `Enter` |
| Cancel current generation | `Esc` |
| Newline in prompt | `Shift+Enter` (or `\` then Enter) |
| Show transcript | `Ctrl+R` |
| Resume previous session | `claude --resume`, or `/resume` |
| List slash commands | `/help` |
| Initialize a `CLAUDE.md` for this project | `/init` |
| Manage subagents | `/agents` |
| Manage hooks | `/hooks` |
| Manage MCP servers | `/mcp` |
| Edit user/project memory | `/memory` |
| Switch model (Opus/Sonnet/Haiku) | `/model` |
| Toggle plan mode | `Shift+Tab` (cycles modes) |
| Run a shell command | type `! <command>` |
| Skip permission prompts (use carefully) | start with `claude --permission-mode acceptEdits` |

---

## `CLAUDE.md` — per-project instructions

Drop a `CLAUDE.md` in your project root. Claude reads it on every session in
that directory. Use it to teach Claude about:

- What the project is and what's where
- Key commands (`pytest`, `make build`, `pre-commit run`)
- Conventions you want enforced ("use type hints", "tests live next to the code")
- Things to *avoid* ("don't touch `legacy/`")

A 30-line CLAUDE.md is usually enough; longer files dilute attention.

You can also keep a global `~/.claude/CLAUDE.md` for cross-project preferences.

---

## Subagents

A *subagent* is a focused agent persona Claude spawns when its description
matches the task. Use `/agents` to create one. Each subagent has:

- A name and trigger description
- Its own system prompt
- Its own tool whitelist

Common patterns: `code-reviewer`, `test-runner`, `doc-writer`, `data-explorer`.

---

## Skills

A skill is a **markdown file** (`SKILL.md`) that gives Claude a packaged
capability — domain knowledge, scripts, references — that it can invoke
automatically when its description matches the task, or that you can call
explicitly with `/skill-name`.

```
~/.claude/skills/<skill-name>/SKILL.md     # personal, all projects
.claude/skills/<skill-name>/SKILL.md       # project-scoped (commit to git)
```

See `WRITING_A_SKILL.md` in this folder for the full anatomy. Two ready-to-use
examples are in `example_skills/`.

---

## Hooks

A hook is a shell command Claude runs *automatically* in response to an event
(e.g. before every edit, after every tool call, when the session ends).
Configure in `.claude/settings.json` (project) or `~/.claude/settings.json`
(user). Use `/hooks` for a guided editor.

Common uses:
- Run `pytest` after every code edit
- Auto-format files on save
- Notify Slack when a long-running task finishes

---

## MCP servers

The Model Context Protocol lets Claude Code connect to *any* compatible tool
server — local Python servers (notebook 05), GitHub MCP, Linear MCP, your
group's beamline-control MCP, etc.

```bash
claude mcp add my-tools python /path/to/my_server.py    # add an MCP server
/mcp                                                     # list / inspect
```

Once added, the server's tools appear in Claude's tool list automatically —
same as any built-in.

---

## Plugins & marketplaces

`/plugins` lets you browse and install plugins (bundles of skills, agents,
hooks, MCP servers) from public or private marketplaces. Useful for sharing a
group-specific toolkit without each person installing things by hand.

---

## Safety habits

- **Permission modes**: by default Claude asks before each tool call. `acceptEdits` is convenient for trusted tasks but skips the prompts.
- **Run in a clean git state** so you can `git diff` what Claude changed.
- **Don't blindly approve `Bash(rm *)` or `git push --force`** — review the proposed command first.
- **Read what hooks do** before trusting an untrusted plugin/skill — hooks run shell commands automatically.

---

## Where to read more

- Docs: <https://docs.claude.com/en/docs/claude-code>
- Skills reference: <https://code.claude.com/docs/en/skills.md>
- Anthropic engineering blog: search for "Claude Code"
