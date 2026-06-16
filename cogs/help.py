import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.remove_command("help")

    @commands.command(name="help")
    async def help_command(self, ctx, category: str = None):
        """Show all commands: !help or !help <category>"""
        prefix = "!"

        if category is None:
            embed = discord.Embed(
                title="📖 Bot Commands",
                description=f"Use `{prefix}help <category>` for details.\nPrefix: `{prefix}`",
                color=discord.Color.blurple()
            )
            embed.add_field(name="🎵 Music", value="`!help music`", inline=True)
            embed.add_field(name="🤖 AI", value="`!help ai`", inline=True)
            embed.add_field(name="🎮 Games", value="`!help games`", inline=True)
            embed.add_field(name="⬇️ Download", value="`!help download`", inline=True)
            embed.add_field(name="🛡️ Moderation", value="`!help mod`", inline=True)
            embed.add_field(name="🎉 Fun", value="`!help fun`", inline=True)
            embed.add_field(name="⚙️ Custom Cmds", value="`!help custom`", inline=True)
            embed.set_footer(text=f"Bot by {ctx.guild.name}")
            return await ctx.send(embed=embed)

        category = category.lower()

        if category == "music":
            embed = discord.Embed(title="🎵 Music Commands", color=discord.Color.green())
            cmds = [
                ("!play <song>", "Play a song from YouTube"),
                ("!pause", "Pause current song"),
                ("!resume", "Resume paused song"),
                ("!skip", "Skip current song"),
                ("!stop", "Stop and clear queue"),
                ("!queue", "Show song queue"),
                ("!volume <0-100>", "Set volume"),
                ("!join", "Join your voice channel"),
                ("!leave", "Leave voice channel"),
            ]
        elif category == "ai":
            embed = discord.Embed(title="🤖 AI Commands", color=discord.Color.purple())
            cmds = [
                ("!ask <question>", "Ask the AI anything"),
                ("!chat <message>", "Chat with AI"),
                ("!clearchat", "Clear AI conversation history"),
                ("@BotName <message>", "Mention bot to chat with AI"),
            ]
        elif category == "games":
            embed = discord.Embed(title="🎮 Game Commands", color=discord.Color.gold())
            cmds = [
                ("!rps <rock/paper/scissors>", "Play Rock Paper Scissors"),
                ("!guess", "Guess a number (1-100)"),
                ("!hangman", "Play Hangman"),
                ("!scramble", "Unscramble a word"),
                ("!flip", "Flip a coin"),
                ("!random <min> <max>", "Random number generator"),
            ]
        elif category == "download":
            embed = discord.Embed(title="⬇️ Download Commands", color=discord.Color.red())
            cmds = [
                ("!dlmp3 <song name>", "Download song as MP3 (max 8MB)"),
                ("!dlvideo <video name>", "Download video as MP4 (max 8MB, 480p)"),
            ]
        elif category in ("mod", "moderation"):
            embed = discord.Embed(title="🛡️ Moderation Commands", color=discord.Color.dark_red())
            cmds = [
                ("!kick <user> <reason>", "Kick a member"),
                ("!ban <user> <reason>", "Ban a member"),
                ("!unban <username>", "Unban a member"),
                ("!mute <user> <mins>", "Timeout a member"),
                ("!unmute <user>", "Remove timeout"),
                ("!warn <user> <reason>", "Warn a member"),
                ("!warnings <user>", "View member warnings"),
                ("!purge <amount>", "Delete messages"),
            ]
        elif category == "fun":
            embed = discord.Embed(title="🎉 Fun Commands", color=discord.Color.orange())
            cmds = [
                ("!8ball <question>", "Ask the magic 8ball"),
                ("!roll <sides>", "Roll a dice"),
                ("!coinflip", "Flip a coin"),
                ("!meme", "Get a random meme"),
                ("!trivia", "Answer a trivia question"),
                ("!choose <a> <b> <c>", "Bot picks one option"),
            ]
        elif category == "custom":
            embed = discord.Embed(title="⚙️ Custom Commands", color=discord.Color.teal())
            cmds = [
                ("!addcmd <name> <response>", "Add a custom command"),
                ("!delcmd <name>", "Delete a custom command"),
                ("!listcmds", "List all custom commands"),
            ]
        else:
            return await ctx.send("❌ Unknown category. Use: `music`, `ai`, `games`, `download`, `mod`, `fun`, `custom`")

        for name, desc in cmds:
            embed.add_field(name=f"`{name}`", value=desc, inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))
