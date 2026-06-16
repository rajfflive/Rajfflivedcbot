import discord
from discord.ext import commands
import yt_dlp
import asyncio
import shutil
from collections import deque

FFMPEG_PATH = shutil.which("ffmpeg") or "/usr/local/bin/ffmpeg"

YTDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "default_search": "ytsearch",
    "source_address": "0.0.0.0",
    "extractor_args": {
        "youtube": {
            "player_client": ["android"],
            "player_skip": ["webpage"]
        }
    },
    "http_headers": {
        "User-Agent": "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 Chrome/90.0.4430.91 Mobile Safari/537.36"
    },
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}

    def get_queue(self, guild_id):
        if guild_id not in self.queues:
            self.queues[guild_id] = deque()
        return self.queues[guild_id]

    async def play_next(self, ctx):
        queue = self.get_queue(ctx.guild.id)
        if not queue:
            await ctx.send("✅ Queue finished!")
            return
        url, title = queue.popleft()
        await self._stream(ctx, url, title)

    async def _stream(self, ctx, url, title):
        vc = ctx.voice_client
        loop = asyncio.get_event_loop()
        try:
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        except Exception as e:
            return await ctx.send(f"❌ Could not load audio: {e}")

        if "formats" in data:
            stream_url = next(
                (f["url"] for f in data["formats"] if f.get("acodec") != "none"),
                data.get("url")
            )
        else:
            stream_url = data.get("url")

        if not stream_url:
            return await ctx.send("❌ Could not get stream URL. Try another song.")

        source = discord.FFmpegPCMAudio(stream_url, executable=FFMPEG_PATH, **FFMPEG_OPTIONS)
        source = discord.PCMVolumeTransformer(source, volume=0.5)

        def after(error):
            asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop)

        vc.play(source, after=after)
        await ctx.send(f"🎵 Now playing: **{title}**")

    @commands.command()
    async def join(self, ctx):
        if not ctx.author.voice:
            return await ctx.send("❌ You're not in a voice channel!")
        channel = ctx.author.voice.channel
        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()
        await ctx.send(f"✅ Joined **{channel.name}**")

    @commands.command()
    async def play(self, ctx, *, query):
        if not ctx.voice_client:
            if not ctx.author.voice:
                return await ctx.send("❌ Join a voice channel first!")
            await ctx.author.voice.channel.connect()
        async with ctx.typing():
            loop = asyncio.get_event_loop()
            try:
                data = await loop.run_in_executor(None, lambda: ytdl.extract_info(f"ytsearch:{query}", download=False))
            except Exception as e:
                return await ctx.send(f"❌ Search failed: {e}")
            entries = data.get("entries", [])
            if not entries:
                return await ctx.send("❌ No results found. Try a different song name.")
            entry = entries[0]
            url = entry.get("webpage_url") or entry.get("url")
            title = entry.get("title", query)
        if ctx.voice_client.is_playing():
            self.get_queue(ctx.guild.id).append((url, title))
            await ctx.send(f"📋 Added to queue: **{title}**")
        else:
            await self._stream(ctx, url, title)

    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("⏭️ Skipped!")
        else:
            await ctx.send("❌ Nothing is playing.")

    @commands.command()
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("⏸️ Paused.")

    @commands.command()
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("▶️ Resumed.")

    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client:
            self.get_queue(ctx.guild.id).clear()
            ctx.voice_client.stop()
            await ctx.send("⏹️ Stopped and cleared queue.")

    @commands.command()
    async def queue(self, ctx):
        q = self.get_queue(ctx.guild.id)
        if not q:
            return await ctx.send("📋 Queue is empty.")
        lines = [f"{i+1}. {title}" for i, (_, title) in enumerate(q)]
        await ctx.send("📋 **Queue:**\n" + "\n".join(lines))

    @commands.command()
    async def volume(self, ctx, vol: int):
        if not ctx.voice_client or not ctx.voice_client.source:
            return await ctx.send("❌ Nothing is playing.")
        ctx.voice_client.source.volume = max(0, min(vol, 100)) / 100
        await ctx.send(f"🔊 Volume set to {vol}%")

    @commands.command()
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("👋 Left the voice channel.")

async def setup(bot):
    await bot.add_cog(MusicCog(bot))
