import asyncio
import os
import html 
from pytgcalls import PyTgCalls, idle
from pytgcalls.types import AudioPiped, Update
from pytgcalls.types import HighQualityAudio 
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode

# Configs
from config import API_ID, API_HASH, SESSION, BOT_TOKEN, OWNER_NAME, LOG_GROUP_ID, INSTAGRAM_LINK
from tools.queue import put_queue, pop_queue, clear_queue
from tools.database import is_active_chat, add_active_chat, remove_active_chat

# --- GLOBAL DICTIONARIES ---
LAST_MSG_ID = {}   
QUEUE_MSG_ID = {}  

# --- CLIENT SETUP ---
from pyrogram import Client
worker_app = Client(
    "MusicWorker",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION,
    in_memory=True,
)
worker = PyTgCalls(worker_app)

main_bot = Bot(token=BOT_TOKEN)

# --- HELPER: PROGRESS BAR ---
def get_progress_bar(duration):
    try:
        umm = 0 
        if 0 < umm <= 10: bar = "◉—————————"
        else: bar = "◉—————————" 
        return f"{bar}"
    except:
        return "◉—————————"

# --- 🔥 STARTUP LOGIC ---
async def start_music_worker():
    print("🔵 Starting Music Assistant (VIP Style)...")
    try:
        await worker_app.start()
        await worker.start()
        print("✅ Assistant & PyTgCalls Started!")

        try:
            if LOG_GROUP_ID:
                await worker_app.send_message(
                    int(LOG_GROUP_ID),
                    "<b>✅ Assistant Started Successfully!</b>\n\nI am online and ready to play music. 🎵"
                )
        except Exception as e:
            print(f"⚠️ Log Message Failed: {e}")

    except Exception as e:
        print(f"❌ Assistant Error: {e}")

# --- 1. PLAY LOGIC (Force Join Fix) ---
async def play_stream(chat_id, file_path, title, duration, user, link, thumbnail):
    safe_title = html.escape(title)
    safe_user = html.escape(user)

    # Stream Object Prepare karo
    stream = AudioPiped(file_path, audio_parameters=HighQualityAudio())

    # 🔥 DIRECT JOIN LOGIC (No Database Trust)
    try:
        # Check karo agar pehle se connected hai
        is_connected = False
        try:
            for call in worker.active_calls:
                if call.chat_id == chat_id:
                    is_connected = True
                    break
        except: pass

        if is_connected:
            # Agar sach me connected hai -> Queue
            position = await put_queue(chat_id, file_path, safe_title, duration, safe_user, link, thumbnail)
            return False, position
        else:
            # Agar connected nahi hai -> Join (Play)
            try: await worker.leave_group_call(int(chat_id))
            except: pass
            
            await asyncio.sleep(0.2) 
            
            await worker.join_group_call(
                int(chat_id),
                stream,
            )
            await add_active_chat(chat_id)
            await put_queue(chat_id, file_path, safe_title, duration, safe_user, link, thumbnail)
            return True, 0

    except Exception as e:
        # Error Handling
        err_str = str(e).lower()
        if "no active group call" in err_str:
            return None, "❌ **Voice Chat is OFF!**"
        elif "already" in err_str:
             # Ghost Connection Fix
             try:
                await worker.leave_group_call(int(chat_id))
                await asyncio.sleep(1)
                await worker.join_group_call(int(chat_id), stream)
                await add_active_chat(chat_id)
                await put_queue(chat_id, file_path, safe_title, duration, safe_user, link, thumbnail)
                return True, 0
             except Exception as final_e:
                return None, f"⚠️ Error: {final_e}"
        else:
            return None, str(e)

