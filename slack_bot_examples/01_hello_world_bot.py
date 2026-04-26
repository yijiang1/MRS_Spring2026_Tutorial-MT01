"""Minimal Slack echo bot.

Run:
    export SLACK_BOT_TOKEN=xoxb-...
    export SLACK_APP_TOKEN=xapp-...
    python 01_hello_world_bot.py

What it does:
- Listens for direct messages and @mentions in any channel.
- Echoes the message text back, prefixed with 'You said: '.
- Stops cleanly on Ctrl-C.

Why slack-bolt + Socket Mode:
- No public URL or webhook server required (Socket Mode opens an outbound
  WebSocket to Slack instead of receiving inbound HTTPS).
- Works fine from a laptop behind a firewall, perfect for prototyping.
"""
import os
import asyncio
import logging

from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler

logging.basicConfig(level=logging.INFO)

# slack-bolt reads SLACK_BOT_TOKEN from the environment automatically.
app = AsyncApp(token=os.environ["SLACK_BOT_TOKEN"])


@app.event("message")
async def on_dm(event, say):
    """Triggered for every message the bot can see, including its own.

    `event["channel_type"] == "im"` filters to direct messages only.
    `event.get("subtype")` filters out bot messages, edits, joins, etc.
    """
    if event.get("channel_type") != "im":
        return
    if event.get("subtype"):                 # ignore edits, bot messages, etc.
        return
    await say(f"You said: {event['text']}")


@app.event("app_mention")
async def on_mention(event, say):
    """Triggered when the bot is @mentioned in a channel."""
    # event['text'] includes the mention itself, e.g. "<@U123456> hello"
    user_text = event["text"].split(">", 1)[1].strip()
    await say(f"<@{event['user']}> you said: {user_text}")


async def main():
    handler = AsyncSocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    print("Bot is running. Send it a DM in Slack. Ctrl-C to stop.")
    await handler.start_async()


if __name__ == "__main__":
    asyncio.run(main())
