import asyncio
import os
import re
import json
import random
from typing import Union

import aiohttp
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch

import config
from SONALI.utils.database import is_on_off
from SONALI.utils.formatters import time_to_seconds

# --- YOUR API CONFIGURATION ---
# IMPORTANT: Replace "YOUR_API_KEY" with your actual API key
API_KEY = os.getenv("API_KEY", "tnc_9a13260003bfaa27f9432cd47c0491bb") 
API_BASE_URL = "https://tnc-api.me/api/v1"
# --- END OF CONFIGURATION ---


def get_video_id_from_url(url: str):
    """A robust function to extract the video ID from any YouTube URL."""
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

async def get_stream_link_from_api(full_url: str, is_video: bool):
    """
    A single, reliable function to fetch the stream link from your API.
    """
    video_id = get_video_id_from_url(full_url)
    if not video_id:
        raise Exception("Could not extract video ID from the URL.")
    
    endpoint = "video" if is_video else "audio"
    api_url = f"{API_BASE_URL}/{endpoint}/{video_id}?api_key={API_KEY}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                response.raise_for_status()
                data = await response.json()
                if data.get("success") and data.get("data", {}).get("link"):
                    return data["data"]["link"]
                else:
                    error_message = data.get("data", {}).get("message", "Unknown API Error")
                    raise Exception(f"API Error: {error_message}")
    except Exception as e:
        # Re-raise the exception so it can be caught by the calling function in stream.py
        raise e

# The original helper functions that are still needed for other parts of the bot
def cookie_txt_file():
    cookie_dir = f"{os.getcwd()}/cookies"
    if not os.path.exists(cookie_dir): return None
    cookies_files = [f for f in os.listdir(cookie_dir) if f.endswith(".txt")]
    if not cookies_files: return None
    return os.path.join(cookie_dir, random.choice(cookies_files))

async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    out, errorz = await proc.communicate()
    if errorz:
        if "unavailable videos are hidden" in (errorz.decode("utf-8")).lower():
            return out.decode("utf-8")
        else:
            return errorz.decode("utf-8")
    return out.decode("utf-8")


class YouTubeAPI:
    """
    This class handles all YouTube interactions.
    We are only replacing the 'download' method. All other methods for searching,
    getting details, and handling playlists remain untouched to ensure stability.
    """

    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def url(self, message_1: Message) -> Union[str, None]:
        # This method is unchanged
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        text = ""
        offset = None
        length = None
        for message in messages:
            if offset: break
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text, offset, length = message.text, entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        if offset is None: return None
        return text[offset : offset + length]

    async def details(self, link: str, videoid: Union[bool, str] = None):
        # This method is unchanged
        if videoid: link = self.base + link
        if "&" in link: link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title, duration_min, thumbnail, vidid = result["title"], result["duration"], result["thumbnails"][0]["url"].split("?")[0], result["id"]
            duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0
        return title, duration_min, duration_sec, thumbnail, vidid

    async def track(self, link: str, videoid: Union[bool, str] = None):
        # This method is unchanged
        if videoid: link = self.base + link
        if "&" in link: link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title, duration_min, vidid, yturl, thumbnail = result["title"], result["duration"], result["id"], result["link"], result["thumbnails"][0]["url"].split("?")[0]
        track_details = {"title": title, "link": yturl, "vidid": vidid, "duration_min": duration_min, "thumb": thumbnail}
        return track_details, vidid

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        # This method is unchanged
        if videoid: link = self.listbase + link
        if "&" in link: link = link.split("&")[0]
        cookie_file = cookie_txt_file()
        if not cookie_file: return []
        playlist = await shell_cmd(f"yt-dlp -i --get-id --flat-playlist --cookies {cookie_file} --playlist-end {limit} --skip-download {link}")
        try:
            result = [key for key in playlist.split("\n") if key]
        except: result = []
        return result

    # ------------------------------------------------------------------------- #
    # ▼▼▼ THIS IS THE ONLY METHOD WE ARE REPLACING ▼▼▼
    # ------------------------------------------------------------------------- #

    async def download(
        self,
        link: str,  # In this bot, 'link' is always the video ID (vidid)
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> tuple:
        """
        This is the master download function that gets called by the rest of the bot.
        It is now powered exclusively by your API.
        """
        # The bot's logic always passes the video ID to this function.
        # We build the full URL to pass to our new helper function.
        full_youtube_url = self.base + link

        try:
            # Call our API helper to get the direct streamable link
            stream_url = await get_stream_link_from_api(
                full_youtube_url, is_video=bool(video)
            )
        except Exception as e:
            # If the API call fails, we re-raise the exception.
            # The 'stream' function will catch this and show the user a clean error message.
            raise e
            
        # The bot's streaming engine requires a tuple: (filepath, direct)
        # 'filepath' will be our direct URL.
        # 'direct' must be True to tell the bot to stream it, not look for a local file.
        return (stream_url, True)
        
