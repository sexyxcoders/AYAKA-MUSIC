import asyncio
import importlib

from pyrogram import idle

import config
from SONALI.logging import LOGGER
from SONALI.core.bot import RAUSHAN   # ✅ Use RAUSHAN (with BOT_TOKEN inside bot.py)
from SONALI.core.call import RAUSHAN as Call  # If call manager also named RAUSHAN
from SONALI.misc import sudo
from SONALI.plugins import ALL_MODULES
from SONALI.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS
from SONALI.core.userbot import Userbot


# ✅ Initialize
app = RAUSHAN()     # Bot client (BOT_TOKEN inside bot.py)
userbot = Userbot() # Userbot client


async def init():
    # Check if string sessions are provided for userbot
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error(
            "𝐒𝐭𝐫𝐢𝐧𝐠 𝐒𝐞𝐬𝐬𝐢𝐨𝐧 𝐍𝐨𝐭 𝐅𝐢𝐥𝐥𝐞𝐝, 𝐏𝐥𝐞𝐚𝐬𝐞 𝐅𝐢𝐥𝐥 𝐀 𝐏𝐲𝐫𝐨𝐠𝐫𝐚𝐦 V2 𝐒𝐞𝐬𝐬𝐢𝐨𝐧🤬"
        )

    # Load sudo users
    await sudo()

    # Load banned users
    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except:
        pass

    # Start bot + userbot
    await app.start()
    for all_module in ALL_MODULES:
        importlib.import_module("SONALI.plugins." + all_module)   # ✅ fixed missing dot
    LOGGER("SONALI.plugins").info("𝐀𝐥𝐥 𝐅𝐞𝐚𝐭𝐮𝐫𝐞𝐬 𝐋𝐨𝐚𝐝𝐞𝐝 𝐁𝐚𝐛𝐲🥳...")

    await userbot.start()

    # If call manager has decorators
    await Call.start()
    await Call.decorators()

    LOGGER("SONALI").info("╔═════ஜ۩۞۩ஜ════╗\n  ♨️𝗠𝗔𝗗𝗘 𝗕𝗬 𝗔𝗟𝗣𝗛𝗔♨️\n╚═════ஜ۩۞۩ஜ════╝")

    # Keep running
    await idle()

    # Stop all clients when exiting
    await app.stop()
    await userbot.stop()
    LOGGER("SONALI").info("╔═════ஜ۩۞۩ஜ════╗\n  ♨️𝗠𝗔𝗗𝗘 𝗕𝗬 𝗔𝗟𝗣𝗛𝗔♨️\n╚═════ஜ۩۞۩ஜ════╝")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())