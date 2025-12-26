import asyncio
import html
import math 
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from telegram.constants import ParseMode, ChatAction
from telegram.error import TelegramError

# Imports
from tools.controller import process_stream
from tools.stream import stop_stream, skip_stream, pause_stream, resume_stream, worker
from tools.stream import LAST_MSG_ID, QUEUE_MSG_ID
from config import OWNER_NAME, ASSISTANT_ID, INSTAGRAM_LINK, BOT_NAME

# --- HELPER: PROGRESS BAR LOGIC ---
def get_progress_bar(duration):
    """
    Static aesthetic progress bar.
    """
    try:
        umm = 0 
        if 0 < umm <= 10: bar = "◉—————————"
        elif 10 < umm < 20: bar = "—◉————————"
        elif 20 <= umm < 30: bar = "——◉———————"
        elif 30 <= umm < 40: bar = "———◉——————"
        elif 40 <= umm < 50: bar = "————◉—————"
        elif 50 <= umm < 60: bar = "—————◉————"
        elif 60 <= umm < 70: bar = "——————◉———"
        elif 70 <= umm < 80: bar = "———————◉——"
        elif 80 <= umm < 95: bar = "————————◉—"
        else: bar = "◉—————————" 
        return f"{bar}"
    except:
        return "◉—————————"

# --- PLAY COMMAND (/play) ---
async def play_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    # 0. Auto-Delete User Command
    try: await update.message.delete()
    except: pass

    if not context.args:
        temp = await context.bot.send_message(chat.id, "<blockquote>❌ <b>Usage:</b> /play [Song Name]</blockquote>", parse_mode=ParseMode.HTML)
        await asyncio.sleep(5)
        try: await temp.delete()
        except: pass
        return

    query = " ".join(context.args)

    # 1. Searching Message
    status_msg = await context.bot.send_message(
        chat.id,
        f"<blockquote>🔍 <b>sᴇᴀʀᴄʜɪɴɢ...</b>\n<code>{query}</code></blockquote>",
        parse_mode=ParseMode.HTML
    )
    await context.bot.send_chat_action(chat_id=chat.id, action=ChatAction.TYPING)

    # --- 🔥 VC CHECK & ASSISTANT JOIN LOGIC ---
    try:
        # Step A: Check if Assistant is in Group
        try:
            assistant_member = await chat.get_member(int(ASSISTANT_ID))
            if assistant_member.status in ["kicked", "banned"]:
                await status_msg.edit_text(
                    f"<blockquote>❌ <b>ᴀssɪsᴛᴀɴᴛ ʙᴀɴɴᴇᴅ</b></blockquote>\nAssistant is banned in {chat.title}.\nUnban it to play music.",
                    parse_mode=ParseMode.HTML,
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🗑 ᴄʟᴏsᴇ", callback_data="force_close")]])
                )
                return
        except: pass

        # Step B: Try to Join VC
        try:
            invite_link = await context.bot.export_chat_invite_link(chat.id)
            await worker.join_chat(invite_link)
        except Exception as e:
            err_str = str(e).lower()
            if "already" in err_str or "participant" in err_str:
                pass 
            else:
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

    # Data Extract & Shortening Title
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

    # 🔥 Progress Bar Generate
    bar_display = get_progress_bar(duration)

    # 🔥 BUTTONS
    buttons = [
        [
            InlineKeyboardButton(f"00:00 {bar_display} {duration}", callback_data="GetTimer")
        ],
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
        [
            InlineKeyboardButton("🗑 ᴄʟᴏsᴇ ᴘʟᴀʏᴇʀ", callback_data="force_close")
        ]
    ]
    markup = InlineKeyboardMarkup(buttons)

    # --- MESSAGE SENDING LOGIC ---
    try: await status_msg.delete()
    except: pass

    if data["status"] is True:
        if chat.id in LAST_MSG_ID:
            try: await context.bot.delete_message(chat.id, LAST_MSG_ID[chat.id])
            except: pass

        # 🔥 UPDATED CAPTION (Separate Blockquotes)
        caption = f"""
<blockquote><b>✅ sᴛᴀʀᴛᴇᴅ sᴛʀᴇᴀᴍɪɴɢ</b></blockquote>

<blockquote><b>🎸 ᴛɪᴛʟᴇ :</b> <a href="{link}">{safe_title}</a>
<b>⏳ ᴅᴜʀᴀᴛɪᴏɴ :</b> <code>{duration}</code>
<b>👤 ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :</b> {safe_user}</blockquote>

<blockquote><b>⚡ ᴘᴏᴡᴇʀᴇᴅ ʙʏ :</b> {OWNER_NAME}</blockquote>
"""
        try:
            msg = await context.bot.send_photo(chat.id, photo=img_url, caption=caption, has_spoiler=True, reply_markup=markup, parse_mode=ParseMode.HTML)
            LAST_MSG_ID[chat.id] = msg.message_id
        except Exception as e:
            await context.bot.send_message(chat.id, caption, reply_markup=markup, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

    else:
        # Queue Caption
        caption = f"""
<blockquote><b>📝 ᴀᴅᴅᴇᴅ ᴛᴏ ǫᴜᴇᴜᴇ</b></blockquote>

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
        await query.message.edit_text("<blockquote>✅ <b>Assistant Unbanned!</b>\nAb /play try karo.</blockquote>", parse_mode=ParseMode.HTML)
    except Exception as e:
        await query.answer(f"Error: {e}", show_alert=True)

# --- COMMANDS ---
async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    command = update.message.text.split()[0].replace("/", "").lower()

    try: await update.message.delete()
    except: pass

    msg_text = ""
    if command in ["stop", "end"]:
        await stop_stream(chat_id)
        msg_text = "<blockquote>⏹ <b>sᴛʀᴇᴀᴍ sᴛᴏᴘᴘᴇᴅ</b></blockquote>"
    elif command in ["skip", "next"]:
        await skip_stream(chat_id)
        msg_text = "<blockquote>⏭ <b>sᴋɪᴘᴘᴇᴅ</b></blockquote>"
    elif command == "pause":
        await pause_stream(chat_id)
        msg_text = "<blockquote>II <b>sᴛʀᴇᴀᴍ ᴘᴀᴜsᴇᴅ</b></blockquote>"
    elif command == "resume":
        await resume_stream(chat_id)
        msg_text = "<blockquote>▶ <b>sᴛʀᴇᴀᴍ ʀᴇsᴜᴍᴇᴅ</b></blockquote>"

    if chat_id in LAST_MSG_ID:
        try: await context.bot.delete_message(chat_id, LAST_MSG_ID[chat_id])
        except: pass

    temp = await context.bot.send_message(chat_id, msg_text, parse_mode=ParseMode.HTML)
    await asyncio.sleep(4)
    try: await temp.delete()
    except: pass

def register_handlers(app):
    app.add_handler(CommandHandler(["play", "p"], play_command))
    app.add_handler(CommandHandler(["stop", "end", "skip", "next", "pause", "resume"], stop_command))
    app.add_handler(CallbackQueryHandler(unban_cb, pattern="unban_assistant"))
    print("  ✅ Music Module Loaded: Auto-Join & Anti-Ban!")
    
