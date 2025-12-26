import asyncio
from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped, Update
from pytgcalls.types.input_stream.quality import HighQualityAudio
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode

# Configs
from config import API_ID, API_HASH, SESSION, BOT_TOKEN, OWNER_NAME
from tools.queue import put_queue, pop_queue, clear_queue
from tools.database import is_active_chat, add_active_chat, remove_active_chat

# --- GLOBAL DICTIONARIES (Message Track Karne Ke Liye) ---
LAST_MSG_ID = {}   # Currently Playing Message ID
QUEUE_MSG_ID = {}  # "Added to Queue" Message IDs

# --- CLIENT SETUP ---
# 1. Userbot (Music Player)
worker = Client(
    "MusicWorker",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION,
    in_memory=True,
)

call_py = PyTgCalls(worker)

# 2. Main Bot (Message Manager) - Iska use hum auto-play message bhejne ke liye karenge
main_bot = Bot(token=BOT_TOKEN)

async def start_music_worker():
    print("🔵 Starting Music Assistant (VIP Style)...")
    try:
        await worker.start()
        await call_py.start()
        print("✅ Assistant & PyTgCalls Started!")
    except Exception as e:
        print(f"❌ Assistant Error: {e}")

# --- 1. PLAY LOGIC (First Time Play) ---
async def play_stream(chat_id, file_path, title, duration, user, link, thumbnail):
    """
    Queue system ke sath AudioPiped Play
    """
    # Agar chat already active hai, toh Queue mein daalo
    if await is_active_chat(chat_id):
        # Note: put_queue ab Link aur Thumbnail bhi leta hai
        position = await put_queue(chat_id, file_path, title, duration, user, link, thumbnail)
        return False, position
    else:
        try:
            stream = AudioPiped(
                file_path,
                audio_parameters=HighQualityAudio(),
            )
            
            await call_py.join_group_call(
                int(chat_id),
                stream,
            )
            
            await add_active_chat(chat_id)
            await put_queue(chat_id, file_path, title, duration, user, link, thumbnail)
            return True, 0
        except Exception as e:
            print(f"❌ Play Error: {e}")
            return None, str(e)

# --- 2. AUTO PLAY HANDLER (Jab gaana khatam ho) ---
@call_py.on_stream_end()
async def stream_end_handler(client, update: Update):
    chat_id = update.chat_id
    print(f"🔄 Stream Ended in {chat_id}")

    # A. Purana "Playing" Message Delete karo
    if chat_id in LAST_MSG_ID:
        try:
            await main_bot.delete_message(chat_id, LAST_MSG_ID[chat_id])
        except:
            pass # Message shayad pehle hi delete ho gaya ho
    
    # B. Queue se next song nikalo
    next_song = await pop_queue(chat_id)

    if next_song:
        file = next_song["file"]
        title = next_song["title"]
        duration = next_song["duration"]
        user = next_song["by"]
        link = next_song["link"]
        thumbnail = next_song["thumbnail"]
        
        try:
            # C. Next Song Play karo
            stream = AudioPiped(
                file,
                audio_parameters=HighQualityAudio(),
            )
            await call_py.change_stream(chat_id, stream)
            
            # D. "Added to Queue" Message Delete karo
            queue_key = f"{chat_id}-{title}"
            if queue_key in QUEUE_MSG_ID:
                try:
                    await main_bot.delete_message(chat_id, QUEUE_MSG_ID[queue_key])
                    del QUEUE_MSG_ID[queue_key]
                except:
                    pass

            # E. Naya UI Message Bhejo (VIP Style)
            buttons = [
                [
                    InlineKeyboardButton("II", callback_data="music_pause"),
                    InlineKeyboardButton("▶", callback_data="music_resume"),
                    InlineKeyboardButton("‣‣I", callback_data="music_skip"),
                    InlineKeyboardButton("▢", callback_data="music_stop")
                ],
                [InlineKeyboardButton("📺 Watch on YouTube", url=link)]
            ]
            
            caption = f"""
<blockquote><b>✅ Started Streaming</b></blockquote>

<b>📌 Title :</b> <a href="{link}">{title}</a>
<b>⏱ Duration :</b> <code>{duration}</code>
<b>👤 Req By :</b> {user}

<b>⚡ Powered By :</b> {OWNER_NAME}
"""
            msg = await main_bot.send_photo(
                chat_id,
                photo=thumbnail,
                caption=caption,
                has_spoiler=True, # 🔥 Spoiler Logic
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.HTML
            )
            
            # ID Save karo agle deletion ke liye
            LAST_MSG_ID[chat_id] = msg.message_id

        except Exception as e:
            print(f"❌ Auto-Play Error: {e}")
            await stop_stream(chat_id)
    else:
        # F. Agar Queue khatam, toh VC chhod do
        await stop_stream(chat_id)