# --- 2. AUTO PLAY HANDLER (Next Song Fix) ---
@worker.on_stream_end()
async def stream_end_handler(client, update: Update):
    chat_id = update.chat_id
    print(f"🔄 Stream Ended in {chat_id}")

    # Old Message Delete
    if chat_id in LAST_MSG_ID:
        try: await main_bot.delete_message(chat_id, LAST_MSG_ID[chat_id])
        except: pass 
    
    # Next Song Nikalo
    next_song = await pop_queue(chat_id)

    if next_song:
        file = next_song["file"]
        title = next_song["title"] 
        duration = next_song["duration"]
        user = next_song["by"] 
        link = next_song["link"]
        thumbnail = next_song["thumbnail"]
        
        # 🔥 ROBUST NEXT PLAY LOGIC
        try:
            stream = AudioPiped(file, audio_parameters=HighQualityAudio())
            
            # Try 1: Change Stream (Normal transition)
            try:
                await worker.change_stream(chat_id, stream)
            except Exception as e:
                # Try 2: Force Join (Agar glitch ki wajah se nikal gaya tha)
                print(f"⚠️ Change Stream Failed ({e}), Trying Force Join...")
                await worker.join_group_call(chat_id, stream)

            # UI Update
            if len(title) > 30: display_title = title[:30] + "..."
            else: display_title = title
            
            bar_display = get_progress_bar(duration)

            buttons = [
                [InlineKeyboardButton(f"00:00 {bar_display} {duration}", callback_data="GetTimer")],
                [
                    InlineKeyboardButton("II", callback_data="music_pause"),
                    InlineKeyboardButton("▶", callback_data="music_resume"),
                    InlineKeyboardButton("‣‣I", callback_data="music_skip"),
                    InlineKeyboardButton("▢", callback_data="music_stop")
                ],
                [
                    InlineKeyboardButton("📺 ʏᴏᴜᴛᴜʙᴇ", url=link),
                    InlineKeyboardButton("📸 ɪɴsᴛᴀɢʀᴀᴍ", url=INSTAGRAM_LINK)
                ],
                [InlineKeyboardButton("🗑 ᴄʟᴏsᴇ ᴘʟᴀʏᴇʀ", callback_data="force_close")]
            ]
            
            caption = f"""
<b>✅ sᴛᴀʀᴛᴇᴅ sᴛʀᴇᴀᴍɪɴɢ</b>

<blockquote><b>🎸 ᴛɪᴛʟᴇ :</b> <a href="{link}">{display_title}</a>
<b>⏳ ᴅᴜʀᴀᴛɪᴏɴ :</b> <code>{duration}</code>
<b>👤 ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :</b> {user}</blockquote>

{bar_display}

<blockquote><b>⚡ ᴘᴏᴡᴇʀᴇᴅ ʙʏ :</b> {OWNER_NAME}</blockquote>
"""
            msg = await main_bot.send_photo(
                chat_id,
                photo=thumbnail,
                caption=caption,
                has_spoiler=True, 
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.HTML
            )
            LAST_MSG_ID[chat_id] = msg.message_id

        except Exception as e:
            print(f"❌ Auto-Play Critical Error: {e}")
            await stop_stream(chat_id)

    else:
        # Queue Empty -> Stop
        print(f"✅ Queue Empty for {chat_id}, Leaving VC.")
        await stop_stream(chat_id)

# --- 3. SKIP LOGIC ---
async def skip_stream(chat_id):
    if chat_id in LAST_MSG_ID:
        try: await main_bot.delete_message(chat_id, LAST_MSG_ID[chat_id])
        except: pass

    next_song = await pop_queue(chat_id)

    if next_song:
        file = next_song["file"]
        title = next_song["title"]
        link = next_song["link"]
        thumbnail = next_song["thumbnail"]
        duration = next_song["duration"]
        user = next_song["by"]

        try:
            stream = AudioPiped(file, audio_parameters=HighQualityAudio())
            await worker.change_stream(chat_id, stream)
            
            if len(title) > 30: display_title = title[:30] + "..."
            else: display_title = title

            bar_display = get_progress_bar(duration)

            buttons = [
                [InlineKeyboardButton(f"00:00 {bar_display} {duration}", callback_data="GetTimer")],
                [
                    InlineKeyboardButton("II", callback_data="music_pause"),
                    InlineKeyboardButton("▶", callback_data="music_resume"),
                    InlineKeyboardButton("‣‣I", callback_data="music_skip"),
                    InlineKeyboardButton("▢", callback_data="music_stop")
                ],
                [
                    InlineKeyboardButton("📺 ʏᴏᴜᴛᴜʙᴇ", url=link),
                    InlineKeyboardButton("📸 ɪɴsᴛᴀɢʀᴀᴍ", url=INSTAGRAM_LINK)
                ],
                [InlineKeyboardButton("🗑 ᴄʟᴏsᴇ ᴘʟᴀʏᴇʀ", callback_data="force_close")]
            ]
            
            caption = f"""
<b>✅ sᴛᴀʀᴛᴇᴅ sᴛʀᴇᴀᴍɪɴɢ</b>

<blockquote><b>🎸 ᴛɪᴛʟᴇ :</b> <a href="{link}">{display_title}</a>
<b>⏳ ᴅᴜʀᴀᴛɪᴏɴ :</b> <code>{duration}</code>
<b>👤 ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :</b> {user}</blockquote>

{bar_display}

<blockquote><b>⚡ ᴘᴏᴡᴇʀᴇᴅ ʙʏ :</b> {OWNER_NAME}</blockquote>
"""
            msg = await main_bot.send_photo(
                chat_id, photo=thumbnail, caption=caption,
                has_spoiler=True, reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.HTML
            )
            LAST_MSG_ID[chat_id] = msg.message_id
            return True 
        except Exception as e:
            print(f"Skip Error: {e}")
            return False
    else:
        await stop_stream(chat_id)
        return False

# --- 4. STOP LOGIC ---
async def stop_stream(chat_id):
    try:
        await worker.leave_group_call(int(chat_id))
        await remove_active_chat(chat_id)
        await clear_queue(chat_id)
        if chat_id in LAST_MSG_ID:
            try: await main_bot.delete_message(chat_id, LAST_MSG_ID[chat_id])
            except: pass
        return True
    except: return False

# --- 5. PAUSE & RESUME ---
async def pause_stream(chat_id):
    try:
        await worker.pause_stream(chat_id)
        return True
    except: return False

async def resume_stream(chat_id):
    try:
        await worker.resume_stream(chat_id)
        return True
    except: return False

