from pyrogram import Client

# Dictionary to keep track of running cloned bots
cloned_bots = {}


async def start_clone(bot_token: str, api_id: int, api_hash: str):
    """
    Start a new bot instance using the given bot token.
    """
    if bot_token in cloned_bots:
        return f"⚠️ A bot with this token is already running."

    try:
        client = Client(
            name=f"clone_{bot_token.split(':')[0]}",
            api_id=api_id,
            api_hash=api_hash,
            bot_token=bot_token,
            plugins=dict(root="SONALI")  # your main plugins folder
        )

        await client.start()
        cloned_bots[bot_token] = client
        return f"✅ Clone started successfully for token: {bot_token[:10]}..."
    except Exception as e:
        return f"❌ Failed to start clone: {str(e)}"


async def stop_clone(bot_token: str):
    """
    Stop a running cloned bot.
    """
    if bot_token not in cloned_bots:
        return f"⚠️ No clone found with this token."

    try:
        client = cloned_bots.pop(bot_token)
        await client.stop()
        return f"🛑 Clone stopped for token: {bot_token[:10]}..."
    except Exception as e:
        return f"❌ Failed to stop clone: {str(e)}"