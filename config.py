import os

# Bot Settings
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
COMMAND_PREFIX = os.environ.get("COMMAND_PREFIX", "!")

# Validate required vars
if not DISCORD_TOKEN:
    raise ValueError("❌ DISCORD_TOKEN is not set in environment variables!")
if not ANTHROPIC_API_KEY:
    raise ValueError("❌ ANTHROPIC_API_KEY is not set in environment variables!")
