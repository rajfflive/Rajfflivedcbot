import discord
from discord.ext import commands
import random
import asyncio

WORDS = ["python", "discord", "gaming", "server", "keyboard", "monitor", "science",
         "music", "dragon", "castle", "planet", "rocket", "jungle", "champion"]

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hangman_active = {}
        self.guess_active = {}

    # ── Rock Paper Scissors ──────────────────────────────────
    @commands.command(name="rps")
    async def rps(self, ctx, choice: str):
        """Play Rock Paper Scissors: !rps rock/paper/scissors"""
        choice = choice.lower()
        options = ["rock", "paper", "scissors"]
        if choice not in options:
            return await ctx.send("❌ Choose: `rock`, `paper`, or `scissors`")
        bot_choice = random.choice(options)
        wins = {"rock": "scissors", "paper": "rock", "scissors": "paper"}
        if choice == bot_choice:
            result = "🤝 It's a tie!"
        elif wins[choice] == bot_choice:
            result = "🎉 You win!"
        else:
            result = "😈 I win!"
        embed = discord.Embed(title="Rock Paper Scissors", color=discord.Color.blue())
        embed.add_field(name="Your choice", value=choice.capitalize(), inline=True)
        embed.add_field(name="My choice", value=bot_choice.capitalize(), inline=True)
        embed.add_field(name="Result", value=result, inline=False)
        await ctx.send(embed=embed)

    # ── Number Guessing ──────────────────────────────────────
    @commands.command(name="guess")
    async def guess(self, ctx):
        """Guess a number between 1 and 100!"""
        if ctx.channel.id in self.guess_active:
            return await ctx.send("❌ A game is already running in this channel!")
        number = random.randint(1, 100)
        self.guess_active[ctx.channel.id] = True
        attempts = 7
        await ctx.send(f"🔢 I'm thinking of a number between **1 and 100**! You have **{attempts} attempts**. Type your guess!")

        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author and m.content.isdigit()

        for attempt in range(1, attempts + 1):
            try:
                msg = await self.bot.wait_for("message", check=check, timeout=30.0)
                guessed = int(msg.content)
                if guessed == number:
                    del self.guess_active[ctx.channel.id]
                    return await ctx.send(f"🎉 Correct! You got it in **{attempt}** attempt(s)!")
                elif guessed < number:
                    remaining = attempts - attempt
                    await ctx.send(f"📈 Too low! {remaining} attempts left." if remaining > 0 else f"❌ Out of attempts! The number was **{number}**.")
                else:
                    remaining = attempts - attempt
                    await ctx.send(f"📉 Too high! {remaining} attempts left." if remaining > 0 else f"❌ Out of attempts! The number was **{number}**.")
                if attempt == attempts:
                    break
            except asyncio.TimeoutError:
                await ctx.send(f"⏰ Time's up! The number was **{number}**.")
                break
        self.guess_active.pop(ctx.channel.id, None)

    # ── Hangman ──────────────────────────────────────────────
    @commands.command(name="hangman")
    async def hangman(self, ctx):
        """Play hangman!"""
        if ctx.channel.id in self.hangman_active:
            return await ctx.send("❌ A hangman game is already running here!")

        word = random.choice(WORDS)
        guessed = set()
        wrong = 0
        max_wrong = 6
        self.hangman_active[ctx.channel.id] = True

        def display():
            return " ".join(c if c in guessed else "_" for c in word)

        def is_won():
            return all(c in guessed for c in word)

        stages = ["😵", "😦", "😟", "😨", "😰", "😱", "💀"]
        await ctx.send(f"🎯 **Hangman started!** Guess letters one at a time.\n`{display()}` — {max_wrong - wrong} lives {stages[wrong]}")

        def check(m):
            return (m.channel == ctx.channel and m.author == ctx.author
                    and len(m.content) == 1 and m.content.isalpha())

        while wrong < max_wrong:
            try:
                msg = await self.bot.wait_for("message", check=check, timeout=30.0)
                letter = msg.content.lower()
                if letter in guessed:
                    await ctx.send("⚠️ Already guessed that!")
                    continue
                guessed.add(letter)
                if letter in word:
                    if is_won():
                        del self.hangman_active[ctx.channel.id]
                        return await ctx.send(f"🎉 You won! The word was **{word}**!")
                    await ctx.send(f"✅ Correct! `{display()}`")
                else:
                    wrong += 1
                    remaining = max_wrong - wrong
                    await ctx.send(f"❌ Wrong! `{display()}` — {remaining} lives {stages[wrong]}")
            except asyncio.TimeoutError:
                await ctx.send(f"⏰ Time's up! The word was **{word}**.")
                break

        self.hangman_active.pop(ctx.channel.id, None)
        if not all(c in guessed for c in word):
            await ctx.send(f"💀 Game over! The word was **{word}**.")

    # ── Word Scramble ─────────────────────────────────────────
    @commands.command(name="scramble")
    async def scramble(self, ctx):
        """Unscramble the word!"""
        word = random.choice(WORDS)
        scrambled = list(word)
        random.shuffle(scrambled)
        scrambled_word = "".join(scrambled)
        await ctx.send(f"🔀 Unscramble this word: **{scrambled_word}**\nYou have 20 seconds!")

        def check(m):
            return m.channel == ctx.channel and m.content.lower() == word

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=20.0)
            await ctx.send(f"🎉 **{msg.author.mention}** got it! The word was **{word}**!")
        except asyncio.TimeoutError:
            await ctx.send(f"⏰ Time's up! The word was **{word}**.")

    # ── Flip a Coin ───────────────────────────────────────────
    @commands.command(name="flip")
    async def flip(self, ctx):
        """Flip a coin"""
        await ctx.send(f"🪙 **{random.choice(['Heads', 'Tails'])}!**")

    # ── Random Number ─────────────────────────────────────────
    @commands.command(name="random")
    async def random_number(self, ctx, minimum: int = 1, maximum: int = 100):
        """Generate a random number: !random 1 100"""
        if minimum >= maximum:
            return await ctx.send("❌ Minimum must be less than maximum!")
        await ctx.send(f"🎲 Random number between {minimum} and {maximum}: **{random.randint(minimum, maximum)}**")

async def setup(bot):
    await bot.add_cog(Games(bot))
