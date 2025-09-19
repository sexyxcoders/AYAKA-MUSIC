from pyrogram import Client, errors
from pyrogram.enums import ChatMemberStatus

import config
from ..logging import LOGGER


class RAUSHAN(Client):
    def __init__(self):
        LOGGER("RAUSHAN").info("Starting Bot...")
        super().__init__(
            "SONALI",  # session name
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            in_memory=True,
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
                text=f"<u><b>» {self.mention} ʙᴏᴛ sᴛᴀʀᴛᴇᴅ :</b></u>\n\n"
                     f"ɪᴅ : <code>{self.id}</code>\n"
                     f"ɴᴀᴍᴇ : {self.name}\n"
                     f"ᴜsᴇʀɴᴀᴍᴇ : @{self.username}",
            )
        except (errors.ChannelInvalid, errors.PeerIdInvalid):
            LOGGER("RAUSHAN").error(
                "Bot failed to access the log group/channel. "
                "Make sure you have added your bot to the log group/channel."
            )
        except Exception as ex:
            LOGGER("RAUSHAN").error(
                f"Bot failed to access the log group/channel.\nReason: {type(ex).__name__}."
            )

        a = await self.get_chat_member(config.LOGGER_ID, self.id)
        if a.status != ChatMemberStatus.ADMINISTRATOR:
            LOGGER("RAUSHAN").error(
                "Please promote your bot as an admin in your log group/channel."
            )

        LOGGER("RAUSHAN").info(f"Music Bot Started as {self.name}")

    async def stop(self):
        await super().stop()