import os
from config import DURATION_LIMIT_MIN
from tools.database import get_db_queue, save_db_queue, clear_db_queue

QUEUE_LIMIT = 50

async def put_queue(chat_id, file, title, duration, user, link, thumbnail, stream_type="audio"):
    """
    Song ko queue mein add karta hai.
    """
    
    # 🔒 SAFETY: Check karo file path sahi hai ya nahi
    if not isinstance(file, str):
        print(f"❌ Queue Error: File path text nahi hai! ({type(file)})")
        return {"error": "File Error"}

    # Database se queue nikalo
    queue = await get_db_queue(chat_id)
    
    # ⚠️ SAFETY: Agar queue None hai toh empty list banao
    if not queue:
        queue = []

    if len(queue) >= QUEUE_LIMIT:
        return {"error": "Queue Full"}

    song = {
        "title": title,
        "file": str(file),
        "duration": duration,
        "by": user,
        "link": link,
        "thumbnail": thumbnail,
        "streamtype": stream_type,
        "played": 0,
    }

    queue.append(song)

    # Database update karo
    await save_db_queue(chat_id, queue)
    
    print(f"✅ [QUEUE] Song Added in {chat_id}. Total Songs: {len(queue)}")
    
    return len(queue) - 1

async def get_current_song(chat_id):
    """
    CURRENT song nikalta hai (played wala)
    """
    queue = await get_db_queue(chat_id)
    if not queue:
        return None
    return queue[0]

async def pop_queue(chat_id):
    """
    Sirf current song hataata hai aur database update karta hai.
    """
    queue = await get_db_queue(chat_id)

    if not queue:
        print(f"⚠️ [QUEUE] Pop failed for {chat_id}. Queue was already empty.")
        return None

    # Current song remove karo
    removed_song = queue.pop(0)

    # Database update karo
    await save_db_queue(chat_id, queue)
    
    # 🔍 DEBUG PRINT
    print(f"✂️ [QUEUE] Popped Song in {chat_id}. Remaining Songs: {len(queue)}")
    
    return removed_song

async def get_next_song(chat_id):
    """
    NEXT song (index 1) return karta hai.
    """
    queue = await get_db_queue(chat_id)
    
    if queue and len(queue) > 1:
        return queue[1]
    
    return None

async def get_queue(chat_id):
    queue = await get_db_queue(chat_id)
    if not queue:
        return []
    return queue

async def clear_queue(chat_id):
    """
    Queue saaf kar dega.
    """
    await clear_db_queue(chat_id)
    print(f"🧹 Queue Cleared for {chat_id}")
    
