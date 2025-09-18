from pyrogram import filters
from SONALI import app, config
from SONALI.utils.clone_manager import start_clone, stop_clone


@app.on_message(filters.command("clone") & filters.user(config.OWNER_ID))
async def clone_handler(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /clone <BOT_TOKEN>")

    token = message.command[1]
    msg = await start_clone(token, config.API_ID, config.API_HASH)
    await message.reply_text(msg)


@app.on_message(filters.command("stopclone") & filters.user(config.OWNER_ID))
async def stopclone_handler(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /stopclone <BOT_TOKEN>")

    token = message.command[1]
    msg = await stop_clone(token)
    await message.reply_text(msg)