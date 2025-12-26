import asyncio
import html  # ✅ IMP: Crash fix karne ke liye
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from telegram.constants import ParseMode, ChatAction
from telegram.error import TelegramError

# Imports
from tools.controller import process_stream
# Worker import kiya taaki join karwa sakein
from tools.stream import stop_stream, skip_stream, pause_stream, resume_stream, worker 
from tools.stream import LAST_MSG_ID, QUEUE_MSG_ID 
from config import OWNER_NAME, ASSISTANT_ID 

# --- PLAY COMMAND (/play) ---
async def play_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    
    # 0. Auto-Delete User Command
    try: await update.message.delete()
    except: pass 

    if not context.args:
        # Check for reply (File) logic future ke liye, abhi basic usage
        temp = await context.bot.send_message(chat.id, "<blockquote>❌ <b>Usage:</b> /play [Song Name]</blockquote>", parse_mode=ParseMode.HTML)
        await asyncio.sleep(5)
        try: await temp.delete()
        except: pass
        return

    query = " ".join(context.args)
    
    # 1. Searching Message
    status_msg = await context.bot.send_message(
        chat.id,
        f"<blockquote>🔍 <b>Searching...</b>\n<code>{query}</code></blockquote>", 
        parse_mode=ParseMode.HTML
    )
    await context.bot.send_chat_action(chat_id=chat.id, action=ChatAction.TYPING)

    # --- 🔥 ASSISTANT CHECK & AUTO JOIN LOGIC ---
    try:
        # Step A: Check if Assistant is in Group
        # Note: ASSISTANT_ID config.py me hona chahiye (Integer)
        try:
            assistant_member = await chat.get_member(int(ASSISTANT_ID))
            
            # Step B: Agar Assistant Ban hai
            if assistant_member.status in ["kicked", "banned"]:
                await status_msg.edit_text(
                    f"<blockquote>❌ <b>Assistant Banned</b></blockquote>\nAssistant is banned in {chat.title}.\nUnban it to play music.",
                    parse_mode=ParseMode.HTML,
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔓 Unban Assistant", callback_data="unban_assistant")]])
                )
                return
        except ValueError:
             print("⚠️ Config Error: ASSISTANT_ID integer nahi hai.")

    except TelegramError:
        # Step C: Agar Assistant Group mein nahi hai (Member not found error)
        try:
            await status_msg.edit_text("<blockquote>🔄 <b>Assistant Joining...</b></blockquote>", parse_mode=ParseMode.HTML)
            
            # 1. Link Generate karo
            invite_link = await context.bot.export_chat_invite_link(chat.id)
            
            # 2. Assistant ko join karwao (Using worker/app client)
            try:
                await worker.join_chat(invite_link)
            except Exception as e:
                # Kabhi kabhi wo already join hota hai par cache update nahi hota
                print(f"Join Warning: {e}")
            
            # 3. Thoda wait karo taaki Telegram process kar le
            await asyncio.sleep(2)
            
        except Exception as e:
            return await status_msg.edit_text(
                f"<blockquote>❌ <b>Assistant Join Error</b></blockquote>\nMake me <b>Admin</b> with Invite Users permission.\n\nError: <code>{e}</code>",
                parse_mode=ParseMode.HTML
            )

    # --- CONTROLLER LOGIC ---
    error, data = await process_stream(chat.id, user.first_name, query)

    if error:
        await status_msg.edit_text(f"<blockquote>❌ {error}</blockquote>", parse_mode=ParseMode.HTML)
        await asyncio.sleep(5)
        try: await status_msg.delete()
        except: pass
        return

    # Data Extract & Safety Fix
    # ✅ FIX: HTML Escape (Title aur Name ko safe banao taaki crash na ho)
    safe_title = html.escape(data["title"])
    safe_user = html.escape(data["user"])
    
    duration = data["duration"]
    link = data["link"]
    img_url = data.get("thumbnail", data.get("img_url")) # Fallback check
    
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

    # --- MESSAGE SENDING LOGIC ---
    # Delete old Searching msg
    try: await status_msg.delete()
    except: pass

    # Caption Prep
    if data["status"] is True:
        # Purana player delete agar exist kare
        if chat.id in LAST_MSG_ID:
            try: await context.bot.delete_message(chat.id, LAST_MSG_ID[chat.id])
            except: pass
            
        caption = f"""
<blockquote><b>✅ Started Streaming</b></blockquote>

<b>📌 Title :</b> <a href="{link}">{safe_title}</a>
<b>⏱ Duration :</b> <code>{duration}</code>
<b>👤 Req By :</b> {safe_user}

<b>⚡ Powered By :</b> {OWNER_NAME}
"""
        try:
            msg = await context.bot.send_photo(chat.id, photo=img_url, caption=caption, has_spoiler=True, reply_markup=markup, parse_mode=ParseMode.HTML)
            LAST_MSG_ID[chat.id] = msg.message_id
        except Exception as e:
            # Fallback agar photo fail ho
            await context.bot.send_message(chat.id, caption, reply_markup=markup, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

    else:
        # Queue Logic
        caption = f"""
<blockquote><b>📝 Added to Queue</b></blockquote>

<b>📌 Title :</b> <a href="{link}">{safe_title}</a>
<b>🔢 Position :</b> <code>#{data['position']}</code>
<b>⏱ Duration :</b> <code>{duration}</code>
<b>👤 Req By :</b> {safe_user}

<b>⚡ Powered By :</b> {OWNER_NAME}
"""
        q_msg = await context.bot.send_photo(chat.id, photo=img_url, caption=caption, has_spoiler=True, reply_markup=markup, parse_mode=ParseMode.HTML)
        key = f"{chat.id}-{safe_title}"
        QUEUE_MSG_ID[key] = q_msg.message_id


# --- UNBAN CALLBACK ---
async def unban_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat = update.effective_chat
    
    # Admin Check (Ispe rakhna padega kyunki unban sirf admin kar sakta hai)
    user = await chat.get_member(query.from_user.id)
    if user.status not in ["creator", "administrator"]:
        return await query.answer("❌ Sirf Admin Unban kar sakta hai!", show_alert=True)

    try:
        await chat.unban_member(int(ASSISTANT_ID))
        await query.message.edit_text("<blockquote>✅ <b>Assistant Unbanned!</b>\nAb /play try karo.</blockquote>", parse_mode=ParseMode.HTML)
    except Exception as e:
        await query.answer(f"Error: {e}", show_alert=True)

# --- COMMANDS (STOP/SKIP/PAUSE/RESUME) ---
# 🔓 NO ADMIN CHECK HERE (As requested)
async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    command = update.message.text.split()[0].replace("/", "").lower() # Command nikalo
    
    try: await update.message.delete()
    except: pass
    
    msg_text = ""
    
    # Logic distribute karo
    if command in ["stop", "end"]:
        await stop_stream(chat_id)
        msg_text = "<blockquote>⏹ <b>Stopped.</b></blockquote>"
        
    elif command in ["skip", "next"]:
        await skip_stream(chat_id)
        msg_text = "<blockquote>⏭ <b>Skipped.</b></blockquote>"
        
    elif command == "pause":
        await pause_stream(chat_id)
        msg_text = "<blockquote>II <b>Paused.</b></blockquote>"
        
    elif command == "resume":
        await resume_stream(chat_id)
        msg_text = "<blockquote>▶ <b>Resumed.</b></blockquote>"

    # Message update (Last player remove)
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
    
