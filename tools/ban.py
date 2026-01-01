import datetime
from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes, CommandHandler
from telegram.constants import ChatMemberStatus, ParseMode
from telegram.error import TelegramError, BadRequest

# --- HELPER: CHECK ADMIN & GET TARGET ---
async def check_admin_get_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    args = context.args

    # 1. Requester Admin Check
    member = await chat.get_member(user.id)
    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        await update.message.reply_text("❌ **ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ!**")
        return None, None

    # 2. Bot Admin Check
    bot_member = await chat.get_member(context.bot.id)
    if not bot_member.can_restrict_members:
        await update.message.reply_text("❌ **ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ 'ʙᴀɴ/ᴍᴜᴛᴇ' ᴘᴇʀᴍɪssɪᴏɴs!**")
        return None, None

    # 3. Get Target Logic (IMPROVED 🛠️)
    target_user = None

    # Case A: Reply
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    
    # Case B: Arguments (ID or Username)
    elif args:
        raw_arg = args[0]
        
        # Agar Mention (Message Entity) hai
        if update.message.entities:
            for entity in update.message.entities:
                if entity.type == "text_mention":
                    target_user = entity.user
                    break
        
        # Agar abhi bhi nahi mila, toh ID check karo
        if not target_user:
            # Agar sirf numbers hain (UserID)
            if raw_arg.isdigit():
                try:
                    target_member = await chat.get_member(int(raw_arg))
                    target_user = target_member.user
                except:
                    pass
            # Agar @Username hai (Bot shayad na dhoond paye)
            elif raw_arg.startswith("@"):
                 await update.message.reply_text("⚠️ **@ᴜsᴇʀɴᴀᴍᴇ ɪssᴜᴇ:**\nᴘʟᴇᴀsᴇ **ʀᴇᴘʟʏ** ᴛᴏ ᴛʜᴇ ᴜsᴇʀ ᴏʀ ᴜsᴇ **ᴜsᴇʀ ɪᴅ**.\n(Telegram API limits searching by username).")
                 return None, None

    if not target_user:
        await update.message.reply_text("❌ **ᴜsᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ!**\nᴘʟᴇᴀsᴇ **ʀᴇᴘʟʏ** ᴛᴏ ᴛʜᴇ ᴜsᴇʀ's ᴍᴇssᴀɢᴇ.")
        return None, None

    # 4. Check if Target is Admin
    try:
        target_member = await chat.get_member(target_user.id)
        if target_member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            await update.message.reply_text("❌ **ɪ ᴄᴀɴ'ᴛ ʙᴀɴ/ᴍᴜᴛᴇ ᴀɴ ᴀᴅᴍɪɴ!**")
            return None, None
    except:
        pass # User shayad group mein nahi hai, fir bhi ban try karenge

    return chat, target_user

# --- HELPER: FORMAT MESSAGE ---
def format_action(action, user, admin, reason=None, time=None):
    text = (
        f"» {action} ɪɴ {datetime.datetime.now().strftime('%H:%M')}\n\n"
        f"👤 ᴜsᴇʀ : {user.mention_html()}\n"
        f"👮 ᴀᴅᴍɪɴ : {admin.mention_html()}"
    )
    if time: text += f"\n⏳ ᴅᴜʀᴀᴛɪᴏɴ : `{time}`"
    if reason: text += f"\n📝 ʀᴇᴀsᴏɴ : `{reason}`"
    return text

# --- 1. BAN COMMAND ---
async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat, target = await check_admin_get_user(update, context)
    if not chat or not target: return

    reason = " ".join(context.args[1:]) if len(context.args) > 1 else None

    try:
        await chat.ban_member(target.id)
        msg = format_action("ʙᴀɴɴᴇᴅ", target, update.effective_user, reason)
        await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {e}")

# --- 2. UNBAN COMMAND ---
async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat, target = await check_admin_get_user(update, context)
    if not chat or not target: return

    try:
        await chat.unban_member(target.id)
        msg = format_action("ᴜɴʙᴀɴɴᴇᴅ", target, update.effective_user)
        await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {e}")

# --- 3. MUTE COMMAND ---
async def mute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat, target = await check_admin_get_user(update, context)
    if not chat or not target: return

    try:
        await chat.restrict_member(target.id, permissions=ChatPermissions(can_send_messages=False))
        msg = format_action("ᴍᴜᴛᴇᴅ", target, update.effective_user)
        await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {e}")

# --- 4. UNMUTE COMMAND ---
async def unmute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat, target = await check_admin_get_user(update, context)
    if not chat or not target: return

    try:
        # Full Permissions wapis dena
        await chat.restrict_member(
            target.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_invite_users=True
            )
        )
        msg = format_action("ᴜɴᴍᴜᴛᴇᴅ", target, update.effective_user)
        await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {e}")

# --- REGISTER HANDLERS ---
def register_handlers(app):
    app.add_handler(CommandHandler(["ban", "fuck"], ban_user))
    app.add_handler(CommandHandler(["unban"], unban_user))
    app.add_handler(CommandHandler(["mute", "shush"], mute_user))
    app.add_handler(CommandHandler(["unmute"], unmute_user))
    print("  ✅ Admin Tools (Ban/Mute) Loaded!")
    
