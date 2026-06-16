import discord
from discord.ext import commands
import anthropic
import config

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self.conversations = {}

    def ask_claude_sync(self, user_id: int, user_message: str) -> str:
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        self.conversations[user_id].append({"role": "user", "content": user_message})
        history = self.conversations[user_id][-10:]
        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system="You are a helpful and friendly Discord bot assistant. Keep responses concise and suitable for chat.",
            messages=history
        )
        reply = response.content[0].text
        self.conversations[user_id].append({"role": "assistant", "content": reply})
        return reply

    @commands.command(name="ask")
    async def ask(self, ctx, *, question: str):
        async with ctx.typing():
            try:
                reply = await self.bot.loop.run_in_executor(
                    None, lambda: self.ask_claude_sync(ctx.author.id, question)
                )
                if len(reply) > 2000:
                    for chunk in [reply[i:i+1990] for i in range(0, len(reply), 1990)]:
                        await ctx.send(chunk)
                else:
                    await ctx.send(reply)
            except Exception as e:
                await ctx.send(f"❌ Error: {e}")

    @commands.command(name="chat")
    async def chat(self, ctx, *, message: str):
        async with ctx.typing():
            try:
                reply = await self.bot.loop.run_in_executor(
                    None, lambda: self.ask_claude_sync(ctx.author.id, message)
                )
                if len(reply) > 2000:
                    for chunk in [reply[i:i+1990] for i in range(0, len(reply), 1990)]:
                        await ctx.send(chunk)
                else:
                    await ctx.send(reply)
            except Exception as e:
                await ctx.send(f"❌ Error: {e}")

    @commands.command(name="clearchat")
    async def clear_chat(self, ctx):
        self.conversations.pop(ctx.author.id, None)
        await ctx.send("🧹 Conversation history cleared.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if self.bot.user in message.mentions:
            content = message.content.replace(f"<@{self.bot.user.id}>", "").strip()
            if not content:
                return await message.channel.send("Hey! Use `!ask <question>` or mention me with a question.")
            async with message.channel.typing():
                try:
                    reply = await self.bot.loop.run_in_executor(
                        None, lambda: self.ask_claude_sync(message.author.id, content)
                    )
                    await message.channel.send(reply)
                except Exception as e:
                    await message.channel.send(f"❌ Error: {e}")

async def setup(bot):
    await bot.add_cog(AI(bot))
