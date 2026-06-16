import discord
from discord.ext import commands
import config
from database import init_db

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=config.COMMAND_PREFIX, intents=intents)

COGS = ["cogs.moderation", "cogs.music", "cogs.fun", "cogs.custom_commands", "cogs.ai"]

@bot.event
async def on_ready():
    init_db()
    for cog in COGS:
        await bot.load_extension(cog)
    await bot.tree.sync()
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing argument: `{error.param.name}`")
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        await ctx.send(f"❌ An error occurred: {error}")

if __name__ == "__main__":
    bot.run(config.DISCORD_TOKEN)
