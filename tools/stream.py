import os
from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped, Update  # ✅ FIX: InputAudioStream hata diya
from config import API_ID, API_HASH, SESSION
from tools.queue import put_queue, pop_queue, clear_queue, get_queue
from tools.database import is_active_chat, add_active_chat, remove_active_chat

# --- CLIENT SETUP ---
# Assistant Client (Userbot)
worker = Client(
    "MusicWorker",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION,
    in_memory=True,
)

call_py = PyTgCalls(worker)

async def start_music_worker():
    print("🔵 Starting Music Assistant...")
    try:
        await worker.start()
        await call_py.start()
        print("✅ Assistant & PyTgCalls Started!")
    except Exception as e:
        print(f"❌ Assistant Error: {e}")

# --- PLAY LOGIC ---
async def play_stream(chat_id, file_path, title, duration, user):
    """
    Decide karta hai: Abhi bajana hai ya Queue mein daalna hai?
    """
    # 1. Check karo: Kya gana already baj raha hai?
    if is_active_chat(chat_id):
        # Baj raha hai -> Queue mein daalo
        position = await put_queue(chat_id, file_path, title, duration, user)
        return False, position # False = Playing nahi, Queue hua
    
    # 2. Nahi baj raha -> Direct Play karo
    else:
        try:
            # ✅ FIX: AudioPiped use kiya
            await call_py.join_group_call(
                int(chat_id),
                AudioPiped(file_path),
            )
            add_active_chat(chat_id) # Database mein Active mark karo
            await put_queue(chat_id, file_path, title, duration, user) # Queue init karo
            return True, 0 # True = Playing Now
        except Exception as e:
            print(f"❌ Play Error: {e}")
            return None, None

# --- AUTO PLAY (STREAM END HANDLER) ---
@call_py.on_stream_end()
async def stream_end_handler(client, update: Update):
    chat_id = update.chat_id
    print(f"🔄 Stream Ended in {chat_id}, Checking Next Song...")

    # 1. Queue se Next Song nikalo
    next_song = await pop_queue(chat_id)

    if next_song:
        # 2. Next Song hai -> Play karo
        file = next_song["file"]
        title = next_song["title"]
        print(f"▶️ Auto-Playing Next: {title}")
        
        try:
            # ✅ FIX: AudioPiped use kiya
            await call_py.change_stream(
                chat_id,
                AudioPiped(file),
            )
        except Exception as e:
            print(f"❌ Auto-Play Error: {e}")
            # Agar error aaya to leave kar do
            await call_py.leave_group_call(chat_id)
            remove_active_chat(chat_id)
            await clear_queue(chat_id)
    else:
        # 3. Queue Khatam -> Leave karo
        print("🛑 Queue Empty. Leaving VC.")
        try:
            await call_py.leave_group_call(chat_id)
            remove_active_chat(chat_id) # Active tag hatao
            await clear_queue(chat_id)  # Queue saaf karo
        except:
            pass

# --- STOP FUNCTION ---
async def stop_stream(chat_id):
    try:
        await call_py.leave_group_call(int(chat_id))
        remove_active_chat(chat_id)
        await clear_queue(chat_id)
        return True
    except:
        return False

