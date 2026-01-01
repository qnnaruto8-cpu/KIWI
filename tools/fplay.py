import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler
from telegram.constants import ParseMode, ChatAction

# Imports
from tools.controller import process_stream
from tools.stream import play_stream
from tools.database import get_cached_song, save_cached_song
from tools.youtube import YouTubeAPI # ✅ YouTube Import kiya
from tools.utils import run_sync # ✅ Anti-Freeze ke liye

# Initialize YouTube
YouTube = YouTubeAPI()

# --- FPLAY COMMAND (/fplay) ---
async def fplay_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    
    try: await update.message.delete()
    except: pass

    if not context.args:
        return await context.bot.send_message(chat.id, "❌ <b>Usage:</b> /fplay [Song Name]", parse_mode=ParseMode.HTML)

    query = " ".join(context.args)
    
    status_msg = await context.bot.send_message(
        chat.id,
        f"<blockquote>⚡ <b>Fast Searching...</b>\n<code>{query}</code></blockquote>", 
        parse_mode=ParseMode.HTML
    )

    # --- 🚀 STEP 1: CHECK DATABASE (CACHE) ---
    cached_data = await get_cached_song(query)

    if cached_data:
        # ✅ Agar Cache mil gaya (Search Skip Karo)
        title = cached_data["title"]
        duration = cached_data["duration"]
        thumbnail = cached_data["thumbnail"]
        link = cached_data["link"]
        
        await status_msg.edit_text(f"<blockquote>⬇️ <b>Found in Cache! Downloading...</b>\n{title}</blockquote>", parse_mode=ParseMode.HTML)
        
        # 🔥 MAIN FIX: Cache milne ke baad bhi DOWNLOAD karna padega
        try:
            # Background me download karo taaki bot freeze na ho
            file_path, direct_link = await run_sync(
                YouTube.download,
                link,
                mystic=None,
                title=title,
                format_id="bestaudio"
            )
            
            # Ab Play karo (File Path bhej rahe hain, Link nahi)
            success, position = await play_stream(chat.id, file_path, title, duration, user.first_name, link, thumbnail)
            
            if success:
                # Buttons (Music.py style)
                kb = [[InlineKeyboardButton("🗑 Close", callback_data="force_close")]]
                await context.bot.send_photo(
                    chat.id, 
                    photo=thumbnail, 
                    caption=f"🚀 <b>Fast Play (Cached):</b>\n🎵 <b>{title}</b>\n⏱ <b>Duration:</b> {duration}",
                    reply_markup=InlineKeyboardMarkup(kb)
                )
            else:
                await context.bot.send_message(chat.id, "❌ Stream Error: Added to Queue.")

            await status_msg.delete()
            return

        except Exception as e:
            print(f"❌ Cache Play Error: {e}")
            # Agar Cache wala fail ho jaye, to niche Normal Play pe girne do...

    # --- 🐢 STEP 2: AGAR CACHE NAHI HAI (NORMAL PLAY + SAVE) ---
    await status_msg.edit_text(f"<blockquote>🔍 <b>Searching Web...</b>\n<code>{query}</code></blockquote>", parse_mode=ParseMode.HTML)
    
    # Controller call karo (Search + Download)
    error, data = await process_stream(chat.id, user.first_name, query)
    
    if error:
        return await status_msg.edit_text(error)

    # --- 🔥 STEP 3: SAVE TO DATABASE FOR NEXT TIME ---
    # Hum result ko save kar lenge taaki agli baar /fplay kaam kare
    cache_entry = {
        "title": data["title"],
        "duration": data["duration"],
        "thumbnail": data["thumbnail"],
        "link": data["link"] # YouTube URL
    }
    # Future ke liye save karo
    await save_cached_song(query, cache_entry)

    # Send Playing Message
    kb = [[InlineKeyboardButton("🗑 Close", callback_data="force_close")]]
    await context.bot.send_photo(
        chat.id, 
        photo=data["thumbnail"], 
        caption=f"🎵 <b>Playing:</b> {data['title']}\n⏱ <b>Duration:</b> {data['duration']}\n👤 <b>Req:</b> {user.first_name}",
        reply_markup=InlineKeyboardMarkup(kb)
    )
    
    await status_msg.delete()

def register_handlers(app):
    app.add_handler(CommandHandler(["fplay", "fp"], fplay_command))
    print("  ✅ Fast-Play Module Loaded!")
    
