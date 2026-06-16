import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os
import shutil

FFMPEG_PATH = shutil.which("ffmpeg") or "/usr/local/bin/ffmpeg"
MAX_SIZE_MB = 8

YTDL_AUDIO_OPTIONS = {
    "format": "bestaudio/best",
    "outtmpl": "/tmp/%(title)s.%(ext)s",
    "quiet": True,
    "noplaylist": True,
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "128",
    }],
    "ffmpeg_location": FFMPEG_PATH,
    "extractor_args": {
        "youtube": {
            "player_client": ["android"],
            "player_skip": ["webpage"]
        }
    },
}

YTDL_VIDEO_OPTIONS = {
    "format": "bestvideo[height<=480]+bestaudio/best[height<=480]",
    "outtmpl": "/tmp/%(title)s.%(ext)s",
    "quiet": True,
    "noplaylist": True,
    "merge_output_format": "mp4",
    "ffmpeg_location": FFMPEG_PATH,
    "extractor_args": {
        "youtube": {
            "player_client": ["android"],
            "player_skip": ["webpage"]
        }
    },
}

class Download(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="dlmp3")
    async def download_audio(self, ctx, *, query: str):
        """Download a song as MP3: !dlmp3 <song name or URL>"""
        msg = await ctx.send(f"⏳ Searching and downloading **{query}**...")
        loop = asyncio.get_event_loop()

        search = query if query.startswith("http") else f"ytsearch:{query}"
        filepath = None

        try:
            def do_download():
                with yt_dlp.YoutubeDL(YTDL_AUDIO_OPTIONS) as ydl:
                    info = ydl.extract_info(search, download=True)
                    if "entries" in info:
                        info = info["entries"][0]
                    title = info.get("title", "audio")
                    expected = f"/tmp/{title}.mp3"
                    return expected, title

            filepath, title = await loop.run_in_executor(None, do_download)

            if not os.path.exists(filepath):
                mp3s = [f for f in os.listdir("/tmp") if f.endswith(".mp3")]
                if mp3s:
                    filepath = f"/tmp/{mp3s[-1]}"
                else:
                    return await msg.edit(content="❌ Download failed. File not found.")

            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            if size_mb > MAX_SIZE_MB:
                os.remove(filepath)
                return await msg.edit(content=f"❌ File too large ({size_mb:.1f}MB). Discord limit is {MAX_SIZE_MB}MB.")

            await msg.edit(content=f"✅ Downloaded! Uploading **{os.path.basename(filepath)}**...")
            await ctx.send(file=discord.File(filepath))

        except Exception as e:
            await msg.edit(content=f"❌ Error: {e}")
        finally:
            if filepath and os.path.exists(filepath):
                os.remove(filepath)

    @commands.command(name="dlvideo")
    async def download_video(self, ctx, *, query: str):
        """Download a video (max 480p): !dlvideo <title or URL>"""
        msg = await ctx.send(f"⏳ Searching and downloading video **{query}**...")
        loop = asyncio.get_event_loop()

        search = query if query.startswith("http") else f"ytsearch:{query}"
        filepath = None

        try:
            def do_download():
                with yt_dlp.YoutubeDL(YTDL_VIDEO_OPTIONS) as ydl:
                    info = ydl.extract_info(search, download=True)
                    if "entries" in info:
                        info = info["entries"][0]
                    title = info.get("title", "video")
                    expected = f"/tmp/{title}.mp4"
                    return expected, title

            filepath, title = await loop.run_in_executor(None, do_download)

            if not os.path.exists(filepath):
                mp4s = [f for f in os.listdir("/tmp") if f.endswith(".mp4")]
                if mp4s:
                    filepath = f"/tmp/{mp4s[-1]}"
                else:
                    return await msg.edit(content="❌ Download failed. File not found.")

            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            if size_mb > MAX_SIZE_MB:
                os.remove(filepath)
                return await msg.edit(content=f"❌ File too large ({size_mb:.1f}MB). Discord limit is {MAX_SIZE_MB}MB. Try `!dlmp3` for audio only.")

            await msg.edit(content=f"✅ Downloaded! Uploading **{os.path.basename(filepath)}**...")
            await ctx.send(file=discord.File(filepath))

        except Exception as e:
            await msg.edit(content=f"❌ Error: {e}")
        finally:
            if filepath and os.path.exists(filepath):
                os.remove(filepath)

async def setup(bot):
    await bot.add_cog(Download(bot))
