from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from telegram.constants import ChatMemberStatus, ParseMode
from telegram.error import TelegramError

# --- HELPER: USER & ADMIN CHECK ---
async def extract_user_and_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    
    # 1. User Admin Check
    member = await chat.get_member(user.id)
    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        await update.message.reply_text("❌ **ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ!**")
        return None, None, None

    # 2. Bot Admin Check
    bot_member = await chat.get_member(context.bot.id)
    if not bot_member.can_promote_members:
        await update.message.reply_text("❌ **ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ 'ᴀᴅᴅ ᴀᴅᴍɪɴs' ᴘᴏᴡᴇʀ!**")
        return None, None, None

    # 3. Target User & Title Extraction
    target_user = None
    title = None
    args = context.args

    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        if args: title = " ".join(args)
    elif args:
        try:
            target_id = args[0]
            try:
                target_member = await chat.get_member(target_id)
                target_user = target_member.user
            except:
                await update.message.reply_text("❌ **ᴜsᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ!**")
                return None, None, None
            
            if len(args) > 1: title = " ".join(args[1:])
        except:
            await update.message.reply_text("❌ **ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ ɪᴅ.**")
            return None, None, None
    else:
        await update.message.reply_text("⚠️ **ᴜsᴀɢᴇ:** ʀᴇᴘʟʏ ᴏʀ ᴛʏᴘᴇ `/promote [Title]`.")
        return None, None, None

    return chat, target_user, title

# --- HELPER: FORMAT MESSAGE ---
def format_msg(chat_name, action, user, admin):
    return (
        f"» {action} ᴀ ᴜsᴇʀ ɪɴ {chat_name}\n"
        f"👤 ᴜsᴇʀ : {user.mention_html()}\n"
        f"👮 ᴀᴅᴍɪɴ : {admin.mention_html()}"
    )

# --- 1. PROMOTE COMMAND (Basic Admin) ---
async def promote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat, target, title = await extract_user_and_check(update, context)
    if not chat: return

    try:
        # Check if already admin
        member = await chat.get_member(target.id)
        if member.status == ChatMemberStatus.ADMINISTRATOR:
            return await update.message.reply_text("⚠️ **ᴛʜɪs ᴜsᴇʀ ɪs ᴀʟʀᴇᴀᴅʏ ᴀɴ ᴀᴅᴍɪɴ.**")

        await chat.promote_member(
            user_id=target.id,
            can_manage_chat=True,
            can_delete_messages=True,
            can_manage_video_chats=True,
            can_invite_users=True,
            can_pin_messages=True,
            can_restrict_members=False, # Basic (No Ban Power)
            can_promote_members=False,  # No Promote Power
            can_change_info=False
        )

        # Set Title
        if title:
            try: await chat.set_administrator_custom_title(target.id, title)
            except: pass 

        msg = format_msg(chat.title, "ᴘʀᴏᴍᴏᴛɪɴɢ", target, update.effective_user)
        await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

    except TelegramError as e:
        await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {e}")

# --- 2. FULL PROMOTE COMMAND (God Mode) ---
async def fullpromote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat, target, title = await extract_user_and_check(update, context)
    if not chat: return

    try:
        member = await chat.get_member(target.id)
        if member.status == ChatMemberStatus.ADMINISTRATOR:
            return await update.message.reply_text("⚠️ **ᴛʜɪs ᴜsᴇʀ ɪs ᴀʟʀᴇᴀᴅʏ ᴀɴ ᴀᴅᴍɪɴ.**")

        await chat.promote_member(
            user_id=target.id,
            can_manage_chat=True,
            can_delete_messages=True,
            can_manage_video_chats=True,
            can_invite_users=True,
            can_pin_messages=True,
            can_restrict_members=True,
            can_promote_members=True,  # 🔥 FULL POWER
            can_change_info=True
        )

        if title:
            try: await chat.set_administrator_custom_title(target.id, title)
            except: pass

        msg = format_msg(chat.title, "ꜰᴜʟʟ ᴘʀᴏᴍᴏᴛɪɴɢ", target, update.effective_user)
        await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

    except TelegramError as e:
        await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {e}")

# --- 3. DEMOTE COMMAND ---
async def demote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat, target, title = await extract_user_and_check(update, context)
    if not chat: return

    try:
        member = await chat.get_member(target.id)
        if member.status != ChatMemberStatus.ADMINISTRATOR:
            return await update.message.reply_text("⚠️ **ᴛʜɪs ᴜsᴇʀ ɪs ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ.**")

        # Strip all powers
        await chat.promote_member(
            user_id=target.id,
            can_manage_chat=False,
            can_delete_messages=False,
            can_manage_video_chats=False,
            can_invite_users=False,
            can_pin_messages=False,
            can_restrict_members=False,
            can_promote_members=False,
            can_change_info=False
        )

        msg = format_msg(chat.title, "ᴅᴇᴍᴏᴛɪɴɢ", target, update.effective_user)
        await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

    except TelegramError as e:
        await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {e}")

# --- HANDLER REGISTRATION ---
def register_handlers(app):
    app.add_handler(CommandHandler(["promote", "admin"], promote))
    app.add_handler(CommandHandler(["fullpromote", "fpromote"], fullpromote))
    app.add_handler(CommandHandler(["demote", "unadmin"], demote))
    print("  ✅ Admin Tools (Promote) Loaded!")
