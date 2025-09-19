from pyrogram import Client, errors
from pyrogram.enums import ChatMemberStatus, ParseMode
import config
from SONALI.logging import LOGGER


# 🔑 Only BOT_TOKEN is hardcoded her
BOT_TOKEN = "8477795771:AAGFz4p7pmJaw5wp7L1U_KkeqdIJGJ56rZk"


class RAUSHAN(Client):
    def __init__(self):
        LOGGER(__name__).info("Initializing Bot...")
        super().__init__(
            name="RAUSHAN",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=BOT_TOKEN,   # ✅ uses the hardcoded token here
            in_memory=True,
            parse_mode=ParseMode.HTML,
            max_concurrent_transmissions=7,
        )

    async def start(self):
        await super().start()
        self.id = self.me.id
        self.name = self.me.first_name + " " + (self.me.last_name or "")
        self.username = self.me.username
        self.mention = self.me.mention

        try:
            await self.send_message(
                chat_id=config.LOGGER_ID,
                text=(
                    f"<u><b>» {self.mention} ʙᴏᴛ sᴛᴀʀᴛᴇᴅ :</b></u>\n\n"
                    f"ɪᴅ : <code>{self.id}</code>\n"
                    f"ɴᴀᴍᴇ : {self.name}\n"
                    f"ᴜsᴇʀɴᴀᴍᴇ : @{self.username}"
                ),
            )
        except (errors.ChannelInvalid, errors.PeerIdInvalid):
            LOGGER(__name__).error(
                "Bot failed to access the log group/channel. "
                "Make sure you've added your bot to your log group/channel."
            )
            exit()
        except Exception as ex:
            LOGGER(__name__).error(
                f"Bot failed to access the log group/channel.\nReason: {type(ex).__name__}."
            )
            exit()

        a = await self.get_chat_member(config.LOGGER_ID, self.id)
        if a.status != ChatMemberStatus.ADMINISTRATOR:
            LOGGER(__name__).error(
                "Please promote your bot as an admin in your log group/channel."
            )
            exit()

        LOGGER(__name__).info(f"Music Bot Started as {self.name}")

    async def stop(self):
        await super().stop()
        LOGGER(__name__).info("Bot stopped.")