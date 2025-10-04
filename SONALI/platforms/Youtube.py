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
API_KEY = os.getenv("API_KEY", "tnc_9a13260003bfaa27f9432cd47c0491bb") 
API_BASE_URL = "https://tnc-api.me/api/v1"
# --- END CONFIGURATION ---


def get_video_id_from_url(url: str):
    """Extract the YouTube video ID from any valid URL."""
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None


async def get_stream_link_from_api(full_url: str, is_video: bool):
    """Fetch a direct stream link from TNC API."""
    video_id = get_video_id_from_url(full_url)
    if not video_id:
        raise Exception("Could not extract video ID from the URL.")

    endpoint = "video" if is_video else "audio"
    api_url = f"{API_BASE_URL}/{endpoint}/{video_id}?api_key={API_KEY}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                # Raise if HTTP error
                response.raise_for_status()
                data = await response.json()

                # Debug log full API response
                print(f"[DEBUG] API Response from {endpoint}: {json.dumps(data, indent=2)}")

                if data.get("success") and data.get("data", {}).get("link"):
                    return data["data"]["link"]

                # If no link, raise with server’s message
                error_message = (
                    data.get("data", {}).get("message")
                    or data.get("message")
                    or "Unknown API Error"
                )
                raise Exception(f"TNC API Error → {error_message}")
    except Exception as e:
        print(f"[ERROR] get_stream_link_from_api failed → {str(e)}")
        raise


def cookie_txt_file():
    cookie_dir = f"{os.getcwd()}/cookies"
    if not os.path.exists(cookie_dir):
        return None
    cookies_files = [f for f in os.listdir(cookie_dir) if f.endswith(".txt")]
    if not cookies_files:
        return None
    return os.path.join(cookie_dir, random.choice(cookies_files))


async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    out, errorz = await proc.communicate()
    if errorz:
        decoded_err = errorz.decode("utf-8")
        if "unavailable videos are hidden" in decoded_err.lower():
            return out.decode("utf-8")
        else:
            print(f"[ERROR] Shell Command Failed → {decoded_err}")
            return decoded_err
    return out.decode("utf-8")


class YouTubeAPI:
    """Handles YouTube searching, details, playlists, and downloading via API."""

    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        text = ""
        offset = None
        length = None
        for message in messages:
            if offset:
                break
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text, offset, length = message.text, entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        if offset is None:
            return None
        return text[offset: offset + length]

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0
        return title, duration_min, duration_sec, thumbnail, vidid

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            vidid = result["id"]
            yturl = result["link"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        track_details = {
            "title": title,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }
        return track_details, vidid

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]
        cookie_file = cookie_txt_file()
        if not cookie_file:
            return []
        playlist = await shell_cmd(
            f"yt-dlp -i --get-id --flat-playlist --cookies {cookie_file} --playlist-end {limit} --skip-download {link}"
        )
        try:
            result = [key for key in playlist.split("\n") if key]
        except:
            result = []
        return result

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> tuple:
        """Download (stream) handler powered by TNC API."""
        full_youtube_url = self.base + link
        try:
            stream_url = await get_stream_link_from_api(
                full_youtube_url, is_video=bool(video)
            )

            if not stream_url:
                raise Exception("NoAudioSourceFound → API returned empty link")

            return (stream_url, True)

        except Exception as e:
            print(f"[ERROR] YouTubeAPI.download failed → {str(e)}")
            raise
