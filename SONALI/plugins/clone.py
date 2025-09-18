from pyrogram import filters
from SONALI import app, API_ID, API_HASH
from SONALI.clone_manager import start_clone, stop_clone


@app.on_message(filters.command("clone"))
async def clone_handler(client, message):
    if len(message.command) < 2:
        return await message.reply("⚡ Usage: `/clone <BOT_TOKEN>`", quote=True)

    token = message.command[1]
    result = await start_clone(token, API_ID, API_HASH)
    await message.reply(result, quote=True)


@app.on_message(filters.command("stopclone"))
async def stopclone_handler(client, message):
    if len(message.command) < 2:
        return await message.reply("⚡ Usage: `/stopclone <BOT_TOKEN>`", quote=True)

    token = message.command[1]
    result = await stop_clone(token)
    await message.reply(result, quote=True)