"""Slack bot wired to Claude with per-user conversation memory.

Run:
    export SLACK_BOT_TOKEN=xoxb-...
    export SLACK_APP_TOKEN=xapp-...
    export ANTHROPIC_API_KEY=...
    python 02_claude_bot.py

What it does:
- Receives a DM or @mention.
- Looks up that user's prior chat history (in-process dict).
- Sends the full conversation to Claude with a system prompt.
- Posts the response back, chunked if Slack's 3000-char message limit is hit.
- Posts in the same thread as the user's message (if any) so threads stay tidy.

This is the smallest interesting "scientific Slack bot" — it remembers
context within a session and feels conversational. Production extras
(persistence across restarts, multi-user quotas, tool use) come next.
"""
import os
import asyncio
import logging
from collections import defaultdict

import anthropic
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler

logging.basicConfig(level=logging.INFO)

MODEL = "claude-sonnet-4-6"
MAX_HISTORY_TURNS = 20      # cap on user+assistant messages kept per user
MAX_SLACK_CHARS = 3000      # Slack's per-message text limit (well under 4000)

SYSTEM_PROMPT = (
    "You are a helpful materials-science research assistant on Slack. "
    "Keep replies concise (under 200 words unless asked for more). "
    "Use Slack markdown: *bold*, _italic_, `code`, and ```code blocks```. "
    "Do not pretend to access tools you do not have."
)

app = AsyncApp(token=os.environ["SLACK_BOT_TOKEN"])
client = anthropic.AsyncAnthropic()

# Per-user in-process conversation store. Lost on restart — fine for a demo;
# in production back this with SQLite, Redis, etc.
HISTORY: dict[str, list[dict]] = defaultdict(list)


def chunk(text: str, limit: int = MAX_SLACK_CHARS) -> list[str]:
    """Split a long reply on paragraph boundaries to fit Slack's limit."""
    if len(text) <= limit:
        return [text]
    chunks, buf = [], ""
    for para in text.split("\n\n"):
        if len(buf) + len(para) + 2 > limit:
            chunks.append(buf.rstrip())
            buf = para + "\n\n"
        else:
            buf += para + "\n\n"
    if buf.strip():
        chunks.append(buf.rstrip())
    return chunks


async def claude_reply(user_id: str, user_text: str) -> str:
    """Append user_text to history, call Claude, append + return the reply."""
    history = HISTORY[user_id]
    history.append({"role": "user", "content": user_text})
    # Trim to last N turns to keep context small
    history[:] = history[-MAX_HISTORY_TURNS:]

    resp = await client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=history,
    )
    reply = "".join(b.text for b in resp.content if b.type == "text")
    history.append({"role": "assistant", "content": reply})
    return reply


async def handle(event, say):
    user_id = event["user"]
    text = event.get("text", "")
    # Strip the leading "<@BOTID>" if this came from an @mention
    if text.startswith("<@"):
        text = text.split(">", 1)[1].strip()

    if text.lower() in {"clear", "reset", "forget"}:
        HISTORY.pop(user_id, None)
        await say(text="🧹 Cleared our conversation history.",
                  thread_ts=event.get("thread_ts") or event.get("ts"))
        return

    try:
        reply = await claude_reply(user_id, text)
    except Exception as e:
        await say(text=f"⚠️ Error: `{e}`")
        return

    # Reply in-thread if the user opened one; otherwise top-level
    thread_ts = event.get("thread_ts") or event.get("ts")
    for piece in chunk(reply):
        await say(text=piece, thread_ts=thread_ts)


@app.event("message")
async def on_dm(event, say):
    if event.get("channel_type") != "im" or event.get("subtype"):
        return
    await handle(event, say)


@app.event("app_mention")
async def on_mention(event, say):
    await handle(event, say)


async def main():
    handler = AsyncSocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    print(f"Bot is running with model {MODEL}. Type 'clear' to reset history. Ctrl-C to stop.")
    await handler.start_async()


if __name__ == "__main__":
    asyncio.run(main())
