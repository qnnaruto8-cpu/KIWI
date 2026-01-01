import asyncio
import os
import html 
from pytgcalls import PyTgCalls, idle
from pytgcalls.types import AudioPiped, Update, HighQualityAudio 
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode

# Configs
from config import API_ID, API_HASH, SESSION, BOT_TOKEN, OWNER_NAME, LOG_GROUP_ID, INSTAGRAM_LINK
from tools.queue import put_queue, pop_queue, clear_queue, get_queue
from tools.database import is_active_chat, add_active_chat, remove_active_chat

# --- GLOBAL DICTIONARIES ---
LAST_MSG_ID = {}   

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
    # Simple Visual Bar
    return "◉————————————"

# --- 🔥 HELPER: SEND PLAYING MESSAGE (Common Logic) ---
async def send_now_playing(chat_id, song_data):
    """
    Ye function har jagah use hoga message bhejne ke liye.
    Code repeat nahi karna padega.
    """
    try:
        # Purana message delete karo
        if chat_id in LAST_MSG_ID:
            try: await main_bot.delete_message(chat_id, LAST_MSG_ID[chat_id])
            except: pass
        
        # Data Nikalo
        title = song_data["title"]
        duration = song_data["duration"]
        user = song_data["by"]
        link = song_data["link"]
        thumbnail = song_data["thumbnail"]

        # Title formatting
        display_title = title[:30] + "..." if len(title) > 30 else title
        bar_display = get_progress_bar(duration)

        # Buttons
        buttons = [
            [InlineKeyboardButton(f"⏳ {duration}", callback_data="GetTimer")],
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
        return True
    except Exception as e:
        print(f"❌ UI Error: {e}")
        return False

# --- 🔥 STARTUP LOGIC ---
async def start_music_worker():
    print("🔵 Starting Music Assistant (VIP Style)...")
    try:
        await worker_app.start()
        await worker.start()
        print("✅ Assistant & PyTgCalls Started!")

        if LOG_GROUP_ID:
            try:
                await worker_app.send_message(
                    int(LOG_GROUP_ID),
                    "<b>✅ Assistant Started Successfully!</b>\n\nI am online and ready to play music. 🎵"
                )
            except: pass
    except Exception as e:
        print(f"❌ Assistant Error: {e}")

# --- 1. PLAY LOGIC (Force Join Fix) ---
async def play_stream(chat_id, file_path, title, duration, user, link, thumbnail):
    safe_title = html.escape(title)
    safe_user = html.escape(user)

    stream = AudioPiped(file_path, audio_parameters=HighQualityAudio())

    # 🔥 DIRECT JOIN LOGIC
    try:
        # Check Active Call
        is_connected = False
        try:
            for call in worker.active_calls:
                if call.chat_id == chat_id:
                    is_connected = True
                    break
        except: pass

        if is_connected:
            # Agar connected hai -> Queue me daalo
            position = await put_queue(chat_id, file_path, safe_title, duration, safe_user, link, thumbnail)
            return False, position
        else:
            # Agar connected nahi hai -> Join karo
            try: await worker.leave_group_call(int(chat_id))
            except: pass
            await asyncio.sleep(0.2) 
            
            await worker.join_group_call(int(chat_id), stream)
            await add_active_chat(chat_id)
            
            # Queue me add karo aur UI bhejo
            await put_queue(chat_id, file_path, safe_title, duration, safe_user, link, thumbnail)
            
            # Message Bhejo
            song_data = {
                "title": safe_title, "duration": duration, "by": safe_user,
                "link": link, "thumbnail": thumbnail
            }
            await send_now_playing(chat_id, song_data)
            
            return True, 0

    except Exception as e:
        err_str = str(e).lower()
        if "already" in err_str:
             # Ghost Connection Fix
             try:
                await worker.leave_group_call(int(chat_id))
                await asyncio.sleep(1)
                await worker.join_group_call(int(chat_id), stream)
                await add_active_chat(chat_id)
                await put_queue(chat_id, file_path, safe_title, duration, safe_user, link, thumbnail)
                
                # Message Bhejo
                song_data = {
                    "title": safe_title, "duration": duration, "by": safe_user,
                    "link": link, "thumbnail": thumbnail
                }
                await send_now_playing(chat_id, song_data)
                return True, 0
             except Exception as final_e:
                return None, f"⚠️ Error: {final_e}"
        else:
            return None, str(e)

# --- 2. AUTO PLAY HANDLER (Optimized) ---
@worker.on_stream_end()
async def stream_end_handler(client, update: Update):
    chat_id = update.chat_id
    print(f"🔄 Stream Ended in {chat_id}")
    
    # Message saaf karo
    if chat_id in LAST_MSG_ID:
        try: await main_bot.delete_message(chat_id, LAST_MSG_ID[chat_id])
        except: pass 
    
    await asyncio.sleep(1)
    
    # Current song remove karo
    await pop_queue(chat_id)
    
    # Next check karo
    queue = await get_queue(chat_id)
    
    if queue and len(queue) > 0:
        next_song = queue[0]
        print(f"🎵 Auto-Playing Next: {next_song['title']}")
        
        try:
            stream = AudioPiped(next_song["file"], audio_parameters=HighQualityAudio())
            
            # Try switching stream
            try:
                await worker.change_stream(chat_id, stream)
            except Exception as e:
                print(f"⚠️ Change Failed, Re-Joining... {e}")
                try: await worker.leave_group_call(chat_id)
                except: pass
                await asyncio.sleep(1)
                await worker.join_group_call(chat_id, stream)

            # Send UI
            await send_now_playing(chat_id, next_song)

        except Exception as e:
            print(f"❌ Auto-Play Error: {e}")
            await stop_stream(chat_id)

    else:
        print(f"✅ Queue Empty for {chat_id}, Leaving VC.")
        await stop_stream(chat_id)

# --- 3. SKIP LOGIC ---
async def skip_stream(chat_id):
    # Current pop karo
    await pop_queue(chat_id)
    
    # Next check karo
    queue = await get_queue(chat_id)
    
    if queue and len(queue) > 0:
        next_song = queue[0]
        try:
            stream = AudioPiped(next_song["file"], audio_parameters=HighQualityAudio())
            await worker.change_stream(chat_id, stream)
            # Send UI
            await send_now_playing(chat_id, next_song)
            return True 
        except Exception as e:
            print(f"Skip Error: {e}")
            await stop_stream(chat_id)
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
    except Exception as e:
        print(f"Stop Stream Error: {e}")
        return False

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

# --- 6. GET CURRENT PLAYING ---
async def get_current_playing(chat_id):
    queue = await get_queue(chat_id)
    if queue and len(queue) > 0:
        return queue[0]
    return None
    
