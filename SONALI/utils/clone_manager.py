# SONALI/utils/clone_manager.py

import asyncio
from pyrogram import Client

# Dictionary to store running clone clients
running_clones = {}

async def start_clone(token: str, api_id: int, api_hash: str) -> str:
    """
    Starts a new Pyrogram client instance with the given BOT_TOKEN.
    Returns a status message.
    """
    if token in running_clones:
        return f"A clone with this token is already running."

    try:
        # Create a new Pyrogram client
        clone_client = Client(
            name=f"clone_{token[-5:]}",
            api_id=api_id,
            api_hash=api_hash,
            bot_token=token
        )

        # Start the client asynchronously
        await clone_client.start()

        # Store it in the running clones dictionary
        running_clones[token] = clone_client
        return f"✅ Clone started successfully for token ending with `{token[-5:]}`."

    except Exception as e:
        return f"❌ Failed to start clone: {e}"


async def stop_clone(token: str) -> str:
    """
    Stops a running Pyrogram client instance.
    Returns a status message.
    """
    clone_client = running_clones.get(token)
    if not clone_client:
        return f"No running clone found for this token."

    try:
        # Stop the client asynchronously
        await clone_client.stop()
        # Remove from the dictionary
        running_clones.pop(token)
        return f"✅ Clone stopped successfully for token ending with `{token[-5:]}`."
    except Exception as e:
        return f"❌ Failed to stop clone: {e}"
