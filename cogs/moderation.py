import discord
from discord.ext import commands
from database import get_conn
import asyncio
import datetime

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        await member.kick(reason=reason)
        await ctx.send(f"👟 **{member}** has been kicked. Reason: {reason}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        await member.ban(reason=reason)
        await ctx.send(f"🔨 **{member}** has been banned. Reason: {reason}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, username):
        banned = [entry async for entry in ctx.guild.bans()]
        for entry in banned:
            if str(entry.user) == username:
                await ctx.guild.unban(entry.user)
                await ctx.send(f"✅ **{entry.user}** has been unbanned.")
                return
        await ctx.send(f"❌ User `{username}` not found in ban list.")

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, duration: int = 10, *, reason="No reason provided"):
        """Mute a member for [duration] minutes (default 10)."""
        until = discord.utils.utcnow() + datetime.timedelta(minutes=duration)
        await member.timeout(until, reason=reason)
        await ctx.send(f"🔇 **{member}** muted for {duration} minute(s). Reason: {reason}")

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member):
        await member.timeout(None)
        await ctx.send(f"🔊 **{member}** has been unmuted.")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount + 1)
        msg = await ctx.send(f"🧹 Deleted {amount} messages.")
        await asyncio.sleep(3)
        await msg.delete()

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason="No reason provided"):
        conn = get_conn()
        conn.execute(
            "INSERT INTO warnings (guild_id, user_id, reason) VALUES (?, ?, ?)",
            (ctx.guild.id, member.id, reason)
        )
        conn.commit()
        conn.close()
        await ctx.send(f"⚠️ **{member}** has been warned. Reason: {reason}")

    @commands.command()
    async def warnings(self, ctx, member: discord.Member):
        conn = get_conn()
        rows = conn.execute(
            "SELECT reason, timestamp FROM warnings WHERE guild_id=? AND user_id=?",
            (ctx.guild.id, member.id)
        ).fetchall()
        conn.close()
        if not rows:
            await ctx.send(f"✅ **{member}** has no warnings.")
            return
        embed = discord.Embed(title=f"Warnings for {member}", color=discord.Color.orange())
        for i, (reason, ts) in enumerate(rows, 1):
            embed.add_field(name=f"#{i} — {ts}", value=reason, inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
