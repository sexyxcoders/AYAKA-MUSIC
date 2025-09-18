from pyrogram import Client

# Dictionary to keep track of all running cloned bots
cloned_bots = {}


async def start_clone(bot_token: str, api_id: int, api_hash: str):
    """
    Start a new bot instance using the given bot token.
    """
    if bot_token in cloned_bots:
        return f"⚠️ A bot with this token is already running."

    try:
        # Create a new client instance
        app = Client(
            name=f"clone_{bot_token.split(':')[0]}",
            api_id=api_id,
            api_hash=api_hash,
            bot_token=bot_token,
            in_memory=True  # prevents creating session files on disk
        )

        await app.start()
        me = await app.get_me()

        # Save in our dictionary
        cloned_bots[bot_token] = app

        return f"✅ Successfully cloned @{me.username}"
    except Exception as e:
        return f"❌ Clone failed: {str(e)}"


async def stop_clone(bot_token: str):
    """
    Stop and remove a cloned bot instance.
    """
    if bot_token not in cloned_bots:
        return "⚠️ No cloned bot found with this token."

    try:
        await cloned_bots[bot_token].stop()
        del cloned_bots[bot_token]
        return "🛑 Bot stopped successfully."
    except Exception as e:
        return f"❌ Failed to stop bot: {str(e)}"