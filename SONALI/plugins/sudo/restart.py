import asyncio
import os
import shutil
import socket
import sys
from datetime import datetime
from pyrogram.types import CallbackQuery
import urllib3
from pyrogram import filters
import aiohttp
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from io import BytesIO
import config
from SONALI import app
from SONALI.misc import HAPP, SUDOERS, XCB
from SONALI.utils.database import (
    get_active_chats,
    remove_active_chat,
    remove_active_video_chat,
)
from SONALI.utils.decorators.language import language
from SONALI.utils.pastebin import RAUSHANBin

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


async def is_heroku():
    return "heroku" in socket.getfqdn()


async def make_carbon(code):
    url = "https://carbonara.solopov.dev/api/cook"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"code": code}) as resp:
            image = BytesIO(await resp.read())
    image.name = "carbon.png"
    return image


def cleanup_storage():
    for folder in ["downloads", "raw_files", "cache"]:
        try:
            shutil.rmtree(folder)
        except:
            pass


@app.on_message(filters.command(["get_log", "logs", "getlogs"]) & SUDOERS)
@language
async def log_(client, message, _):
    try:
        await message.reply_document(document="log.txt")
    except:
        await message.reply_text(_["server_1"])


@app.on_message(filters.command(["update", "gitpull", "up"]) & SUDOERS)
@language
async def update_(client, message, _):
    if await is_heroku() and HAPP is None:
        return await message.reply_text(_["server_2"])

    response = await message.reply_text(_["server_3"])

    # ✅ Fetch latest commits safely
    os.system(f"git fetch origin {config.UPSTREAM_BRANCH} &> /dev/null")
    await asyncio.sleep(3)

    # Check for new commits
    fetch_result = os.popen(f"git log HEAD..origin/{config.UPSTREAM_BRANCH} --oneline").read()
    if not fetch_result.strip():
        return await response.edit(_["server_6"])  # No updates available

    updates = ""
    ordinal = lambda format: "%d%s" % (
        format,
        "tsnrhtdd"[(format // 10 % 10 != 1) * (format % 10 < 4) * format % 10 :: 4],
    )

    for line in fetch_result.strip().split("\n"):
        commit_hash, commit_msg = line.split(" ", 1)
        updates += f"<b>➣ #{commit_hash}: {commit_msg}</b>\n"

    _update_response_ = "<b>ᴀ ɴᴇᴡ ᴜᴩᴅᴀᴛᴇ ɪs ᴀᴠᴀɪʟᴀʙʟᴇ ғᴏʀ ᴛʜᴇ ʙᴏᴛ !</b>\n\n➣ ᴩᴜsʜɪɴɢ ᴜᴩᴅᴀᴛᴇs ɴᴏᴡ\n\n<b><u>ᴜᴩᴅᴀᴛᴇs:</u></b>\n\n"
    _final_updates_ = _update_response_ + updates

    if len(_final_updates_) > 4096:
        url = await RAUSHANBin(updates)
        nrs = await response.edit(
            f"<b>ᴀ ɴᴇᴡ ᴜᴩᴅᴀᴛᴇ ɪs ᴀᴠᴀɪʟᴀʙʟᴇ ғᴏʀ ᴛʜᴇ ʙᴏᴛ !</b>\n\n"
            f"➣ ᴩᴜsʜɪɴɢ ᴜᴩᴅᴀᴛᴇs ɴᴏᴡ\n\n"
            f"<u><b>ᴜᴩᴅᴀᴛᴇs :</b></u>\n\n<a href={url}>ᴄʜᴇᴄᴋ ᴜᴩᴅᴀᴛᴇs</a>"
        )
    else:
        nrs = await response.edit(_final_updates_, disable_web_page_preview=True)

    # Pull updates safely
    os.system(f"git stash &> /dev/null && git pull origin {config.UPSTREAM_BRANCH}")

    # Notify active chats
    try:
        served_chats = await get_active_chats()
        for x in served_chats:
            try:
                await app.send_message(chat_id=int(x), text=_["server_8"].format(app.mention))
                await remove_active_chat(x)
                await remove_active_video_chat(x)
            except:
                pass
        await response.edit(f"{nrs.text}\n\n{_['server_7']}")
    except:
        pass

    cleanup_storage()

    # Restart bot via execv (like your working example)
    if await is_heroku():
        try:
            os.system(
                f"{XCB[5]} {XCB[7]} {XCB[9]}{XCB[4]}{XCB[0]*2}{XCB[6]}{XCB[4]}{XCB[8]}"
                f"{XCB[1]}{XCB[5]}{XCB[2]}{XCB[6]}{XCB[2]}{XCB[3]}{XCB[0]}"
                f"{XCB[10]}{XCB[2]}{XCB[5]} {XCB[11]}{XCB[4]}{XCB[12]}"
            )
            return
        except Exception as err:
            await response.edit(f"{nrs.text}\n\n{_['server_9']}")
            return await app.send_message(chat_id=config.LOGGER_ID, text=_["server_10"].format(err))
    else:
        os.execv(sys.executable, [sys.executable, "-m", "SONALI"])


@app.on_message(filters.command(["restart"]) & SUDOERS)
async def restart_(_, message):
    response = await message.reply_text("ʀᴇsᴛᴀʀᴛɪɴɢ...")
    ac_chats = await get_active_chats()
    for x in ac_chats:
        try:
            await app.send_message(
                chat_id=int(x),
                text=f"{app.mention} ɪs ʀᴇsᴛᴀʀᴛɪɴɢ...\n\nʏᴏᴜ ᴄᴀɴ sᴛᴀʀᴛ ᴩʟᴀʏɪɴɢ ᴀɢᴀɪɴ ᴀғᴛᴇʀ 15-20 sᴇᴄᴏɴᴅs.",
            )
            await remove_active_chat(x)
            await remove_active_video_chat(x)
        except:
            pass

    cleanup_storage()

    await response.edit_text(
        "» ʀᴇsᴛᴀʀᴛ ᴘʀᴏᴄᴇss sᴛᴀʀᴛᴇᴅ, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ғᴏʀ ғᴇᴡ sᴇᴄᴏɴᴅs ᴜɴᴛɪʟ ᴛʜᴇ ʙᴏᴛ sᴛᴀʀᴛs..."
    )
    os.execv(sys.executable, [sys.executable, "-m", "SONALI"])
