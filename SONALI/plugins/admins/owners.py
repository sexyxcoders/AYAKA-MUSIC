from pyrogram import filters
from SONALI import app
import config
from SONALI.utils.clone_manager import start_clone, stop_clone


@app.on_message(filters.command("clone") & filters.user(config.OWNER_ID))
async def clone_handler(client, message):
    """
    Starts a clone bot with the given BOT_TOKEN.
    Usage: /clone <BOT_TOKEN>
    """
    if len(message.command) < 2:
        return await message.reply_text("❌ Usage: /clone <BOT_TOKEN>")

    token = message.command[1]

    # Send a temporary "processing" message
    processing_msg = await message.reply_text("⏳ Starting clone...")

    # Start the clone
    result = await start_clone(token, config.API_ID, config.API_HASH)

    # Update the message with the result
    await processing_msg.edit_text(result)


@app.on_message(filters.command("stopclone") & filters.user(config.OWNER_ID))
async def stopclone_handler(client, message):
    """
    Stops a running clone bot using the provided BOT_TOKEN.
    Usage: /stopclone <BOT_TOKEN>
    """
    if len(message.command) < 2:
        return await message.reply_text("❌ Usage: /stopclone <BOT_TOKEN>")

    token = message.command[1]

    # Send a temporary "processing" message
    processing_msg = await message.reply_text("⏳ Stopping clone...")

    # Stop the clone
    result = await stop_clone(token)

    # Update the message with the result
    await processing_msg.edit_text(result)
