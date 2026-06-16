import discord
from discord.ext import commands
from database import get_conn

class CustomCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="addcmd")
    @commands.has_permissions(manage_guild=True)
    async def add_command(self, ctx, trigger: str, *, response: str):
        """Add a custom command: !addcmd <trigger> <response>"""
        conn = get_conn()
        conn.execute(
            "INSERT OR REPLACE INTO custom_commands (guild_id, trigger, response) VALUES (?, ?, ?)",
            (ctx.guild.id, trigger.lower(), response)
        )
        conn.commit()
        conn.close()
        await ctx.send(f"✅ Custom command `!{trigger}` added!")

    @commands.command(name="delcmd")
    @commands.has_permissions(manage_guild=True)
    async def delete_command(self, ctx, trigger: str):
        """Delete a custom command: !delcmd <trigger>"""
        conn = get_conn()
        conn.execute(
            "DELETE FROM custom_commands WHERE guild_id=? AND trigger=?",
            (ctx.guild.id, trigger.lower())
        )
        conn.commit()
        conn.close()
        await ctx.send(f"🗑️ Custom command `!{trigger}` removed.")

    @commands.command(name="listcmds")
    async def list_commands(self, ctx):
        """List all custom commands for this server."""
        conn = get_conn()
        rows = conn.execute(
            "SELECT trigger FROM custom_commands WHERE guild_id=?",
            (ctx.guild.id,)
        ).fetchall()
        conn.close()
        if not rows:
            return await ctx.send("📋 No custom commands set up yet.")
        cmds = ", ".join(f"`!{r[0]}`" for r in rows)
        await ctx.send(f"📋 **Custom Commands:** {cmds}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        if not message.content.startswith("!"):
            return
        trigger = message.content[1:].split()[0].lower()
        conn = get_conn()
        row = conn.execute(
            "SELECT response FROM custom_commands WHERE guild_id=? AND trigger=?",
            (message.guild.id, trigger)
        ).fetchone()
        conn.close()
        if row:
            await message.channel.send(row[0])

async def setup(bot):
    await bot.add_cog(CustomCommands(bot))
