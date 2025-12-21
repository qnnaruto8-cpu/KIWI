import html
from telegram import Update, ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode, ChatMemberStatus
from telegram.ext import ContextTypes
from database import add_warning, remove_warning, reset_warnings
from config import OWNER_ID

# Fancy Font Helper
def to_fancy(text):
    mapping = {'A': 'Λ', 'E': 'Є', 'S': 'δ', 'O': 'σ', 'T': 'ᴛ', 'N': 'ɴ', 'M': 'ᴍ', 'U': 'ᴜ', 'R': 'ʀ', 'D': 'ᴅ', 'C': 'ᴄ', 'P': 'ᴘ', 'G': 'ɢ', 'B': 'ʙ', 'L': 'ʟ', 'W': 'ᴡ', 'K': 'ᴋ', 'J': 'ᴊ', 'Y': 'ʏ', 'I': 'ɪ', 'H': 'ʜ'}
    return "".join(mapping.get(c.upper(), c) for c in text)

# --- HELPER: CHECK USER ADMIN ---
async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Checks if the command user is an Admin"""
    user = update.effective_user
    chat = update.effective_chat
    
    # 1. Owner Check
    try:
        if str(user.id) == str(OWNER_ID): 
            return True
    except: pass

    # 2. Private Chat Check
    if chat.type == "private":
        await update.message.reply_text("❌ This command works only in Groups.")
        return False

    # 3. Group Admin Check
    try:
        member = await chat.get_member(user.id)
        if member.status in ['administrator', 'creator']:
            return True
    except Exception as e:
        print(f"DEBUG: Admin check error: {e}")
    
    # If not Admin
    msg_text = f"<blockquote><b>❌ {to_fancy('ACCESS DENIED')}</b></blockquote>\n<blockquote>Only Admins can use this command.</blockquote>"
    await update.message.reply_text(msg_text, parse_mode=ParseMode.HTML)
    return False

# --- COMMANDS ---

# 🔥 NEW: GET ID COMMAND 🔥
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: await update.message.delete()
    except: pass

    chat = update.effective_chat
    msg = update.message
    reply = msg.reply_to_message
    
    text = f"<blockquote><b>🆔 {to_fancy('ID LOOKUP')}</b></blockquote>\n\n"
    
    # Scenario 1: Reply to a message
    if reply:
        user_id = reply.from_user.id
        text += f"<blockquote><b>👤 ᴜsᴇʀ ɪᴅ :</b> <code>{user_id}</code>\n"
        
        if reply.forward_from:
            text += f"<b>⏩ ғᴡᴅ ᴜsᴇʀ ɪᴅ :</b> <code>{reply.forward_from.id}</code>\n"
        
        if reply.forward_from_chat:
            text += f"<b>📢 ғᴡᴅ ᴄʜᴀᴛ ɪᴅ :</b> <code>{reply.forward_from_chat.id}</code>\n"
            
        if reply.forward_sender_name and not reply.forward_from and not reply.forward_from_chat:
             text += f"<b>⏩ ғᴡᴅ sᴇɴᴅᴇʀ :</b> {html.escape(reply.forward_sender_name)} (ID Hidden)\n"
             
        text += "</blockquote>\n"

    # Scenario 2: Direct Command
    else:
        user_id = update.effective_user.id
        text += f"<blockquote><b>👤 ʏᴏᴜʀ ɪᴅ :</b> <code>{user_id}</code></blockquote>\n"

    text += f"<blockquote><b>👥 ɢʀᴏᴜᴘ ɪᴅ :</b> <code>{chat.id}</code></blockquote>"
    
    await context.bot.send_message(chat.id, text, parse_mode=ParseMode.HTML)

async def warn_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: await update.message.delete()
    except: pass

    if not await is_admin(update, context): return

    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a user with <code>.warn</code>", parse_mode=ParseMode.HTML)

    target = update.message.reply_to_message.from_user
    chat = update.effective_chat
    
    if str(target.id) == str(OWNER_ID) or target.is_bot:
        return await update.message.reply_text("❌ You cannot warn the Owner or a Bot!")

    count = add_warning(chat.id, target.id)
    
    if count >= 3:
        try:
            await chat.ban_member(target.id)
            reset_warnings(chat.id, target.id)
            msg = f"<blockquote><b>🚫 {to_fancy('BANNED')}</b></blockquote>\n<blockquote><b>👤 ᴜsᴇʀ :</b> {html.escape(target.first_name)}\n<b>⚠️ ʀᴇᴀsᴏɴ :</b> 3 Warnings Reached</blockquote>"
            await chat.send_message(msg, parse_mode=ParseMode.HTML)
        except Exception as e:
            await chat.send_message(f"❌ Error: `{e}`")
    else:
        msg = f"<blockquote><b>⚠️ {to_fancy('WARNING ISSUED')}</b></blockquote>\n<blockquote><b>👤 ᴜsᴇʀ :</b> {html.escape(target.first_name)}\n<b>🔢 ᴄᴏᴜɴᴛ :</b> {count}/3</blockquote>"
        await chat.send_message(msg, parse_mode=ParseMode.HTML)

async def unwarn_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: await update.message.delete()
    except: pass
    
    if not await is_admin(update, context): return
    if not update.message.reply_to_message: return await update.message.reply_text("⚠️ Reply to a user to use this command.")

    target = update.message.reply_to_message.from_user
    chat = update.effective_chat
    
    count = remove_warning(chat.id, target.id)
    msg = f"<blockquote><b>✅ {to_fancy('UNWARNED')}</b></blockquote>\n<blockquote><b>👤 ᴜsᴇʀ :</b> {html.escape(target.first_name)}\n<b>🔢 ʟᴇғᴛ :</b> {count}</blockquote>"
    await chat.send_message(msg, parse_mode=ParseMode.HTML)

async def mute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: await update.message.delete()
    except: pass
    
    if not await is_admin(update, context): return
    if not update.message.reply_to_message: return await update.message.reply_text("⚠️ Reply to a user to use this command.")

    target = update.message.reply_to_message.from_user
    chat = update.effective_chat
    
    try:
        await chat.restrict_member(target.id, permissions=ChatPermissions(can_send_messages=False))
        msg = f"<blockquote><b>🔇 {to_fancy('MUTED')}</b></blockquote>\n<blockquote><b>👤 ᴜsᴇʀ :</b> {html.escape(target.first_name)}\n<b>🚫 sᴛᴀᴛᴜs :</b> Cannot send messages</blockquote>"
        await chat.send_message(msg, parse_mode=ParseMode.HTML)
    except Exception as e:
        await chat.send_message(f"❌ Error: {e}")

async def unmute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: await update.message.delete()
    except: pass
    
    if not await is_admin(update, context): return
    if not update.message.reply_to_message: return await update.message.reply_text("⚠️ Reply to a user to use this command.")

    target = update.message.reply_to_message.from_user
    chat = update.effective_chat
    
    try:
        await chat.restrict_member(
            target.id, 
            permissions=ChatPermissions(
                can_send_messages=True, can_send_media_messages=True,
                can_send_other_messages=True, can_send_polls=True
            )
        )
        msg = f"<blockquote><b>🔊 {to_fancy('UNMUTED')}</b></blockquote>\n<blockquote><b>👤 ᴜsᴇʀ :</b> {html.escape(target.first_name)}\n<b>✅ sᴛᴀᴛᴜs :</b> Can speak now</blockquote>"
        await chat.send_message(msg, parse_mode=ParseMode.HTML)
    except Exception as e:
        await chat.send_message(f"❌ Error: {e}")

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: await update.message.delete()
    except: pass
    
    if not await is_admin(update, context): return
    if not update.message.reply_to_message: return await update.message.reply_text("⚠️ Reply to a user to use this command.")

    target = update.message.reply_to_message.from_user
    try:
        await update.effective_chat.ban_member(target.id)
        msg = f"<blockquote><b>🚫 {to_fancy('BANNED')}</b></blockquote>\n<blockquote><b>👤 ᴜsᴇʀ :</b> {html.escape(target.first_name)}\n<b>👢 ᴀᴄᴛɪᴏɴ :</b> Removed from group</blockquote>"
        await update.effective_chat.send_message(msg, parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.effective_chat.send_message(f"❌ Error: `{e}`")

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: await update.message.delete()
    except: pass
    
    if not await is_admin(update, context): return
    if not update.message.reply_to_message: return await update.message.reply_text("⚠️ Reply to a user to use this command.")

    target = update.message.reply_to_message.from_user
    try:
        await update.effective_chat.unban_member(target.id)
        msg = f"<blockquote><b>✅ {to_fancy('UNBANNED')}</b></blockquote>\n<blockquote><b>👤 ᴜsᴇʀ :</b> {html.escape(target.first_name)}\n<b>🚪 sᴛᴀᴛᴜs :</b> Can join again</blockquote>"
        await update.effective_chat.send_message(msg, parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.effective_chat.send_message(f"❌ Error: {e}")

async def kick_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: await update.message.delete()
    except: pass
    
    if not await is_admin(update, context): return
    if not update.message.reply_to_message: return await update.message.reply_text("⚠️ Reply to a user to use this command.")

    target = update.message.reply_to_message.from_user
    try:
        await update.effective_chat.ban_member(target.id)
        await update.effective_chat.unban_member(target.id)
        msg = f"<blockquote><b>🦵 {to_fancy('KICKED')}</b></blockquote>\n<blockquote><b>👤 ᴜsᴇʀ :</b> {html.escape(target.first_name)}</blockquote>"
        await update.effective_chat.send_message(msg, parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.effective_chat.send_message(f"❌ Error: {e}")

async def promote_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: await update.message.delete()
    except: pass
    
    if not await is_admin(update, context): return
    if not update.message.reply_to_message: return await update.message.reply_text("⚠️ Reply to a user to use this command.")

    target = update.message.reply_to_message.from_user
    
    can_change_info = False; can_delete = True; can_invite = True; can_pin = False
    
    if context.args:
        level = context.args[0]
        if level == "2": can_pin = True; can_change_info = True
        elif level == "3": can_pin = True; can_change_info = True
            
    try:
        await update.effective_chat.promote_member(
            user_id=target.id, can_delete_messages=can_delete, can_invite_users=can_invite,
            can_pin_messages=can_pin, can_change_info=can_change_info, is_anonymous=False
        )
        msg = f"<blockquote><b>👮‍♂️ {to_fancy('PROMOTED')}</b></blockquote>\n<blockquote><b>👤 ᴜsᴇʀ :</b> {html.escape(target.first_name)}\n<b>🛡️ ʀᴏʟᴇ :</b> Admin</blockquote>"
        await update.effective_chat.send_message(msg, parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.effective_chat.send_message(f"❌ Error: {e}")

async def demote_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: await update.message.delete()
    except: pass
    
    if not await is_admin(update, context): return
    if not update.message.reply_to_message: return await update.message.reply_text("⚠️ Reply to a user to use this command.")

    target = update.message.reply_to_message.from_user
    try:
        await update.effective_chat.promote_member(
            user_id=target.id, can_delete_messages=False, can_invite_users=False,
            can_pin_messages=False, can_change_info=False, is_anonymous=False
        )
        msg = f"<blockquote><b>⬇️ {to_fancy('DEMOTED')}</b></blockquote>\n<blockquote><b>👤 ᴜsᴇʀ :</b> {html.escape(target.first_name)}\n<b>⛔ ʀᴏʟᴇ :</b> Member</blockquote>"
        await update.effective_chat.send_message(msg, parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.effective_chat.send_message(f"❌ Error: {e}")

async def set_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: await update.message.delete()
    except: pass
    
    if not await is_admin(update, context): return
    if not update.message.reply_to_message: return await update.message.reply_text("⚠️ Reply to a user to use this command.")

    if not context.args: return
    title = " ".join(context.args)
    target = update.message.reply_to_message.from_user
    
    try:
        await update.effective_chat.set_administrator_custom_title(target.id, title)
        msg = f"<blockquote><b>🏷 {to_fancy('TITLE SET')}</b></blockquote>\n<blockquote><b>👤 ᴜsᴇʀ :</b> {html.escape(target.first_name)}\n<b>🔖 ᴛɪᴛʟᴇ :</b> {html.escape(title)}</blockquote>"
        await update.effective_chat.send_message(msg, parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.effective_chat.send_message(f"❌ Error: {e}")

async def pin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: await update.message.delete()
    except: pass
    
    if not await is_admin(update, context): return
    if not update.message.reply_to_message: return await update.message.reply_text("⚠️ Reply to a message to use this command.")

    try:
        await update.message.reply_to_message.pin()
    except Exception as e:
        await update.effective_chat.send_message(f"❌ Error: {e}")

async def delete_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: await update.message.delete()
    except: pass
    
    if not await is_admin(update, context): return

    if update.message.reply_to_message:
        try:
            await update.message.reply_to_message.delete()
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")

async def admin_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: await update.message.delete()
    except: pass
    
    text = f"""
<blockquote><b>🛡️ {to_fancy('ADMIN COMMANDS')}</b></blockquote>
<blockquote>
<b>🔸 <code>.id</code></b> : Get User/Group IDs
<b>🔸 <code>.warn</code></b> : Warn user (3 = Ban)
<b>🔸 <code>.unwarn</code></b> : Remove warning
<b>🔸 <code>.mute</code></b> : Mute user
<b>🔸 <code>.unmute</code></b> : Unmute user
<b>🔸 <code>.ban</code></b> : Ban user
<b>🔸 <code>.unban</code></b> : Unban user
<b>🔸 <code>.kick</code></b> : Kick user
<b>🔸 <code>.promote</code></b> : Promote
<b>🔸 <code>.demote</code></b> : Demote
<b>🔸 <code>.title</code></b> : Set Admin Title
<b>🔸 <code>.pin</code></b> : Pin message
<b>🔸 <code>.d</code></b> : Delete message
</blockquote>
"""
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)
