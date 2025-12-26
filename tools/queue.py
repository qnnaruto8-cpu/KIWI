import os
from config import DURATION_LIMIT_MIN
from tools.database import get_db_queue, save_db_queue, clear_db_queue

QUEUE_LIMIT = 50


async def put_queue(chat_id, file, title, duration, user, stream_type="audio"):
    """
    Song ko queue mein add karta hai aur database update karta hai.
    """

    # 🔒 SAFETY: file MUST be string path
    if not isinstance(file, str):
        raise ValueError(f"Queue Error: file must be string path, got {type(file)}")

    # ✅ FIX: await added
    queue = await get_db_queue(chat_id)

    if len(queue) >= QUEUE_LIMIT:
        return {"error": "Queue Full"}

    song = {
        "title": title,
        "file": str(file),      # ensure string
        "duration": duration,
        "by": user,
        "streamtype": stream_type,
        "played": 0,
    }

    queue.append(song)

    # ✅ FIX: await added
    await save_db_queue(chat_id, queue)

    return len(queue) - 1


async def pop_queue(chat_id):
    """
    Current song hataata hai aur next deta hai
    """

    # ✅ FIX: await added
    queue = await get_db_queue(chat_id)

    if not queue:
        return None

    # Remove current song
    queue.pop(0)

    # ✅ FIX: await added
    await save_db_queue(chat_id, queue)

    if queue:
        next_song = queue[0]

        # 🔒 DOUBLE SAFETY
        if not isinstance(next_song.get("file"), str):
            raise ValueError("Queue Corrupted: file is not string")

        return next_song

    return None


async def get_queue(chat_id):
    # ✅ FIX: await added
    return await get_db_queue(chat_id)


async def clear_queue(chat_id):
    # ✅ FIX: await added
    await clear_db_queue(chat_id)
