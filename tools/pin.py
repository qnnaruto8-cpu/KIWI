from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from telegram.constants import ChatMemberStatus, ParseMode
from telegram.error import BadRequest

# --- HELPER: ADMIN CHECK ---
async def check_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    # Admin Permission Check
    member = await chat.get_member(user.id)
    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        await update.message.reply_text("❌ **ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ!**")
        return False

    # Bot Permission Check
    bot_member = await chat.get_member(context.bot.id)
    if not bot_member.can_pin_messages:
        await update.message.reply_text("❌ **ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ 'ᴘɪɴ ᴍᴇssᴀɢᴇs' ᴘᴇʀᴍɪssɪᴏɴ!**")
        return False
        
    return True

# --- 1. PIN COMMAND ---
async def pin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_admin(update, context): return

    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ **ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ᴘɪɴ ɪᴛ.**")

    # Notify Logic (/pin loud or just /pin)
    notify = True
    if context.args and context.args[0].lower() == "silent":
        notify = False

    try:
        await update.message.reply_to_message.pin(disable_notification=not notify)
        
        msg = f"📌 **ᴍᴇssᴀɢᴇ ᴘɪɴɴᴇᴅ!**\n👮 ʙʏ: {update.effective_user.mention_html()}"
        if not notify: msg += " (Sɪʟᴇɴᴛʟʏ)"
        
        await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
    except BadRequest as e:
        await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {e}")

# --- 2. UNPIN COMMAND ---
async def unpin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_admin(update, context): return

    try:
        # Agar reply hai to wo message unpin karo, warnaa latest pin hatao
        if update.message.reply_to_message:
            await update.message.reply_to_message.unpin()
            await update.message.reply_text("📍 **ᴍᴇssᴀɢᴇ ᴜɴᴘɪɴɴᴇᴅ!**")
        else:
            await update.effective_chat.unpin_message() # Unpins the last pinned message
            await update.message.reply_text("📍 **ʟᴀsᴛ ᴘɪɴ ʀᴇᴍᴏᴠᴇᴅ!**")
    except Exception as e:
        await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {e}")

# --- 3. UNPIN ALL COMMAND ---
async def unpin_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_admin(update, context): return

    status = await update.message.reply_text("🔄 **ᴜɴᴘɪɴɴɪɴɢ ᴀʟʟ ᴍᴇssᴀɢᴇs...**")
    
    try:
        await update.effective_chat.unpin_all_messages()
        await status.edit_text("🗑️ **ᴀʟʟ ᴘɪɴɴᴇᴅ ᴍᴇssᴀɢᴇs ᴄʟᴇᴀʀᴇᴅ!**")
    except Exception as e:
        await status.edit_text(f"❌ ᴇʀʀᴏʀ: {e}")

# --- REGISTER HANDLERS ---
def register_handlers(app):
    app.add_handler(CommandHandler(["pin", "loudpin"], pin_message))
    app.add_handler(CommandHandler(["unpin"], unpin_message))
    app.add_handler(CommandHandler(["unpinall", "clearboard"], unpin_all_messages))
    print("  ✅ Pin/Unpin Tools Loaded!")
  
