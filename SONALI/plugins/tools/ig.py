import re
import httpx
from pyrogram import Client, filters
from pyrogram.types import Message
from SONALI import app

API_URL = "https://www.alphaapis.org/Instagram/dl/v1"


async def fetch_instagram_media(instagram_url: str):
    """Fetch media info from API"""
    async with httpx.AsyncClient(timeout=15.0) as http:
        response = await http.get(API_URL, params={"url": instagram_url})
        response.raise_for_status()
        return response.json()


async def send_instagram_media(message: Message, url: str):
    """Download and send Instagram media"""
    processing_message = await message.reply_text("Pʀᴏᴄᴇssɪɴɢ...")

    try:
        data = await fetch_instagram_media(url)
        results = data.get("result", [])

        if not results:
            return await processing_message.edit("⚠️ Nᴏ ᴍᴇᴅɪᴀ ғᴏᴜɴᴅ. Pʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ᴛʜᴇ ʟɪɴᴋ.")

        for item in results:
            download_link = item.get("downloadLink")

            if not download_link:
                continue

            if ".mp4" in download_link:
                await message.reply_video(download_link)
            elif any(ext in download_link for ext in (".jpg", ".jpeg", ".png", ".webp")):
                await message.reply_photo(download_link)
            else:
                await message.reply_text(f"❌ Uɴsᴜᴘᴘᴏʀᴛᴇᴅ ᴍᴇᴅɪᴀ ᴛʏᴘᴇ: {download_link}")

    except Exception as e:
        await processing_message.edit(f"❌ Eʀʀᴏʀ: {e}")
    finally:
        await processing_message.delete()


# Command handler (/ig or /insta)
@app.on_message(filters.command(["ig", "insta"]))
async def insta_download_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("❌ Usᴀɢᴇ /insta [Instagram URL]")

    instagram_url = message.command[1]
    await send_instagram_media(message, instagram_url)


# Auto-detect Instagram URLs in any message
@app.on_message(filters.regex(r"(https?://(?:www\.)?(?:instagram\.com|instagr\.am)/\S+)"))
async def insta_download_auto(client: Client, message: Message):
    match = re.search(r"(https?://(?:www\.)?(?:instagram\.com|instagr\.am)/\S+)", message.text)
    if match:
        instagram_url = match.group(1)
        await send_instagram_media(message, instagram_url)
