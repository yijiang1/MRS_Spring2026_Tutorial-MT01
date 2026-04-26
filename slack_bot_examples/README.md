# Slack bot examples for MRS Tutorial MT01

Three runnable Slack bots at increasing complexity. Walked through in
[`../10_slack_bot.ipynb`](../10_slack_bot.ipynb).

| File | What it does | Lines |
|---|---|---|
| `01_hello_world_bot.py` | Echoes any DM or @mention back to the user | ~50 |
| `02_claude_bot.py` | Wired to Claude with per-user conversation memory + threading | ~100 |
| `03_tool_use_bot.py` | Adds a literature-search tool (OpenAlex) so the bot can answer "find me papers about X" | ~180 |

All three use **slack-bolt** in **Socket Mode** (long-lived outbound
WebSocket — no public URL, no webhook server, works behind a firewall).

## One-time setup

### 1. Create the Slack app

1. <https://api.slack.com/apps> → *Create New App* → *From scratch*
2. Name it (e.g. *MRS Tutorial Bot*), pick your workspace
3. **Socket Mode** (left sidebar) → toggle on → generate an *App-Level
   Token* with the `connections:write` scope. Copy this — it starts with
   `xapp-...`. This is your `SLACK_APP_TOKEN`.
4. **OAuth & Permissions** → under *Bot Token Scopes*, add:
   - `app_mentions:read`
   - `chat:write`
   - `im:history`
   - `im:read`
   - `im:write`
   - `reactions:write` *(only needed for `03_tool_use_bot.py`)*
5. **Event Subscriptions** → enable. Under *Subscribe to bot events* add:
   - `app_mention`
   - `message.im`
6. **Install App** (top of the OAuth page) → install to your workspace.
   Copy the *Bot User OAuth Token* — starts with `xoxb-...`. This is
   your `SLACK_BOT_TOKEN`.

### 2. Install Python deps

```bash
pip install slack-bolt aiohttp anthropic requests
```

### 3. Set environment variables and run

```bash
export SLACK_BOT_TOKEN=xoxb-...
export SLACK_APP_TOKEN=xapp-...
export ANTHROPIC_API_KEY=...           # for 02 and 03
export OPENALEX_MAILTO=you@inst.edu    # for 03 (polite-pool etiquette)

python 01_hello_world_bot.py
# in another terminal: DM your bot in Slack, or @mention it in a channel
```

Stop with **Ctrl-C**.

### 4. Talk to your bot in Slack

- Find the bot in Slack's left sidebar under *Apps*, click to start a DM.
- Or invite it to a channel and `@MentionTheBotByName some question`.

## Common gotchas

| Symptom | Likely cause |
|---|---|
| `not_authed` or `invalid_auth` | Wrong token. `SLACK_APP_TOKEN` is `xapp-`, `SLACK_BOT_TOKEN` is `xoxb-`. They are not interchangeable. |
| Bot doesn't react in a channel | Forgot to invite it (`/invite @yourbot`) or to subscribe to `app_mention` |
| Bot doesn't react in DM | Missing `im:history`, `im:read`, or `message.im` event subscription |
| `missing_scope` error from API call | Re-add the scope in *OAuth & Permissions* and **reinstall** the app to pick up new scopes |
| Bot runs but nothing prints | You're looking at the wrong console — check the one running `python 0X_bot.py` |
| Replies come from `Slackbot` instead of yours | Slack's built-in bot, not yours. Make sure you DM your *app's* bot, not the system Slackbot |

## Production-shaped patterns these omit

- Persistence across restarts (use SQLite/Postgres for `HISTORY`)
- Per-user rate limits / quotas
- File upload handling (`files_upload_v2`)
- Slash commands (`/summarise`, `/find-paper`, etc.)
- Multi-workspace install via OAuth (these are single-workspace bots)
- Health checks, metrics, structured logging
- Graceful shutdown and reconnect-on-network-error

The `services/slack_bot_agent.py` in
<https://github.com/yijiang1/MIC_Data_Analysis_FAQ> shows what most of
these look like in production.
