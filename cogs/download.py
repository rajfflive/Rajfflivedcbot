import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os
import shutil
import re

FFMPEG_PATH = shutil.which("ffmpeg") or "/usr/local/bin/ffmpeg"
MAX_SIZE_MB = 8

def safe_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)[:50]

YTDL_AUDIO_OPTIONS = {
    "format": "bestaudio/best",
    "outtmpl": "/tmp/dlbot_%(id)s.%(ext)s",
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
    "format": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best[height<=480]",
    "outtmpl": "/tmp/dlbot_%(id)s.%(ext)s",
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
        search = query if query.startswith("http") else f"ytsearch1:{query}"

        try:
            def do_download():
                with yt_dlp.YoutubeDL(YTDL_AUDIO_OPTIONS) as ydl:
                    info = ydl.extract_info(search, download=True)
                    if "entries" in info:
                        info = info["entries"][0]
                    video_id = info.get("id", "audio")
                    title = info.get("title", "audio")
                    return video_id, title

            video_id, title = await loop.run_in_executor(None, do_download)

            filepath = None
            for f in os.listdir("/tmp"):
                if f.startswith(f"dlbot_{video_id}") and f.endswith(".mp3"):
                    filepath = f"/tmp/{f}"
                    break

            if not filepath:
                mp3s = [f"/tmp/{f}" for f in os.listdir("/tmp") if f.startswith("dlbot_") and f.endswith(".mp3")]
                if mp3s:
                    filepath = max(mp3s, key=os.path.getmtime)
                else:
                    return await msg.edit(content="❌ Download failed. File not found.")

            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            if size_mb > MAX_SIZE_MB:
                os.remove(filepath)
                return await msg.edit(content=f"❌ File too large ({size_mb:.1f}MB). Discord limit is {MAX_SIZE_MB}MB.")

            safe_title = safe_filename(title)
            await msg.edit(content=f"✅ Uploading **{safe_title}.mp3**...")
            await ctx.send(file=discord.File(filepath, filename=f"{safe_title}.mp3"))

        except Exception as e:
            await msg.edit(content=f"❌ Error: {e}")
        finally:
            for f in os.listdir("/tmp"):
                if f.startswith("dlbot_"):
                    try:
                        os.remove(f"/tmp/{f}")
                    except:
                        pass

    @commands.command(name="dlvideo")
    async def download_video(self, ctx, *, query: str):
        """Download a video (max 480p): !dlvideo <title or URL>"""
        msg = await ctx.send(f"⏳ Searching and downloading video **{query}**...")
        loop = asyncio.get_event_loop()
        search = query if query.startswith("http") else f"ytsearch1:{query}"

        try:
            def do_download():
                with yt_dlp.YoutubeDL(YTDL_VIDEO_OPTIONS) as ydl:
                    info = ydl.extract_info(search, download=True)
                    if "entries" in info:
                        info = info["entries"][0]
                    video_id = info.get("id", "video")
                    title = info.get("title", "video")
                    return video_id, title

            video_id, title = await loop.run_in_executor(None, do_download)

            filepath = None
            for f in os.listdir("/tmp"):
                if f.startswith(f"dlbot_{video_id}") and f.endswith(".mp4"):
                    filepath = f"/tmp/{f}"
                    break

            if not filepath:
                mp4s = [f"/tmp/{f}" for f in os.listdir("/tmp") if f.startswith("dlbot_") and f.endswith(".mp4")]
                if mp4s:
                    filepath = max(mp4s, key=os.path.getmtime)
                else:
                    return await msg.edit(content="❌ Download failed. File not found.")

            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            if size_mb > MAX_SIZE_MB:
                os.remove(filepath)
                return await msg.edit(content=f"❌ File too large ({size_mb:.1f}MB). Try `!dlmp3` for audio only.")

            safe_title = safe_filename(title)
            await msg.edit(content=f"✅ Uploading **{safe_title}.mp4**...")
            await ctx.send(file=discord.File(filepath, filename=f"{safe_title}.mp4"))

        except Exception as e:
            await msg.edit(content=f"❌ Error: {e}")
        finally:
            for f in os.listdir("/tmp"):
                if f.startswith("dlbot_"):
                    try:
                        os.remove(f"/tmp/{f}")
                    except:
                        pass

async def setup(bot):
    await bot.add_cog(Download(bot))
