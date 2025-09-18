import asyncio
import os
import shutil
import socket
from datetime import datetime
from pyrogram.types import CallbackQuery
import urllib3
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError
from pyrogram import filters
import aiohttp
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from io import BytesIO
from pyrogram import filters
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

 
@app.on_message(
    filters.command(["get_log", "logs", "getlogs"]) & SUDOERS
)
@language
async def log_(client, message, _):
    try:
        await message.reply_document(document="log.txt")
    except:
        await message.reply_text(_["server_1"])


@app.on_message(filters.command(["update", "gitpull", "up"]) & SUDOERS)
@language
async def update_(client, message, _):
    if await is_heroku():
        if HAPP is None:
            return await message.reply_text(_["server_2"])

    response = await message.reply_text(_["server_3"])

    try:
        # explicitly point Repo to current directory
        repo = Repo(os.getcwd())   # ✅ fixed
    except GitCommandError:
        return await response.edit(_["server_4"])
    except InvalidGitRepositoryError:
        return await response.edit(
            "⚠️ This folder is not a valid git repository.\n\n"
            "Make sure you deployed the bot using `git clone` "
            "and not by uploading a zip."
        )

    # fetch latest commits
    try:
        repo.git.fetch("origin", config.UPSTREAM_BRANCH)
    except Exception as e:
        return await response.edit(f"❌ Git fetch failed:\n<code>{str(e)}</code>")

    # check for new commits
    commits = list(repo.iter_commits(f"HEAD..origin/{config.UPSTREAM_BRANCH}"))
    if not commits:
        return await response.edit(_["server_6"])  # no updates available

    updates = ""
    ordinal = lambda format: "%d%s" % (
        format,
        "tsnrhtdd"[(format // 10 % 10 != 1) * (format % 10 < 4) * format % 10 :: 4],
    )
    REPO_ = repo.remotes.origin.url.split(".git")[0]

    for info in commits:
        updates += (
            f"<b>➣ #{info.count()}: <a href={REPO_}/commit/{info}>{info.summary}</a> "
            f"ʙʏ -> {info.author}</b>\n"
            f"\t<b>➥ ᴄᴏᴍᴍɪᴛᴇᴅ ᴏɴ :</b> "
            f"{ordinal(int(datetime.fromtimestamp(info.committed_date).strftime('%d')))} "
            f"{datetime.fromtimestamp(info.committed_date).strftime('%b %Y')}\n\n"
        )

    _update_response_ = (
        "<b>ᴀ ɴᴇᴡ ᴜᴩᴅᴀᴛᴇ ɪs ᴀᴠᴀɪʟᴀʙʟᴇ ғᴏʀ ᴛʜᴇ ʙᴏᴛ !</b>\n\n"
        "➣ ᴩᴜsʜɪɴɢ ᴜᴩᴅᴀᴛᴇs ɴᴏᴡ\n\n"
        "<b><u>ᴜᴩᴅᴀᴛᴇs:</u></b>\n\n"
    )
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

    # pull updates safely
    try:
        repo.git.stash("save")
        repo.git.pull("origin", config.UPSTREAM_BRANCH)
    except Exception as e:
        return await response.edit(f"❌ Git pull failed:\n<code>{str(e)}</code>")

    # notify active chats and restart
    try:
        served_chats = await get_active_chats()
        for x in served_chats:
            try:
                await app.send_message(
                    chat_id=int(x),
                    text=_["server_8"].format(app.mention),
                )
                await remove_active_chat(x)
                await remove_active_video_chat(x)
            except:
                pass
        await response.edit(f"{nrs.text}\n\n{_['server_7']}")
    except:
        pass

    if await is_heroku():
        try:
            os.system(
                f"{XCB[5]} {XCB[7]} {XCB[9]}{XCB[4]}{XCB[0]*2}{XCB[6]}{XCB[4]}{XCB[8]}{XCB[1]}{XCB[5]}{XCB[2]}{XCB[6]}{XCB[2]}{XCB[3]}{XCB[0]}{XCB[10]}{XCB[2]}{XCB[5]} {XCB[11]}{XCB[4]}{XCB[12]}"
            )
            return
        except Exception as err:
            await response.edit(f"{nrs.text}\n\n{_['server_9']}")
            return await app.send_message(
                chat_id=config.LOGGER_ID,
                text=_["server_10"].format(err),
            )
    else:
        os.system("pip3 install -r requirements.txt")
        os.system(f"kill -9 {os.getpid()} && bash start")
        exit()


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

    try:
        shutil.rmtree("downloads")
        shutil.rmtree("raw_files")
        shutil.rmtree("cache")
    except:
        pass
    await response.edit_text(
        "» ʀᴇsᴛᴀʀᴛ ᴘʀᴏᴄᴇss sᴛᴀʀᴛᴇᴅ, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ғᴏʀ ғᴇᴡ sᴇᴄᴏɴᴅs ᴜɴᴛɪʟ ᴛʜᴇ ʙᴏᴛ sᴛᴀʀᴛs..."
    )
    os.system(f"kill -9 {os.getpid()} && bash start")
