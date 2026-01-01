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
    
    # Sirf Group mein
    if chat.type == "private":
        return await update.message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ᴏɴʟʏ ꜰᴏʀ ɢʀᴏᴜᴘs.")

    # Only Admin Check
    member = await chat.get_member(user.id)
    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        return await update.message.reply_text("❌ **ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴄʜᴀɴɢᴇ ᴛʜɪs sᴇᴛᴛɪɴɢ!**")

    if not context.args:
        return await update.message.reply_text("⚠️ ᴜsᴀɢᴇ: `/admincmd on` ᴏʀ `/admincmd off`")

    state = context.args[0].lower()
    
    if state == "on":
        await set_admincmd_mode(chat.id, True)
        await update.message.reply_text("✅ **ᴀᴅᴍɪɴ ʟɪsᴛ ᴄᴏᴍᴍᴀɴᴅ ᴇɴᴀʙʟᴇᴅ!**\nNow everyone can use `/admin`.")
    elif state == "off":
        await set_admincmd_mode(chat.id, False)
        await update.message.reply_text("🔒 **ᴀᴅᴍɪɴ ʟɪsᴛ ᴄᴏᴍᴍᴀɴᴅ ᴅɪsᴀʙʟᴇᴅ!**\n`/admin` will not work now.")
    else:
        await update.message.reply_text("⚠️ ᴜsᴀɢᴇ: `/admincmd on` ᴏʀ `/admincmd off`")

# --- MAIN COMMAND: SHOW LIST ---
async def show_admin_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    
    if chat.type == "private": return

    # 🔥 STEP 1: CHECK IF ENABLED
    is_enabled = await is_admincmd_enabled(chat.id)
    if not is_enabled:
        # Agar OFF hai, to chup-chap return ho jao (Reply mat karo)
        return

    # List fetch logic...
    try:
        administrators = await chat.get_administrators()
    except Exception as e:
        return await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {e}")

    owner = None
    admin_list = []
    
    for admin in administrators:
        user = admin.user
        styled_name = to_small_caps(user.first_name)
        mention = f'<a href="tg://user?id={user.id}">{styled_name}</a>'
        
        title = ""
        if admin.custom_title:
            title = f"[{to_small_caps(admin.custom_title)}]"

        if admin.status == ChatMemberStatus.OWNER:
            owner = f"{mention} {title}"
        else:
            if user.is_bot:
                admin_list.append(f"{mention} 🤖")
            else:
                admin_list.append(f"{mention} {title}")

    # Build Message
    text = "<blockquote>"
    if owner:
        text += f"👑 <b>ᴏᴡɴᴇʀ :</b>\n└ {owner}\n\n"
    
    if admin_list:
        text += f"👮 <b>ᴀᴅᴍɪɴs :</b>\n"
        for ad in admin_list:
            text += f"└ {ad}\n"
    text += "</blockquote>"

    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

# --- REGISTER HANDLER ---
def register_handlers(app):
    # ON/OFF Command
    app.add_handler(CommandHandler(["admincmd", "adminmode"], toggle_admincmd))
    
    # Admin List Command
    app.add_handler(MessageHandler(filters.Regex(r"^[./]admin$"), show_admin_list))
    
    print("  ✅ Admin List Tool Loaded!")
              
