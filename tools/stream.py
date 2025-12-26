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

# --- CURRENT STREAM DATA TRACKER ---
current_streams = {}  # {chat_id: {"paused": bool, "current_file": str}}

# --- PLAY LOGIC ---
async def play_stream(chat_id, file_path, title, duration, user):
    """
    AudioPiped Version
    """
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
            
            # ✅ Current stream track karo
            current_streams[chat_id] = {
                "paused": False,
                "current_file": file_path,
                "title": title,
                "duration": duration,
                "user": user
            }
            
            await add_active_chat(chat_id)
            await put_queue(chat_id, file_path, title, duration, user)
            return True, 0
        except Exception as e:
            print(f"❌ Play Error: {e}")
            return None, None

# --- PAUSE STREAM ---
async def pause_stream(chat_id: int):
    """Stream को pause करें"""
    try:
        await call_py.pause_stream(int(chat_id))
        
        # ✅ Status update karo
        if chat_id in current_streams:
            current_streams[chat_id]["paused"] = True
            
        print(f"⏸ Stream paused in {chat_id}")
        return True
    except Exception as e:
        print(f"❌ Pause Error: {e}")
        return False

# --- RESUME STREAM ---
async def resume_stream(chat_id: int):
    """Stream resume करें"""
    try:
        await call_py.resume_stream(int(chat_id))
        
        # ✅ Status update karo
        if chat_id in current_streams:
            current_streams[chat_id]["paused"] = False
            
        print(f"▶️ Stream resumed in {chat_id}")
        return True
    except Exception as e:
        print(f"❌ Resume Error: {e}")
        return False

# --- SKIP STREAM ---
async def skip_stream(chat_id: int):
    """Current stream skip करें aur next play karo"""
    try:
        # ✅ Current stream stop karo
        await call_py.leave_group_call(int(chat_id))
        
        # ✅ Next song queue se nikalo
        next_song = await pop_queue(chat_id)
        
        if next_song:
            file = next_song["file"]
            title = next_song["title"]
            duration = next_song["duration"]
            user = next_song["user"]
            
            # ✅ Naya stream start karo
            stream = AudioPiped(
                file,
                audio_parameters=HighQualityAudio(),
            )
            
            await call_py.join_group_call(
                int(chat_id),
                stream,
            )
            
            # ✅ Update current stream
            current_streams[chat_id] = {
                "paused": False,
                "current_file": file,
                "title": title,
                "duration": duration,
                "user": user
            }
            
            print(f"⏭ Skipped to next song in {chat_id}")
            return True, {
                "title": title,
                "duration": duration,
                "user": user,
                "file": file
            }
        else:
            # ✅ Queue empty hai toh clean karo
            await remove_active_chat(chat_id)
            await clear_queue(chat_id)
            if chat_id in current_streams:
                del current_streams[chat_id]
                
            print(f"⏭ Queue empty in {chat_id}, stopped")
            return False, None
            
    except Exception as e:
        print(f"❌ Skip Error: {e}")
        return False, None

# --- STOP STREAM ---
async def stop_stream(chat_id):
    """Stream complete stop"""
    try:
        await call_py.leave_group_call(int(chat_id))
        
        # ✅ Clean up
        await remove_active_chat(chat_id)
        await clear_queue(chat_id)
        
        if chat_id in current_streams:
            del current_streams[chat_id]
            
        print(f"⏹ Stream stopped in {chat_id}")
        return True
    except Exception as e:
        print(f"❌ Stop Error: {e}")
        return False

# --- GET CURRENT PLAYING INFO ---
async def get_current_stream(chat_id):
    """Current playing ka info de"""
    if chat_id in current_streams:
        return current_streams[chat_id]
    return None

# --- GET QUEUE INFO ---
async def get_queue_info(chat_id):
    """Queue ki list de"""
    queue = await get_queue(chat_id)
    return queue

# --- CHECK IF PLAYING ---
async def is_stream_playing(chat_id):
    """Check karo stream chal raha hai ya nahi"""
    if chat_id in current_streams:
        return not current_streams[chat_id]["paused"]
    return False

# --- AUTO PLAY (STREAM END) ---
@call_py.on_stream_end()
async def stream_end_handler(client, update: Update):
    chat_id = update.chat_id
    print(f"🔄 Stream Ended in {chat_id}")

    # ✅ Current stream data clear karo
    if chat_id in current_streams:
        del current_streams[chat_id]

    next_song = await pop_queue(chat_id)

    if next_song:
        file = next_song["file"]
        title = next_song["title"]
        duration = next_song["duration"]
        user = next_song["user"]
        
        try:
            # ✅ Naya stream start karo
            stream = AudioPiped(
                file,
                audio_parameters=HighQualityAudio(),
            )
            
            # ✅ Update current stream
            current_streams[chat_id] = {
                "paused": False,
                "current_file": file,
                "title": title,
                "duration": duration,
                "user": user
            }
            
            await call_py.join_group_call(
                chat_id,
                stream,
            )
            
        except Exception as e:
            print(f"❌ Auto-Play Error: {e}")
            await call_py.leave_group_call(chat_id)
            await remove_active_chat(chat_id)
            await clear_queue(chat_id)
            if chat_id in current_streams:
                del current_streams[chat_id]
    else:
        try:
            await call_py.leave_group_call(chat_id)
            await remove_active_chat(chat_id)
            await clear_queue(chat_id)
        except:
            pass
