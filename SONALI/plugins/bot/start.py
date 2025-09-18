import asyncio 
import time
import random
from config import LOGGER_ID, BANNED_USERS
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardMarkup, Message

from SONALI import app
from SONALI.misc import _boot_
from SONALI.utils.database import get_served_chats, get_served_users, get_sudoers
from SONALI.utils import bot_sys_stats
from SONALI.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from SONALI.utils.decorators.language import LanguageStart
from SONALI.utils.formatters import get_readable_time
from SONALI.utils.inline import private_panel, start_panel
from strings import get_string


START_VIDS = [
    "BAACAgUAAxkBAAIoZGjLJkqG7KXOtwjdg-517Y5a0LdWAAI7JAACelNYVqtEqxscnpTGHgQ",
    "BAACAgUAAxkBAAIoYmjLJi0ZnXdn9Lws5maiSj1s0231AAI5JAACelNYVkaPVJ0IXdaIHgQ",
    "BAACAgUAAxkBAAIoYGjLJgtN95ogNn0713K7xtAzm0gVAAI4JAACelNYVviTFt5bQXDYHgQ"
]

# --------------------- PRIVATE START --------------------- #
@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    loading_1 = await message.reply_text(random.choice(GREET))
    await add_served_user(message.from_user.id)
    await message.react("🍓")

    for dots in ["", ".", "..", "..."]:
        await loading_1.edit_text(f"<b>ʟᴏᴀᴅɪɴɢ{dots}</b>")
        await asyncio.sleep(0.1)

    await loading_1.delete()

    if len(message.text.split()) > 1:
        ...
    else:
        out = private_panel(_)

        #await message.reply_sticker(sticker=random.choice(STICKERS))

        async def send_start_panel():
            await message.reply_video(
                video=random.choice(START_VIDS),   # file_id from your bot
                caption=_["start_2"].format(message.from_user.mention,
                    "", "", "", "", "", ""
                ),
                reply_markup=InlineKeyboardMarkup(out),
            )

        asyncio.create_task(send_start_panel())

        if await is_on_off(2):
            await app.send_message(
                chat_id=config.LOGGER_ID,
                text=(
                    f"{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.\n\n"
                    f"<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n"
                    f"<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}"
                ),
            )


# --------------------- GROUP START --------------------- #
@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    out = start_panel(_)
    uptime = int(time.time() - _boot_)

    async def send_group_panel():
        await message.reply_video(
            video=random.choice(START_VIDS),  # file_id from your bot
            caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
            reply_markup=InlineKeyboardMarkup(out),
        )

    asyncio.create_task(send_group_panel())
    return await add_served_chat(message.chat.id)


# --------------------- WELCOME HANDLER --------------------- #
@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)

            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except:
                    pass

            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)

                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(
                            app.mention,
                            f"https://t.me/{app.username}?start=sudolist",
                            config.SUPPORT_CHAT,
                        ),
                        disable_web_page_preview=True,
                    )
                    return await app.leave_chat(message.chat.id)

                out = start_panel(_)

                async def send_welcome_panel():
                    await message.reply_video(
                        video=random.choice(START_VIDS),
                        caption=_["start_3"].format(
                            message.from_user.mention,
                            app.mention,
                            message.chat.title,
                            app.mention,
                        ),
                        reply_markup=InlineKeyboardMarkup(out),
                    )

                asyncio.create_task(send_welcome_panel())
                await add_served_chat(message.chat.id)
                await message.stop_propagation()

        except Exception as ex:
            print(ex)


# --------------------- FILE_ID HELPER --------------------- #
# Send any video to your bot in private to get its file_id
@app.on_message(filters.video & filters.private)
async def get_file_id(client, message: Message):
    file_id = message.video.file_id
    print("Video file_id:", file_id)  # also logs in console
    await message.reply_text(f"✅ Your video file_id:\n<code>{file_id}</code>")
