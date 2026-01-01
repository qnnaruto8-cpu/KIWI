import datetime
from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes, CommandHandler
from telegram.constants import ChatMemberStatus, ParseMode
from telegram.error import TelegramError

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

    # 3. Get Target
    target_user = None
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    elif args:
        try:
            target_id = args[0]
            # Try to fetch member via ID
            target_member = await chat.get_member(target_id)
            target_user = target_member.user
        except:
            await update.message.reply_text("❌ **ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ ɪᴅ ᴏʀ ᴜsᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ!**")
            return None, None
    else:
        await update.message.reply_text("⚠️ **ᴜsᴀɢᴇ:** ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ ᴛʏᴘᴇ `/ban [UserID]`")
        return None, None

    # 4. Check if Target is Admin (Protection)
    if target_user:
        target_member = await chat.get_member(target_user.id)
        if target_member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            await update.message.reply_text("❌ **ɪ ᴄᴀɴ'ᴛ ʙᴀɴ/ᴍᴜᴛᴇ ᴀɴ ᴀᴅᴍɪɴ!**")
            return None, None

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

# --- 3. MUTE COMMAND (Forever) ---
async def mute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat, target = await check_admin_get_user(update, context)
    if not chat or not target: return

    try:
        # Permissions: Can't send anything
        await chat.restrict_member(
            target.id,
            permissions=ChatPermissions(can_send_messages=False)
        )
        msg = format_action("ᴍᴜᴛᴇᴅ", target, update.effective_user)
        await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {e}")

# --- 4. UNMUTE COMMAND ---
async def unmute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat, target = await check_admin_get_user(update, context)
    if not chat or not target: return

    try:
        # Permissions: Allow everything (Standard Member)
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

# --- 5. TMUTE COMMAND (Timed Mute) ---
async def tmute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    args = context.args

    # Admin check repeated here slightly differently because of args parsing
    member = await chat.get_member(user.id)
    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        return await update.message.reply_text("❌ **ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ!**")

    if not args and not update.message.reply_to_message:
         return await update.message.reply_text("⚠️ **ᴜsᴀɢᴇ:** Reply with `/tmute 10m` or `/tmute [ID] 2h`")

    # Get Target
    target = None
    time_str = None

    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user
        if args: time_str = args[0]
    elif len(args) >= 2:
        try:
            target = (await chat.get_member(args[0])).user
            time_str = args[1]
        except: return await update.message.reply_text("❌ **ᴜsᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ!**")
    
    if not target or not time_str:
        return await update.message.reply_text("❌ **ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴛɪᴍᴇ!** (e.g. 10m, 2h)")

    # Parse Time
    unit = time_str[-1].lower()
    value = time_str[:-1]
    if not value.isdigit():
        return await update.message.reply_text("❌ **ɪɴᴠᴀʟɪᴅ ᴛɪᴍᴇ ꜰᴏʀᴍᴀᴛ!** Use `10m`, `2h`, `1d`.")
    
    value = int(value)
    delta = None
    
    if unit == 'm': delta = datetime.timedelta(minutes=value)
    elif unit == 'h': delta = datetime.timedelta(hours=value)
    elif unit == 'd': delta = datetime.timedelta(days=value)
    else: return await update.message.reply_text("❌ **ᴜsᴇ ᴍ/ʜ/ᴅ ᴏɴʟʏ!**")

    try:
        until = datetime.datetime.now() + delta
        await chat.restrict_member(
            target.id,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=until
        )
        msg = format_action("ᴛᴇᴍᴘ-ᴍᴜᴛᴇᴅ", target, update.effective_user, time=time_str)
        await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {e}")

# --- REGISTER HANDLERS ---
def register_handlers(app):
    app.add_handler(CommandHandler(["ban", "fuck"], ban_user))
    app.add_handler(CommandHandler(["unban"], unban_user))
    app.add_handler(CommandHandler(["mute", "shush"], mute_user))
    app.add_handler(CommandHandler(["unmute"], unmute_user))
    app.add_handler(CommandHandler(["tmute"], tmute_user))
    print("  ✅ Admin Tools (Ban/Mute) Loaded!")
      
