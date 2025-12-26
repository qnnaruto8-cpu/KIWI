import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler
from telegram.constants import ParseMode, ChatAction

from tools.controller import process_stream
from tools.stream import stop_stream
# 🔥 Import Global Dictionaries from stream
from tools.stream import LAST_MSG_ID, QUEUE_MSG_ID 
from config import OWNER_NAME 

async def play_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    
    try: await update.message.delete()
    except: pass

    if not context.args:
        # Warning...
        return

    query = " ".join(context.args)
    status_msg = await context.bot.send_message(chat.id, f"<blockquote>🔍 <b>Searching...</b>\n<code>{query}</code></blockquote>", parse_mode=ParseMode.HTML)
    await context.bot.send_chat_action(chat_id=chat.id, action=ChatAction.TYPING)

    # Controller Call
    error, data = await process_stream(chat.id, user.first_name, query)

    if error:
        await status_msg.edit_text(error)
        await asyncio.sleep(5)
        try: await status_msg.delete()
        except: pass
        return

    # Data Setup
    title = data["title"]
    duration = data["duration"]
    thumbnail = data["thumbnail"]
    link = data["link"]
    img_url = data.get("img_url", thumbnail)
    
    buttons = [
        [
            InlineKeyboardButton("II", callback_data="music_pause"),
            InlineKeyboardButton("▶", callback_data="music_resume"),
            InlineKeyboardButton("‣‣I", callback_data="music_skip"),
            InlineKeyboardButton("▢", callback_data="music_stop")
        ],
        [InlineKeyboardButton("📺 Watch on YouTube", url=link)]
    ]
    markup = InlineKeyboardMarkup(buttons)

    # --- MAIN LOGIC START ---
    
    # 1. PURANA MSG DELETE (Agar Song 1 play ho raha hai to purana player hatao)
    if data["status"] is True:
        if chat.id in LAST_MSG_ID:
            try: await context.bot.delete_message(chat.id, LAST_MSG_ID[chat.id])
            except: pass

        caption = f"""
<blockquote><b>✅ Started Streaming</b></blockquote>

<b>📌 Title :</b> <a href="{link}">{title}</a>
<b>⏱ Duration :</b> <code>{duration}</code>
<b>👤 Req By :</b> {data['user']}

<b>⚡ Powered By :</b> {OWNER_NAME}
"""
        try: await status_msg.delete()
        except: pass

        # Send New Message
        final_msg = await context.bot.send_photo(
            chat.id, photo=img_url, caption=caption, 
            has_spoiler=True, reply_markup=markup, parse_mode=ParseMode.HTML
        )
        
        # 🔥 ID SAVE KARO (Taaki gaana khatam hone par delete ho)
        LAST_MSG_ID[chat.id] = final_msg.message_id

    # 2. QUEUE MSG LOGIC
    elif data["status"] is False:
        caption = f"""
<blockquote><b>📝 Added to Queue</b></blockquote>

<b>📌 Title :</b> <a href="{link}">{title}</a>
<b>🔢 Position :</b> <code>#{data['position']}</code>
<b>⏱ Duration :</b> <code>{duration}</code>
<b>👤 Req By :</b> {data['user']}

<b>⚡ Powered By :</b> {OWNER_NAME}
"""
        try: await status_msg.delete()
        except: pass

        queue_msg = await context.bot.send_photo(
            chat.id, photo=img_url, caption=caption, 
            has_spoiler=True, reply_markup=markup, parse_mode=ParseMode.HTML
        )
        
        # 🔥 QUEUE ID SAVE KARO (Taaki jab ye play ho, tab ye msg delete ho)
        # Key: ChatID + Title (Unique key to identify song)
        key = f"{chat.id}-{title}"
        QUEUE_MSG_ID[key] = queue_msg.message_id
    
    else:
        await status_msg.edit_text("Error joining VC.")

# --- STOP ---
async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    try: await update.message.delete()
    except: pass
    
    success = await stop_stream(chat_id)
    if success:
        # Stop hone par last player msg bhi uda do
        if chat_id in LAST_MSG_ID:
            try: await context.bot.delete_message(chat_id, LAST_MSG_ID[chat_id])
            except: pass
            
        m = await context.bot.send_message(chat_id, "<blockquote>⏹ <b>Stopped.</b></blockquote>", parse_mode=ParseMode.HTML)
        await asyncio.sleep(4)
        try: await m.delete()
        except: pass

def register_handlers(app):
    app.add_handler(CommandHandler(["play", "p"], play_command))
    app.add_handler(CommandHandler(["stop", "end", "skip"], stop_command))

