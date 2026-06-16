import os

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
COMMAND_PREFIX = os.environ.get("COMMAND_PREFIX", "!")

if not DISCORD_TOKEN:
    raise ValueError("❌ DISCORD_TOKEN not set!")
if not OPENROUTER_API_KEY:
    raise ValueError("❌ OPENROUTER_API_KEY not set!")
