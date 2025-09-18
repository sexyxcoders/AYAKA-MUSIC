import asyncio
import os
import requests
from openai import AsyncOpenAI

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction

from SONALI import app

# ----------------------------
# OpenAI Config
# ----------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY","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")
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# ----------------------------
# ElevenLabs Config
# ----------------------------
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "E7bpJOpaUwdzBn3Wd6Lr")


# ----------------------------
# Typing action
# ----------------------------
async def send_typing_action(client: Client, chat_id: int, interval: int = 1):
    try:
        while True:
            await client.send_chat_action(chat_id, ChatAction.TYPING)
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        pass


# ----------------------------
# GPT Functions
# ----------------------------
async def get_gpt_response(prompt: str) -> str:
    try:
        resp = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"❌ OpenAI Error: {e}"


async def safe_gpt_response(prompt: str, timeout: int = 30) -> str:
    try:
        return await asyncio.wait_for(get_gpt_response(prompt), timeout=timeout)
    except asyncio.TimeoutError:
        raise Exception("⏳ GPT request timed out. Try a shorter prompt.")
    except Exception as e:
        raise Exception(f"❌ GPT Error: {e}")


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
        return await message.reply_text(
            "❌ Your prompt is too long (max 4000 characters)."
        )

    audio_file = "ayaka.mp3"
    typing_task = asyncio.create_task(send_typing_action(client, message.chat.id, interval=1))

    try:
        if tts:
            # Full GPT response for TTS
            content = await safe_gpt_response(query, timeout=30)
            if not content:
                return await message.reply_text("⚠️ No response from GPT.")

            if len(content) > 1000:
                content = content[:1000] + "..."

            # ElevenLabs TTS
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
                    "style": 0.3,
                    "speaking_rate": 0.9
                }
            }

            resp = requests.post(url, headers=headers, json=payload)
            if resp.status_code != 200:
                return await message.reply_text(f"⚠️ TTS failed ({resp.status_code}): {resp.text}")

            with open(audio_file, "wb") as f:
                f.write(resp.content)

            await client.send_voice(chat_id=message.chat.id, voice=audio_file)

        else:
            # Streaming GPT response
            msg = await message.reply_text("🤖 ...")
            collected = ""

            async with openai_client.chat.completions.stream(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": query}],
            ) as stream:
                async for event in stream:
                    if event.type == "token":
                        collected += event.token
                        if len(collected) % 20 == 0:  # update every ~20 chars
                            try:
                                await msg.edit_text(collected)
                            except Exception:
                                pass

                # Final response
                final = await stream.get_final_response()
                collected = final.choices[0].message.content
                try:
                    await msg.edit_text(collected)
                except Exception:
                    pass

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
        await message.reply_text("⏳ Timeout. Try a shorter prompt.")


@app.on_message(filters.command(["chatgpt", "ai", "ask", "Master"], prefixes=["+", ".", "/", "-", "?", "$", "#", "&"]))
async def chatgpt_handler(client: Client, message: Message):
    try:
        await asyncio.wait_for(process_query(client, message), timeout=60)
    except asyncio.TimeoutError:
        await message.reply_text("⏳ Timeout. Try a shorter prompt.")


@app.on_message(filters.command(["ssis"], prefixes=["a", "A"]))
async def annie_tts_handler(client: Client, message: Message):
    try:
        await asyncio.wait_for(process_query(client, message, tts=True), timeout=60)
    except asyncio.TimeoutError:
        await message.reply_text("⏳ Timeout. Try a shorter prompt.")
