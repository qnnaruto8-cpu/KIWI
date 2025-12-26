import os
from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped, AudioVideoPiped, Update
from pytgcalls.types.input_stream.quality import HighQualityAudio

from config import API_ID, API_HASH, SESSION
from tools.queue import put_queue, pop_queue, clear_queue, get_queue
from tools.database import is_active_chat, add_active_chat, remove_active_chat

# --- CLIENT SETUP ---
worker = Client(
    "MusicWorker",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION,
    in_memory=True,
)

call_py = PyTgCalls(worker)

async def start_music_worker():
    print("🔵 Starting Music Assistant (New Style)...")
    try:
        await worker.start()
        await call_py.start()
        print("✅ Assistant & PyTgCalls Started!")
    except Exception as e:
        print(f"❌ Assistant Error: {e}")

# --- PLAY LOGIC ---
async def play_stream(chat_id, file_path, title, duration, user):
    """
    AudioPiped Version
    """
    # ✅ FIX: Added 'await' here
    if await is_active_chat(chat_id):
        position = await put_queue(chat_id, file_path, title, duration, user)
        return False, position
    else:
        try:
            # ✅ AudioPiped Use Kar Rahe Hain
            stream = AudioPiped(
                file_path,
                audio_parameters=HighQualityAudio(),
            )
            
            await call_py.join_group_call(
                int(chat_id),
                stream,
            )
            # ✅ FIX: Added 'await' here
            await add_active_chat(chat_id)
            await put_queue(chat_id, file_path, title, duration, user)
            return True, 0
        except Exception as e:
            print(f"❌ Play Error: {e}")
            return None, None

# --- AUTO PLAY (STREAM END) ---
@call_py.on_stream_end()
async def stream_end_handler(client, update: Update):
    chat_id = update.chat_id
    print(f"🔄 Stream Ended in {chat_id}")

    next_song = await pop_queue(chat_id)

    if next_song:
        file = next_song["file"]
        title = next_song["title"]
        try:
            # ✅ AudioPiped Use Kar Rahe Hain
            stream = AudioPiped(
                file,
                audio_parameters=HighQualityAudio(),
            )
            
            await call_py.change_stream(
                chat_id,
                stream,
            )
        except Exception as e:
            print(f"❌ Auto-Play Error: {e}")
            await call_py.leave_group_call(chat_id)
            # ✅ FIX: Added 'await' here
            await remove_active_chat(chat_id)
            await clear_queue(chat_id)
    else:
        try:
            await call_py.leave_group_call(chat_id)
            # ✅ FIX: Added 'await' here
            await remove_active_chat(chat_id)
            await clear_queue(chat_id)
        except:
            pass

async def stop_stream(chat_id):
    try:
        await call_py.leave_group_call(int(chat_id))
        # ✅ FIX: Added 'await' here
        await remove_active_chat(chat_id)
        await clear_queue(chat_id)
        return True
    except:
        return False
        
