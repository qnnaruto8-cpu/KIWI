import asyncio
import html
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from telegram.constants import ParseMode, ChatAction
from telegram.error import TelegramError

# Imports
from tools.controller import process_stream
# ✅ FIX: 'worker_app' import kiya taaki Assistant Join kar sake
from tools.stream import stop_stream, skip_stream, pause_stream, resume_stream, worker, worker_app
from tools.stream import LAST_MSG_ID, QUEUE_MSG_ID 
from config import OWNER_NAME, ASSISTANT_ID, INSTAGRAM_LINK, BOT_NAME 

# --- HELPER: PROGRESS BAR ---
def get_progress_bar(duration):
    try:
        umm = 0 
        if 0 < umm <= 10: bar = "◉—————————"
        else: bar = "◉—————————" 
        return f"{bar}"
    except:
        return "◉—————————"

# --- PLAY COMMAND (/play) ---
async def play_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    
    try: await update.message.delete()
    except: pass 

    if not context.args:
        temp = await context.bot.send_message(chat.id, "<blockquote>❌ <b>Usage:</b> /play [Song Name]</blockquote>", parse_mode=ParseMode.HTML)
        await asyncio.sleep(5)
        try: await temp.delete()
        except: pass
        return

    query = " ".join(context.args)
    
    status_msg = await context.bot.send_message(
        chat.id,
        f"<blockquote>🔍 <b>sᴇᴀʀᴄʜɪɴɢ...</b>\n<code>{query}</code></blockquote>", 
        parse_mode=ParseMode.HTML
    )
    await context.bot.send_chat_action(chat_id=chat.id, action=ChatAction.TYPING)

    # --- 🔥 VC CHECK & ASSISTANT JOIN LOGIC (FIXED) ---
    try:
        # Step A: Assistant Check (Optional)
        try:
            assistant_member = await chat.get_member(int(ASSISTANT_ID))
            if assistant_member.status in ["kicked", "banned"]:
                await status_msg.edit_text(
                    f"<blockquote>❌ <b>ᴀssɪsᴛᴀɴᴛ ʙᴀɴɴᴇᴅ</b></blockquote>\nAssistant is banned.\nUnban ID: <code>{ASSISTANT_ID}</code>",
                    parse_mode=ParseMode.HTML,
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🗑 ᴄʟᴏsᴇ", callback_data="force_close")]])
                )
                return
        except: pass

        # Step B: Try to Join VC
        # ✅ FIX: Ab 'worker_app' (Assistant) join karega, 'worker' (Player) nahi
        try:
            invite_link = await context.bot.export_chat_invite_link(chat.id)
            try:
                await worker_app.join_chat(invite_link)
            except Exception as e:
                if "USER_ALREADY_PARTICIPANT" in str(e):
                    pass
                else:
                    # Fallback to ID join if link fails
                    try: await worker_app.join_chat(chat.id)
                    except: pass
                    
        except Exception as e:
            # Agar Assistant join na kar paaye, tab VC Off wala error dikhao
            print(f"⚠️ Join Error: {e}")
            await status_msg.edit_text(
                "<blockquote>❌ <b>ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ɪs ᴏғғ</b></blockquote>\n\n<b>Please Turn ON the Voice Chat first!</b>\n<i>Video Chat / Live Stream start karo.</i>",
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🗑 ᴄʟᴏsᴇ", callback_data="force_close")]])
            )
            return

    except Exception as e:
        print(f"Main Logic Error: {e}")

    # --- CONTROLLER LOGIC ---
    error, data = await process_stream(chat.id, user.first_name, query)

    if error:
        await status_msg.edit_text(
            f"<blockquote>❌ <b>ᴇʀʀᴏʀ</b></blockquote>\n{error}", 
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🗑 ᴄʟᴏsᴇ", callback_data="force_close")]])
        )
        return

    # Data Extract
    raw_title = data["title"]
    if len(raw_title) > 30:
        short_title = raw_title[:30] + "..."
    else:
        short_title = raw_title

    safe_title = html.escape(short_title)
    safe_user = html.escape(data["user"])
    
    duration = data["duration"]
    link = data["link"]
    img_url = data.get("thumbnail", data.get("img_url")) 
    
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
            InlineKeyboardButton(f"📸 ɪɴsᴛᴀɢʀᴀᴍ", url=INSTAGRAM_LINK)
        ],
        [InlineKeyboardButton("🗑 ᴄʟᴏsᴇ ᴘʟᴀʏᴇʀ", callback_data="force_close")]
    ]
    markup = InlineKeyboardMarkup(buttons)

    try: await status_msg.delete()
    except: pass

    if data["status"] is True:
        if chat.id in LAST_MSG_ID:
            try: await context.bot.delete_message(chat.id, LAST_MSG_ID[chat.id])
            except: pass
        
        caption = f"""
<b>✅ sᴛᴀʀᴛᴇᴅ sᴛʀᴇᴀᴍɪɴɢ</b>

<blockquote><b>🎸 ᴛɪᴛʟᴇ :</b> <a href="{link}">{safe_title}</a>
<b>⏳ ᴅᴜʀᴀᴛɪᴏɴ :</b> <code>{duration}</code>
<b>👤 ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :</b> {safe_user}</blockquote>

{bar_display}

<blockquote><b>⚡ ᴘᴏᴡᴇʀᴇᴅ ʙʏ :</b> {OWNER_NAME}</blockquote>
"""
        try:
            msg = await context.bot.send_photo(chat.id, photo=img_url, caption=caption, has_spoiler=True, reply_markup=markup, parse_mode=ParseMode.HTML)
            LAST_MSG_ID[chat.id] = msg.message_id
        except Exception as e:
            await context.bot.send_message(chat.id, caption, reply_markup=markup, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

    else:
        caption = f"""
<b>📝 ᴀᴅᴅᴇᴅ ᴛᴏ ǫᴜᴇᴜᴇ</b>

<blockquote><b>🎸 ᴛɪᴛʟᴇ :</b> <a href="{link}">{safe_title}</a>
<b>🔢 ᴘᴏsɪᴛɪᴏɴ :</b> <code>#{data['position']}</code>
<b>⏳ ᴅᴜʀᴀᴛɪᴏɴ :</b> <code>{duration}</code>
<b>👤 ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :</b> {safe_user}</blockquote>
"""
        q_msg = await context.bot.send_photo(chat.id, photo=img_url, caption=caption, has_spoiler=True, reply_markup=markup, parse_mode=ParseMode.HTML)
        key = f"{chat.id}-{safe_title}"
        QUEUE_MSG_ID[key] = q_msg.message_id

# --- UNBAN CALLBACK ---
async def unban_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat = update.effective_chat
    user = await chat.get_member(query.from_user.id)
    if user.status not in ["creator", "administrator"]:
        return await query.answer("❌ Sirf Admin Unban kar sakta hai!", show_alert=True)
    try:
        await chat.unban_member(int(ASSISTANT_ID))

