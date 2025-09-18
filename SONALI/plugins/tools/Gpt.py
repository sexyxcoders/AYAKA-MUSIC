import asyncio
import os
import requests

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction

from lexica import AsyncClient, languageModels, Messages
from SONALI import app


# ----------------------------
# ElevenLabs Config
# ----------------------------
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "E7bpJOpaUwdzBn3Wd6Lr")


def extract_content(response) -> str:
    if isinstance(response, dict):
        return response.get("content", "No content available.")
    return str(response)


async def get_gpt_response(prompt: str) -> str:
    lexica_client = AsyncClient()
    try:
        messages = [Messages(content=prompt, role="user")]
        response = await lexica_client.ChatCompletion(messages, languageModels.gpt)
        return extract_content(response)
    finally:
        await lexica_client.close()


async def safe_gpt_response(prompt: str, timeout: int = 30) -> str:
    try:
        return await asyncio.wait_for(get_gpt_response(prompt), timeout=timeout)
    except asyncio.TimeoutError:
        raise Exception(" GPT ʀᴇǫᴜᴇsᴛ ᴛɪᴍᴇᴅ ᴏᴜᴛ. Pʟᴇᴀsᴇ ᴛʀʏ ᴀ sʜᴏʀᴛᴇʀ ᴘʀᴏᴍᴘᴛ.")
    except Exception as e:
        raise Exception(f"❌ GPT Error: {e}")


async def send_typing_action(client: Client, chat_id: int, interval: int = 3):
    try:
        while True:
            await client.send_chat_action(chat_id, ChatAction.TYPING)
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        pass


# ----------------------------
# Process GPT + TTS
# ----------------------------
async def process_query(client: Client, message: Message, tts: bool = False):
    if len(message.command) < 2:
        return await message.reply_text(
            f"Hello {message.from_user.first_name}, how can I assist you today?"
        )

    query = message.text.split(" ", 1)[1].strip()

    if len(query) > 4000:
        return await message.reply_text("❌ Yᴏᴜʀ ᴘʀᴏᴍᴘᴛ ɪs ᴛᴏᴏ ʟᴏɴɢ (ᴍᴀx 𝟺𝟶𝟶𝟶 ᴄʜᴀʀᴀᴄᴛᴇʀs). Pʟᴇᴀsᴇ sʜᴏʀᴛᴇɴ ɪᴛ.")

    audio_file = "ayaka.mp3"
    typing_task = asyncio.create_task(send_typing_action(client, message.chat.id))

    try:
        content = await safe_gpt_response(query, timeout=30)

        if not content:
            return await message.reply_text("⚠️ Nᴏ ʀᴇsᴘᴏɴsᴇ ғʀᴏᴍ GPT.")

        if tts:
            if len(content) > 1000:
                content = content[:1000] + "..."

            # --- ElevenLabs TTS with voice settings ---
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
            headers = {
                "xi-api-key": ELEVENLABS_API_KEY,
                "accept": "audio/mpeg",
                "Content-Type": "application/json"
            }
            payload = {
                "text": content,
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.8,
                    "style": 0.3,       # adds natural flow
                    "speaking_rate": 0.9  # slower speech
                }
            }

            resp = requests.post(url, headers=headers, json=payload)
            if resp.status_code != 200:
                return await message.reply_text(f"⚠️ TTS failed ({resp.status_code}): {resp.text}")

            with open(audio_file, "wb") as f:
                f.write(resp.content)

            await client.send_voice(chat_id=message.chat.id, voice=audio_file)

        else:
            if len(content) > 4096:
                for i in range(0, len(content), 4096):
                    await message.reply_text(content[i:i+4096])
            else:
                await message.reply_text(content)

    except Exception as e:
        await message.reply_text(str(e))

    finally:
        typing_task.cancel()
        if os.path.exists(audio_file):
            os.remove(audio_file)


# ----------------------------
# Commands
# ----------------------------
@app.on_message(filters.command(["arvis"], prefixes=["j", "J"]))
async def jarvis_handler(client: Client, message: Message):
    try:
        await asyncio.wait_for(process_query(client, message), timeout=60)
    except asyncio.TimeoutError:
        await message.reply_text("⏳ Tɪᴍᴇᴏᴜᴛ. Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ᴡɪᴛʜ ᴀ sʜᴏʀᴛᴇʀ ᴘʀᴏᴍᴘᴛ.")


@app.on_message(filters.command(["chatgpt", "ai", "ask", "Master"], prefixes=["+", ".", "/", "-", "?", "$", "#", "&"]))
async def chatgpt_handler(client: Client, message: Message):
    try:
        await asyncio.wait_for(process_query(client, message), timeout=60)
    except asyncio.TimeoutError:
        await message.reply_text("⏳ Tɪᴍᴇᴏᴜᴛ. Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ᴡɪᴛʜ ᴀ sʜᴏʀᴛᴇʀ ᴘʀᴏᴍᴘᴛ")


@app.on_message(filters.command(["ssis"], prefixes=["a", "A"]))
async def annie_tts_handler(client: Client, message: Message):
    try:
        await asyncio.wait_for(process_query(client, message, tts=True), timeout=60)
    except asyncio.TimeoutError:
        await message.reply_text("⏳ Tɪᴍᴇᴏᴜᴛ. Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ᴡɪᴛʜ ᴀ sʜᴏʀᴛᴇʀ ᴘʀᴏᴍᴘᴛ")
