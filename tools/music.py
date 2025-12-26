from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler
from telegram.constants import ParseMode, ChatAction

# Import hamara Naya Controller aur Engine
from tools.controller import process_stream
from tools.stream import stop_stream

# --- PLAY COMMAND (/play) ---
async def play_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    
    # 1. Check karo user ne gaane ka naam diya hai ya nahi
    if not context.args:
        return await update.message.reply_text(
            "❌ **Usage:** `/play [Song Name or Link]`", 
            parse_mode=ParseMode.MARKDOWN
        )

    query = " ".join(context.args)
    
    # 2. Searching Message (User ko batao kaam chalu hai)
    status_msg = await update.message.reply_text(
        f"🍭", 
        parse_mode=ParseMode.MARKDOWN
    )
    
    # Typing action dikhao
    await context.bot.send_chat_action(chat_id=chat.id, action=ChatAction.TYPING)

    # 3. Controller ko kaam do (Search -> Download -> Ready)
    # Ye function heavy lifting karega
    error, data = await process_stream(chat.id, user.first_name, query)

    # Agar koi error aaya (jaise song nahi mila)
    if error:
        return await status_msg.edit_text(error)

    # 4. Result Process karo
    title = data["title"]
    duration = data["duration"]
    thumbnail = data["thumbnail"]
    requested_by = data["user"]
    link = data["link"]
    
    # Simple Button (YouTube Link)
    button = [[InlineKeyboardButton("📺 Watch on YouTube", url=link)]]
    markup = InlineKeyboardMarkup(button)

    # Case A: Gana Bajna Shuru hua (Direct Play)
    if data["status"] is True:
        text = f"""
✅ **Started Streaming**

📌 **Title:** [{title}]({link})
⏱ **Duration:** `{duration}`
👤 **Req By:** {requested_by}
"""
        # Purana "Searching" message delete karo
        await status_msg.delete()
        
        # Photo ke saath naya message bhejo
        await context.bot.send_photo(
            chat.id, 
            photo=thumbnail, 
            caption=text, 
            reply_markup=markup, 
            parse_mode=ParseMode.MARKDOWN
        )

    # Case B: Gana Queue mein gaya (Wait list)
    elif data["status"] is False:
        position = data["position"]
        text = f"""
📝 **Added to Queue**

📌 **Title:** [{title}]({link})
🔢 **Position:** `#{position}`
⏱ **Duration:** `{duration}`
👤 **Req By:** {requested_by}
"""
        await status_msg.delete()
        await context.bot.send_photo(
            chat.id, 
            photo=thumbnail, 
            caption=text,
            has_spoiler=True,
            reply_markup=markup, 
            parse_mode=ParseMode.MARKDOWN
        )
    
    # Case C: Assistant VC Join nahi kar paya
    else:
        await status_msg.edit_text("❌ **Error:** Assistant VC join nahi kar paya. Kya Assistant Group mein Admin hai?")

# --- STOP COMMAND (/stop) ---
async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    # Stream Engine ko bolo rukne ke liye
    success = await stop_stream(chat_id)
    
    if success:
        await update.message.reply_text("⏹ **Music Stopped & Queue Cleared.**")
    else:
        await update.message.reply_text("❌ Nothing is playing to stop.")

# --- 🔌 AUTO LOADER REGISTER FUNCTION ---
# Main.py is function ko call karega
def register_handlers(app):
    app.add_handler(CommandHandler(["play", "p"], play_command))
    app.add_handler(CommandHandler(["stop", "end", "skip", "pause"], stop_command))
    print("  ✅ Music Module Loaded: /play, /stop")
