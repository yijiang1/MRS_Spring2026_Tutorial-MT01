"""Slack bot with Claude + tool use, talking to a real scientific tool.

Run:
    export SLACK_BOT_TOKEN=xoxb-...
    export SLACK_APP_TOKEN=xapp-...
    export ANTHROPIC_API_KEY=...
    python 03_tool_use_bot.py

What it does:
- Same per-user conversation memory + Slack threading as 02_claude_bot.
- Adds one tool: `search_recent_papers`, which hits the OpenAlex API
  (no key required) — the same tool used in tutorial notebook 08.
- Claude decides when to call it based on the user's question, runs
  the tool-use loop in the background, and posts a final answer.
- Posts a quick status reaction (hourglass) while working, then
  removes it when done — a nice UX touch on Slack.

This is roughly the smallest "scientific Slack assistant" you'd actually
ship to a research group: it answers questions, searches the literature
when relevant, and stays out of the way otherwise.
"""
import os
import json
import asyncio
import logging
from collections import defaultdict
from datetime import date, timedelta

import requests
import anthropic
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler

logging.basicConfig(level=logging.INFO)

MODEL = "claude-sonnet-4-6"
MAX_TURNS = 6                # safety cap on tool-use loop iterations
MAX_HISTORY_TURNS = 20
MAX_SLACK_CHARS = 3000
MAILTO = os.environ.get("OPENALEX_MAILTO", "your.email@example.com")

SYSTEM_PROMPT = (
    "You are a materials-science research assistant on Slack. "
    "When asked about recent papers or literature, call the "
    "`search_recent_papers` tool rather than guessing. "
    "Otherwise answer concisely from your own knowledge. "
    "Use Slack markdown: *bold*, `code`. Keep replies under 200 words."
)

# ---- Tool definition (schema sent to Claude) ----
TOOLS = [{
    "name": "search_recent_papers",
    "description": "Search OpenAlex for recent scientific papers matching a query. "
                   "Returns title, authors, date, journal, and abstract.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query":       {"type": "string"},
            "since":       {"type": "string",
                            "description": "ISO date YYYY-MM-DD (default: 1 year ago)"},
            "max_results": {"type": "integer", "default": 5},
        },
        "required": ["query"],
    },
}]


def reconstruct_abstract(idx):
    if not idx:
        return ""
    pos = [(p, w) for w, ps in idx.items() for p in ps]
    pos.sort()
    return " ".join(w for _, w in pos)


def search_recent_papers(query: str, since: str = None,
                         max_results: int = 5) -> str:
    """Synchronous OpenAlex call. Returns JSON string for tool_result."""
    if since is None:
        since = (date.today() - timedelta(days=365)).isoformat()
    r = requests.get(
        "https://api.openalex.org/works",
        params={
            "search":  query,
            "filter":  f"from_publication_date:{since},type:article",
            "sort":    "publication_date:desc",
            "per_page": max_results,
            "mailto":  MAILTO,
        },
        timeout=30,
    )
    r.raise_for_status()
    out = []
    for w in r.json()["results"]:
        out.append({
            "title":   w.get("title", ""),
            "authors": ", ".join(a["author"]["display_name"]
                                 for a in w.get("authorships", [])[:5]),
            "date":    w.get("publication_date", ""),
            "journal": ((w.get("primary_location") or {}).get("source") or {})
                       .get("display_name", ""),
            "doi":     (w.get("doi") or "").replace("https://doi.org/", ""),
            "abstract": reconstruct_abstract(w.get("abstract_inverted_index"))[:600],
        })
    return json.dumps(out)


HANDLERS = {"search_recent_papers": search_recent_papers}

# ---- Bolt app + Claude client + per-user history ----
app = AsyncApp(token=os.environ["SLACK_BOT_TOKEN"])
client = anthropic.AsyncAnthropic()
HISTORY: dict[str, list[dict]] = defaultdict(list)


def chunk(text: str, limit: int = MAX_SLACK_CHARS) -> list[str]:
    if len(text) <= limit:
        return [text]
    chunks, buf = [], ""
    for para in text.split("\n\n"):
        if len(buf) + len(para) + 2 > limit:
            chunks.append(buf.rstrip()); buf = para + "\n\n"
        else:
            buf += para + "\n\n"
    if buf.strip():
        chunks.append(buf.rstrip())
    return chunks


async def claude_with_tools(user_id: str, user_text: str) -> str:
    """Run a tool-use loop until Claude is done, then return the final text."""
    history = HISTORY[user_id]
    history.append({"role": "user", "content": user_text})
    history[:] = history[-MAX_HISTORY_TURNS:]

    for _ in range(MAX_TURNS):
        resp = await client.messages.create(
            model=MODEL, max_tokens=1024,
            system=SYSTEM_PROMPT, tools=TOOLS,
            messages=history,
        )
        history.append({"role": "assistant", "content": resp.content})
        tool_uses = [b for b in resp.content if b.type == "tool_use"]
        if not tool_uses:
            return "".join(b.text for b in resp.content if b.type == "text")

        results = []
        for tu in tool_uses:
            try:
                payload = HANDLERS[tu.name](**tu.input)
            except Exception as e:
                payload = json.dumps({"error": str(e)})
            results.append({"type": "tool_result", "tool_use_id": tu.id,
                            "content": payload})
        history.append({"role": "user", "content": results})

    return "[ran out of turns — sorry]"


async def handle(event, say, client_):
    user_id = event["user"]
    channel = event["channel"]
    msg_ts  = event["ts"]
    thread_ts = event.get("thread_ts") or msg_ts

    text = event.get("text", "")
    if text.startswith("<@"):
        text = text.split(">", 1)[1].strip()
    if not text:
        return
    if text.lower() in {"clear", "reset", "forget"}:
        HISTORY.pop(user_id, None)
        await say(text="🧹 Cleared our conversation.", thread_ts=thread_ts)
        return

    # UX nicety: hourglass reaction while we work
    try:
        await client_.reactions_add(channel=channel, timestamp=msg_ts,
                                    name="hourglass_flowing_sand")
    except Exception:
        pass

    try:
        reply = await claude_with_tools(user_id, text)
        for piece in chunk(reply):
            await say(text=piece, thread_ts=thread_ts)
    except Exception as e:
        await say(text=f"⚠️ Error: `{e}`", thread_ts=thread_ts)
    finally:
        try:
            await client_.reactions_remove(channel=channel, timestamp=msg_ts,
                                           name="hourglass_flowing_sand")
        except Exception:
            pass


@app.event("message")
async def on_dm(event, say, client):
    if event.get("channel_type") != "im" or event.get("subtype"):
        return
    await handle(event, say, client)


@app.event("app_mention")
async def on_mention(event, say, client):
    await handle(event, say, client)


async def main():
    handler = AsyncSocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    print(f"Tool-use bot running with model {MODEL}. Try: "
          "'find recent ptychography papers'. Ctrl-C to stop.")
    await handler.start_async()


if __name__ == "__main__":
    asyncio.run(main())
