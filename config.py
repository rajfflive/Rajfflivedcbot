import os

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
COMMAND_PREFIX = os.environ.get("COMMAND_PREFIX", "!")

if not DISCORD_TOKEN:
    raise ValueError("❌ DISCORD_TOKEN not set!")
if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY not set!")
