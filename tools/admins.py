import re
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, CommandHandler, filters
from telegram.constants import ChatMemberStatus, ParseMode

# Database Functions
from tools.database import set_admincmd_mode, is_admincmd_enabled

# --- SMALL CAPS MAPPER ---
def to_small_caps(text):
    mapping = {
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ꜰ', 'g': 'ɢ', 'h': 'ʜ', 'i': 'ɪ',
        'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ',
        's': 's', 't': 'ᴛ', 'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ',
        'A': 'ᴀ', 'B': 'ʙ', 'C': 'ᴄ', 'D': 'ᴅ', 'E': 'ᴇ', 'F': 'ꜰ', 'G': 'ɢ', 'H': 'ʜ', 'I': 'ɪ',
        'J': 'ᴊ', 'K': 'ᴋ', 'L': 'ʟ', 'M': 'ᴍ', 'N': 'ɴ', 'O': 'ᴏ', 'P': 'ᴘ', 'Q': 'ǫ', 'R': 'ʀ',
        'S': 's', 'T': 'ᴛ', 'U': 'ᴜ', 'V': 'ᴠ', 'W': 'ᴡ', 'X': 'x', 'Y': 'ʏ', 'Z': 'ᴢ'
    }
    return "".join(mapping.get(c, c) for c in text)

# --- TOGGLE COMMAND: ON/OFF SYSTEM ---
async def toggle_admincmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    
    if chat.type == "private":
        return await update.message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ᴏɴʟʏ ꜰᴏʀ ɢʀᴏᴜᴘs.")

    member = await chat.get_member(user.id)
    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        return await update.message.reply_text("❌ **ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴄʜᴀɴɢᴇ ᴛʜɪs sᴇᴛᴛɪɴɢ!**")

    if not context.args:
        return await update.message.reply_text("⚠️ ᴜsᴀɢᴇ: `/admincmd on` ᴏʀ `/admincmd off`")

    state = context.args[0].lower()
    
    if state == "on":
        await set_admincmd_mode(chat.id, True)
        await update.message.reply_text("✅ **ᴀᴅᴍɪɴ ʟɪsᴛ ᴄᴏᴍᴍᴀɴᴅ ᴇɴᴀʙʟᴇᴅ!**")
    elif state == "off":
        await set_admincmd_mode(chat.id, False)
        await update.message.reply_text("🔒 **ᴀᴅᴍɪɴ ʟɪsᴛ ᴄᴏᴍᴍᴀɴᴅ ᴅɪsᴀʙʟᴇᴅ!**")
    else:
        await update.message.reply_text("⚠️ ᴜsᴀɢᴇ: `/admincmd on` ᴏʀ `/admincmd off`")

# --- 1. ADMIN LIST COMMAND (HUMANS ONLY) ---
async def show_admin_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type == "private": return

    # Check ON/OFF
    is_enabled = await is_admincmd_enabled(chat.id)
    if not is_enabled: return

    try: administrators = await chat.get_administrators()
    except: return

    owner = None
    admin_list = []
    
    for admin in administrators:
        user = admin.user
        
        # 🔥 Filter: Agar Bot hai to SKIP karo
        if user.is_bot:
            continue

        styled_name = to_small_caps(user.first_name)
        mention = f'<a href="tg://user?id={user.id}">{styled_name}</a>'
        
        title = ""
        if admin.custom_title:
            title = f"[{to_small_caps(admin.custom_title)}]"

        if admin.status == ChatMemberStatus.OWNER:
            owner = f"{mention} {title}"
        else:
            admin_list.append(f"{mention} {title}")

    # Message Build
    text = "<blockquote>"
    if owner:
        text += f"👑 <b>ᴏᴡɴᴇʀ :</b>\n└ {owner}\n\n"
    
    if admin_list:
        text += f"👮 <b>ᴀᴅᴍɪɴs :</b>\n"
        for ad in admin_list:
            text += f"└ {ad}\n"
    else:
        if not owner: text += "❌ ɴᴏ ʜᴜᴍᴀɴ ᴀᴅᴍɪɴs ꜰᴏᴜɴᴅ."
        
    text += "</blockquote>"

    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

# --- 2. BOTS LIST COMMAND (ADMIN BOTS ONLY) ---
async def show_bot_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type == "private": return

    try: administrators = await chat.get_administrators()
    except: return

    bot_list = []
    
    for admin in administrators:
        user = admin.user
        
        # 🔥 Filter: Sirf Bots ko select karo
        if not user.is_bot:
            continue

        styled_name = to_small_caps(user.first_name)
        mention = f'<a href="tg://user?id={user.id}">{styled_name}</a>'
        bot_list.append(f"🤖 {mention}")

    text = "<blockquote>"
    if bot_list:
        text += f"🤖 <b>ʙᴏᴛ ʟɪsᴛ :</b>\n"
        for b in bot_list:
            text += f"└ {b}\n"
    else:
        # Note for user why list is empty
        text += "❌ ɴᴏ ᴀᴅᴍɪɴ ʙᴏᴛs ꜰᴏᴜɴᴅ.\n(Only Admin bots are visible)"
    text += "</blockquote>"

    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

# --- REGISTER HANDLERS ---
def register_handlers(app):
    # ON/OFF
    app.add_handler(CommandHandler(["admincmd", "adminmode"], toggle_admincmd))
    
    # ✅ FIX 1: Admin List (Regex updated for 'admin' AND 'admins')
    # (?i) ka matlab case insensitive (Admin, ADMIN, admin sab chalega)
    app.add_handler(MessageHandler(filters.Regex(r"(?i)^[./]admins?$"), show_admin_list))
    
    # ✅ FIX 2: Bot List (Regex updated for 'bot' AND 'bots')
    app.add_handler(MessageHandler(filters.Regex(r"(?i)^[./]bots?$"), show_bot_list))
    
    print("  ✅ Admin & Bot List Tools Loaded!")
    