# --- 3. SKIP LOGIC ---
async def skip_stream(chat_id):
    """
    Manually Next Song Play Karta Hai
    """
    # Next song nikalo
    next_song = await pop_queue(chat_id)

    if next_song:
        # Purana message uda do
        if chat_id in LAST_MSG_ID:
            try: await main_bot.delete_message(chat_id, LAST_MSG_ID[chat_id])
            except: pass

        # Data Prepare
        file = next_song["file"]
        title = next_song["title"]
        link = next_song["link"]
        thumbnail = next_song["thumbnail"]
        duration = next_song["duration"]
        user = next_song["by"]

        try:
            # Stream Change
            stream = AudioPiped(file, audio_parameters=HighQualityAudio())
            await call_py.change_stream(chat_id, stream)
            
            # Queue Message Delete
            queue_key = f"{chat_id}-{title}"
            if queue_key in QUEUE_MSG_ID:
                try: await main_bot.delete_message(chat_id, QUEUE_MSG_ID[queue_key])
                except: pass

            # New Message Send
            buttons = [
                [
                    InlineKeyboardButton("II", callback_data="music_pause"),
                    InlineKeyboardButton("▶", callback_data="music_resume"),
                    InlineKeyboardButton("‣‣I", callback_data="music_skip"),
                    InlineKeyboardButton("▢", callback_data="music_stop")
                ],
                [InlineKeyboardButton("📺 Watch on YouTube", url=link)]
            ]
            caption = f"""
<blockquote><b>✅ Started Streaming</b></blockquote>

<b>📌 Title :</b> <a href="{link}">{title}</a>
<b>⏱ Duration :</b> <code>{duration}</code>
<b>👤 Req By :</b> {user}

<b>⚡ Powered By :</b> {OWNER_NAME}
"""
            msg = await main_bot.send_photo(
                chat_id, photo=thumbnail, caption=caption,
                has_spoiler=True, reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.HTML
            )
            LAST_MSG_ID[chat_id] = msg.message_id
            return True # Skip Success
        except Exception as e:
            print(f"Skip Error: {e}")
            return False
    else:
        # Agar koi next song nahi hai, toh stop kar do
        await stop_stream(chat_id)
        return False

# --- 4. STOP LOGIC ---
async def stop_stream(chat_id):
    try:
        # VC se bahar
        await call_py.leave_group_call(int(chat_id))
        # Database saaf
        await remove_active_chat(chat_id)
        await clear_queue(chat_id)
        
        # Last message delete
        if chat_id in LAST_MSG_ID:
            try: await main_bot.delete_message(chat_id, LAST_MSG_ID[chat_id])
            except: pass
            
        return True
    except:
        return False

# --- 5. PAUSE & RESUME ---
async def pause_stream(chat_id):
    try:
        await call_py.pause_stream(chat_id)
        return True
    except:
        return False

async def resume_stream(chat_id):
    try:
        await call_py.resume_stream(chat_id)
        return True
    except:
        return False

