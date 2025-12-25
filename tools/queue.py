import os
from config import DURATION_LIMIT_MIN
from tools.database import get_db_queue, save_db_queue, clear_db_queue

# --- CONFIG ---
# Maximum queue limit taaki spam na ho
QUEUE_LIMIT = 50 

async def put_queue(chat_id, file, title, duration, user, stream_type="audio"):
    """
    Song ko queue mein add karta hai aur database update karta hai.
    """
    # 1. Database se purani queue nikalo
    queue = get_db_queue(chat_id)
    
    # Check Limit
    if len(queue) >= QUEUE_LIMIT:
        return {"error": "Queue Full"}
    
    # 2. Song Structure banao
    song = {
        "title": title,
        "file": file,
        "duration": duration,
        "by": user,
        "streamtype": stream_type,
        "played": 0
    }
    
    # 3. List mein add karo
    queue.append(song)
    
    # 4. Database mein wapas save karo (Taaki restart hone par bhi rahe)
    save_db_queue(chat_id, queue)
    
    # Return karo ki abhi ye gaana kaunse number par hai
    return len(queue) - 1

async def pop_queue(chat_id):
    """
    Abhi jo gaana chal raha tha usse hatata hai aur NEXT gaana deta hai.
    """
    queue = get_db_queue(chat_id)
    
    if not queue:
        return None
        
    # Step 1: Current Song (0 index) ko remove karo
    queue.pop(0)
    
    # Step 2: Database Update karo
    save_db_queue(chat_id, queue)
    
    # Step 3: Agar aur gaane bache hain, toh next return karo
    if queue:
        return queue[0] # Next Song
        
    return None # Queue khatam

async def get_queue(chat_id):
    """Simple function poori list dekhne ke liye"""
    return get_db_queue(chat_id)

async def clear_queue(chat_id):
    """Sab kuch delete kar deta hai"""
    clear_db_queue(chat_id)
  
