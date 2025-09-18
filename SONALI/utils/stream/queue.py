from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def aq_markup(videoid: str, user_id: int = None):
    """
    Build inline keyboard for queue management.
    
    Args:
        videoid (str): Video/track identifier.
        user_id (int, optional): The user who requested playback (to check ownership).
    
    Returns:
        InlineKeyboardMarkup: Keyboard with playback controls.
    """
    buttons = [
        [
            InlineKeyboardButton("⏸ Pause", callback_data=f"pause|{videoid}"),
            InlineKeyboardButton("▶️ Resume", callback_data=f"resume|{videoid}"),
        ],
        [
            InlineKeyboardButton("⏭ Skip", callback_data=f"skip|{videoid}"),
            InlineKeyboardButton("⏹ Stop", callback_data=f"stop|{videoid}"),
        ],
    ]

    if user_id:
        buttons.append(
            [InlineKeyboardButton("🗑 Remove from Queue", callback_data=f"rmfromq|{videoid}|{user_id}")]
        )

    return InlineKeyboardMarkup(buttons)