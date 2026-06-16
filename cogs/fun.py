import discord
from discord.ext import commands
import random
import aiohttp
import asyncio

EIGHT_BALL_RESPONSES = [
    "It is certain.", "Without a doubt.", "Yes, definitely!",
    "Most likely.", "Signs point to yes.", "Reply hazy, try again.",
    "Ask again later.", "Cannot predict now.", "Don't count on it.",
    "My reply is no.", "Very doubtful.", "Outlook not so good.",
]

TRIVIA_QUESTIONS = [
    {"q": "What is the capital of France?", "a": "paris"},
    {"q": "How many sides does a hexagon have?", "a": "6"},
    {"q": "What is the largest planet in our solar system?", "a": "jupiter"},
    {"q": "Who painted the Mona Lisa?", "a": "leonardo da vinci"},
    {"q": "What is 12 × 12?", "a": "144"},
    {"q": "What element has the symbol 'O'?", "a": "oxygen"},
    {"q": "How many continents are there?", "a": "7"},
    {"q": "What is the fastest land animal?", "a": "cheetah"},
    {"q": "Who wrote Hamlet?", "a": "shakespeare"},
    {"q": "What is the smallest country in the world?", "a": "vatican city"},
]

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.trivia_active = {}

    @commands.command(name="8ball")
    async def eight_ball(self, ctx, *, question):
        response = random.choice(EIGHT_BALL_RESPONSES)
        embed = discord.Embed(color=discord.Color.purple())
        embed.add_field(name="🎱 Question", value=question, inline=False)
        embed.add_field(name="Answer", value=response, inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def roll(self, ctx, sides: int = 6):
        """Roll a dice with [sides] sides (default 6)."""
        result = random.randint(1, sides)
        await ctx.send(f"🎲 You rolled a **{result}** (d{sides})")

    @commands.command()
    async def coinflip(self, ctx):
        result = random.choice(["Heads 🪙", "Tails 🪙"])
        await ctx.send(f"**{result}!**")

    @commands.command()
    async def meme(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://meme-api.com/gimme") as r:
                if r.status == 200:
                    data = await r.json()
                    embed = discord.Embed(title=data["title"], color=discord.Color.green())
                    embed.set_image(url=data["url"])
                    embed.set_footer(text=f"👍 {data['ups']} | r/{data['subreddit']}")
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("❌ Couldn't fetch a meme right now.")

    @commands.command()
    async def trivia(self, ctx):
        """Start a trivia question. First to answer wins!"""
        if ctx.channel.id in self.trivia_active:
            return await ctx.send("❌ A trivia question is already active in this channel!")

        question = random.choice(TRIVIA_QUESTIONS)
        self.trivia_active[ctx.channel.id] = True

        embed = discord.Embed(
            title="🧠 Trivia Time!",
            description=question["q"],
            color=discord.Color.blue()
        )
        embed.set_footer(text="You have 20 seconds to answer!")
        await ctx.send(embed=embed)

        def check(m):
            return m.channel == ctx.channel and m.content.lower() == question["a"]

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=20.0)
            await ctx.send(f"🎉 **{msg.author.mention}** got it! The answer was **{question['a']}**.")
        except asyncio.TimeoutError:
            await ctx.send(f"⏰ Time's up! The answer was **{question['a']}**.")
        finally:
            del self.trivia_active[ctx.channel.id]

    @commands.command()
    async def choose(self, ctx, *options):
        """Choose between options: !choose a b c"""
        if len(options) < 2:
            return await ctx.send("❌ Give me at least 2 options!")
        await ctx.send(f"🤔 I choose: **{random.choice(options)}**")

async def setup(bot):
    await bot.add_cog(Fun(bot))
