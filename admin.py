from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from config import OWNER_ID
from database import (
    users_col, groups_col, codes_col, update_balance, # <-- groups_col added
    add_api_key, remove_api_key, get_all_keys,
    wipe_database, set_economy_status, get_economy_status
)

# --- BROADCAST & MONEY COMMANDS ---

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    if not context.args: return await update.message.reply_text("⚠️ Message toh likho!")

    msg = " ".join(context.args)
    
    # 1. Users ko bhejo
    users = users_col.find({})
    user_count = 0
    for u in users:
        try: 
            await context.bot.send_message(u["_id"], f"📢 **NOTICE**\n\n{msg}", parse_mode=ParseMode.MARKDOWN)
            user_count += 1
        except: pass

    # 2. Groups ko bhejo
    groups = groups_col.find({})
    group_count = 0
    for g in groups:
        try:
            await context.bot.send_message(g["_id"], f"📢 **NOTICE**\n\n{msg}", parse_mode=ParseMode.MARKDOWN)
            group_count += 1
        except: pass

    await update.message.reply_text(
        f"✅ **Broadcast Complete!**\n\n"
        f"👤 Sent to Users: `{user_count}`\n"
        f"👥 Sent to Groups: `{group_count}`",
        parse_mode=ParseMode.MARKDOWN
    )

async def create_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    try:
        codes_col.insert_one({
            "code": context.args[0], 
            "amount": int(context.args[1]), 
            "limit": int(context.args[2]), 
            "redeemed_by": []
        })
        await update.message.reply_text("✅ Code Created")
    except: await update.message.reply_text("⚠️ Format: `/code NAME AMOUNT LIMIT`")

async def add_money(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    try: 
        update_balance(int(context.args[0]), int(context.args[1]))
        await update.message.reply_text("✅ Money Added")
    except: await update.message.reply_text("⚠️ Usage: `/add <user_id> <amount>`")

async def take_money(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    try: 
        update_balance(int(context.args[0]), -int(context.args[1]))
        await update.message.reply_text("✅ Money Taken")
    except: await update.message.reply_text("⚠️ Usage: `/take <user_id> <amount>`")

# --- API KEY COMMANDS ---

async def add_key_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    try:
        new_key = context.args[0]
        if add_api_key(new_key):
            await update.message.reply_text("✅ **API Key Added!**", parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text("⚠️ Key already exists!")
    except:
        await update.message.reply_text("⚠️ Usage: `/addkey <Key>`")
    try: await update.message.delete()
    except: pass

async def remove_key_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    try:
        if remove_api_key(context.args[0]):
            await update.message.reply_text("🗑 **API Key Removed!**", parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text("❌ Key not found.")
    except:
        await update.message.reply_text("⚠️ Usage: `/delkey <Key>`")
    try: await update.message.delete()
    except: pass

async def list_keys_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    keys = get_all_keys()
    await update.message.reply_text(f"🔑 **Total Active API Keys:** `{len(keys)}`", parse_mode=ParseMode.MARKDOWN)

# --- 🔥 ECONOMY & RESET ---

async def economy_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Economy ON/OFF switch"""
    if update.effective_user.id != OWNER_ID: return
    
    current = get_economy_status()
    new_status = not current
    set_economy_status(new_status)
    
    status_text = "🟢 **ON**" if new_status else "🔴 **OFF**"
    await update.message.reply_text(f"⚙️ **Economy System:** {status_text}", parse_mode=ParseMode.MARKDOWN)

async def reset_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Database Wipe Warning"""
    if update.effective_user.id != OWNER_ID: return
    
    keyboard = [
        [InlineKeyboardButton("⚠️ YES, WIPE DATA", callback_data="confirm_wipe")],
        [InlineKeyboardButton("❌ CANCEL", callback_data="cancel_wipe")]
    ]
    
    await update.message.reply_text(
        "☢️ **WARNING: DATABASE RESET** ☢️\n\n"
        "Kya aap sach me saare Users, Money aur Investments delete karna chahte hain?\n"
        "**Ye action undo nahi ho sakta!**",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def reset_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Reset Buttons"""
    query = update.callback_query
    if query.from_user.id != OWNER_ID: 
        await query.answer("Sirf Owner kar sakta hai!", show_alert=True); return

    if query.data == "confirm_wipe":
        wipe_database()
        await query.edit_message_text("💀 **DATABASE WIPED SUCCESSFULLY!**\nSab Zero ho gaye.")
    
    elif query.data == "cancel_wipe":
        await query.message.delete()
        
