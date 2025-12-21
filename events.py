import html
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from database import register_user, check_registered, get_logger_group, update_group_activity, remove_group

# --- HELPERS ---
async def delete_msg(context: ContextTypes.DEFAULT_TYPE):
    try: await context.bot.delete_message(context.job.chat_id, context.job.data)
    except: pass

def to_fancy(text):
    mapping = {'A': 'Λ', 'E': 'Є', 'S': 'δ', 'O': 'σ', 'T': 'ᴛ', 'N': 'ɴ', 'M': 'ᴍ', 'U': 'ᴜ', 'R': 'ʀ', 'D': 'ᴅ', 'C': 'ᴄ', 'P': 'ᴘ', 'G': 'ɢ', 'B': 'ʙ', 'L': 'ʟ', 'W': 'ᴡ', 'K': 'ᴋ', 'J': 'ᴊ', 'Y': 'ʏ', 'I': 'ɪ', 'H': 'ʜ'}
    return "".join(mapping.get(c.upper(), c) for c in text)

# --- 1. WELCOME USER & BOT ADD LOG ---
async def welcome_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.new_chat_members:
        return

    chat = update.effective_chat
    user = update.effective_user # Who added or joined
    
    # 🟢 STEP 1: Group Activity Update
    try:
        update_group_activity(chat.id, chat.title)
    except Exception as e:
        print(f"DB Error (update_group_activity): {e}")

    for member in update.message.new_chat_members:
        # 🤖 A. IF BOT ADDED (Logger Log)
        if member.id == context.bot.id:
            await update.message.reply_text(
                "😎 <b>Thanks for adding me!</b>\nMake me <b>Admin</b> to use full power! ⚡",
                parse_mode=ParseMode.HTML
            )
            
            logger_id = get_logger_group()
            if logger_id:
                msg = f"""
<blockquote>🟢 <b>{to_fancy('BOT ADDED TO GROUP')}</b></blockquote>

<blockquote>
<b>📍 ɢʀᴏᴜᴘ :</b> {html.escape(chat.title)}
<b>🆔 ɪᴅ :</b> <code>{chat.id}</code>
<b>👤 ᴀᴅᴅᴇᴅ ʙʏ :</b> {html.escape(user.first_name) if user else 'Unknown'}
<b>🆔 ᴜsᴇʀ ɪᴅ :</b> <code>{user.id if user else 'N/A'}</code>
</blockquote>
"""
                kb = [[InlineKeyboardButton("❌ Close", callback_data="close_log")]]
                try:
                    await context.bot.send_message(
                        chat_id=logger_id, 
                        text=msg, 
                        reply_markup=InlineKeyboardMarkup(kb), 
                        parse_mode=ParseMode.HTML
                    )
                except: 
                    pass
            continue
            
        # 👤 B. NORMAL USER JOINED
        if not member.is_bot:
            if not check_registered(member.id):
                register_user(member.id, member.first_name)
            
            # Stylish Welcome Message
            msg_text = f"<blockquote>👀 Hey <b>{html.escape(member.first_name)}</b>, welcome to <b>゜{html.escape(chat.title)}</b></blockquote>"
            try:
                await update.message.reply_text(msg_text, parse_mode=ParseMode.HTML)
            except: 
                pass

# --- 2. TRACK LEAVE (BOT REMOVE & STATS FIX) ---
async def track_leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.left_chat_member:
        return

    left_user = update.message.left_chat_member
    action_by = update.message.from_user
    chat = update.effective_chat
    
    # 🤖 A. IF BOT REMOVED / LEFT
    if left_user.id == context.bot.id:
        
        # 🔥 STEP 1: Remove Group from DB
        try:
            remove_group(chat.id)
        except Exception as e:
            print(f"DB Error (remove_group): {e}")
        
        # 🔥 STEP 2: Send Log
        logger_id = get_logger_group()
        if logger_id:
            msg = f"""
<blockquote>🔴 <b>{to_fancy('BOT REMOVED / LEFT')}</b></blockquote>

<blockquote>
<b>📍 ɢʀᴏᴜᴘ :</b> {html.escape(chat.title)}
<b>🆔 ɪᴅ :</b> <code>{chat.id}</code>
<b>👮 ᴀᴄᴛɪᴏɴ ʙʏ :</b> {html.escape(action_by.first_name) if action_by else 'System'}
</blockquote>
"""
            kb = [[InlineKeyboardButton("❌ Close", callback_data="close_log")]]
            try:
                await context.bot.send_message(
                    chat_id=logger_id, 
                    text=msg, 
                    reply_markup=InlineKeyboardMarkup(kb), 
                    parse_mode=ParseMode.HTML
                )
            except:
                pass
        return 

# --- 3. VOICE CHAT HANDLER ---
async def vc_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    msg = update.message
    
    # A. VC STARTED
    if msg.video_chat_started:
        text = f"<blockquote><b>🎙️ {to_fancy('VOICE CHAT STARTED')}</b></blockquote>\n<blockquote>Join now and hang out! 🔥</blockquote>"
        sent = await chat.send_message(text, parse_mode=ParseMode.HTML)
        context.job_queue.run_once(delete_msg, 8, chat_id=chat.id, data=sent.message_id)

    # B. VC ENDED
    elif msg.video_chat_ended:
        text = f"<blockquote><b>🔇 {to_fancy('VOICE CHAT ENDED')}</b></blockquote>\n<blockquote>See you next time! 👋</blockquote>"
        sent = await chat.send_message(text, parse_mode=ParseMode.HTML)
        context.job_queue.run_once(delete_msg, 8, chat_id=chat.id, data=sent.message_id)
        
    # C. USER INVITED / JOINED
    elif msg.video_chat_participants_invited:
        for user in msg.video_chat_participants_invited.users:
            text = f"<blockquote><b>🎧 {to_fancy('USER JOINED VC')}</b></blockquote>\n<blockquote>👤 <b>{html.escape(user.first_name)}</b> is in the chat!</blockquote>"
            sent = await chat.send_message(text, parse_mode=ParseMode.HTML)
            context.job_queue.run_once(delete_msg, 8, chat_id=chat.id, data=sent.message_id)
