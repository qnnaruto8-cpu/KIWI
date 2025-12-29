import html
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from database import (
    get_balance, update_balance, get_bank_balance, 
    update_bank_balance, get_loan, set_loan, 
    users_col, is_dead, is_protected, get_user,
    check_registered
)

# Config
MAX_LOAN_LIMIT = 50000

# --- 🔥 HELPER: FONT STYLER (Small Caps) ---
def to_fancy(text):
    normal = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    stylish = "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ"
    try:
        table = str.maketrans(normal, stylish)
        return text.translate(table)
    except:
        return text

# --- 1. CHECK BALANCE (/bal) ---
async def check_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows User Profile, Rank, Status & Balance (Reply Aware)"""
    
    # 1. Determine Target User
    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user
    else:
        target = update.effective_user

    # 🔥 BOT CHECK LOGIC
    if target.is_bot:
        msg = to_fancy("Bots do not have money! We are rich in code.")
        return await update.message.reply_text(f"🤖 <b>{msg}</b>", parse_mode=ParseMode.HTML)

    # 2. Check if Registered
    if not check_registered(target.id):
        # Get Bot Username for Link
        bot_username = context.bot.username
        if not bot_username:
            me = await context.bot.get_me()
            bot_username = me.username
        
        # Inline Button (Start to DM)
        kb = [[InlineKeyboardButton("📝 Register Here", url=f"https://t.me/{bot_username}?start=register")]]
        
        not_reg_txt = to_fancy("is not registered!")
        you_not_reg = to_fancy("You are not registered!")
        
        if target.id == update.effective_user.id:
            msg = f"🚫 <b>{html.escape(target.first_name)}</b>, {you_not_reg}"
        else:
            msg = f"🚫 <b>{html.escape(target.first_name)}</b> {not_reg_txt}"
            
        return await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)
    
    # 3. Fetch Data for Target
    uid = target.id
    wallet = get_balance(uid)
    bank = get_bank_balance(uid)
    total_amt = wallet + bank
    user_db = get_user(uid)
    kills = user_db.get("kills", 0) if user_db else 0
    
    # Determine Status
    if is_dead(uid): status = f"💀 {to_fancy('DEAD')}"
    elif is_protected(uid): status = f"🛡️ {to_fancy('PROTECTED')}"
    else: status = f"👤 {to_fancy('ALIVE')}"

    # Calculate Rank
    rank = users_col.count_documents({"balance": {"$gt": wallet}}) + 1

    # 4. Show Stats (Aesthetic Mode)
    t_profile = to_fancy('USER PROFILE')
    t_name = to_fancy('NAME')
    t_total = to_fancy('TOTAL')
    t_rank = to_fancy('RANK')
    t_status = to_fancy('STATUS')
    t_kills = to_fancy('KILLS')
    t_wallet = to_fancy('WALLET')
    t_bank = to_fancy('BANK')

    msg = (
        f"<blockquote><b>👤 {t_profile}</b></blockquote>"
        f"<blockquote><b>📛 {t_name} :</b> {html.escape(target.first_name)}\n"
        f"<b>💰 {t_total} :</b> ₹{total_amt}\n"
        f"<b>🏆 {t_rank} :</b> #{rank}\n"
        f"<b>❤️ {t_status} :</b> {status}\n"
        f"<b>⚔️ {t_kills} :</b> {kills}</blockquote>"
        f"<blockquote><b>👛 {t_wallet} :</b> ₹{wallet}\n"
        f"<b>💎 {t_bank} :</b> ₹{bank}</blockquote>"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- 2. BANK INFO ---
async def bank_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await check_balance(update, context)

# --- 3. DEPOSIT ---
async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    wallet = get_balance(user.id)
    
    if not context.args: 
        usage_txt = to_fancy("Usage:")
        return await update.message.reply_text(f"⚠️ <b>{usage_txt}</b> <code>/deposit 100</code>", parse_mode=ParseMode.HTML)
    
    if context.args[0].lower() == "all": amount = wallet
    else:
        try: amount = int(context.args[0])
        except: return await update.message.reply_text(f"❌ {to_fancy('Invalid number.')}")

    if amount <= 0: return await update.message.reply_text(f"❌ {to_fancy('Positive amount required.')}")
    if amount > wallet: return await update.message.reply_text(f"❌ {to_fancy('Insufficient funds.')}")
    
    update_balance(user.id, -amount)
    update_bank_balance(user.id, amount)
    new_bank = get_bank_balance(user.id)
    
    success_txt = to_fancy("DEPOSIT SUCCESS")
    dep_txt = to_fancy("DEPOSITED")
    new_bal_txt = to_fancy("NEW BALANCE")
    
    msg = (
        f"<blockquote><b>✅ {success_txt}</b></blockquote>"
        f"<blockquote><b>💰 {dep_txt} :</b> ₹{amount}\n"
        f"<b>💎 {new_bal_txt} :</b> ₹{new_bank}</blockquote>"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- 4. WITHDRAW ---
async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bank = get_bank_balance(user.id)
    
    if not context.args: 
        usage_txt = to_fancy("Usage:")
        return await update.message.reply_text(f"⚠️ <b>{usage_txt}</b> <code>/withdraw 100</code>", parse_mode=ParseMode.HTML)
    
    if context.args[0].lower() == "all": amount = bank
    else:
        try: amount = int(context.args[0])
        except: return await update.message.reply_text(f"❌ {to_fancy('Invalid number.')}")

    if amount <= 0: return await update.message.reply_text(f"❌ {to_fancy('Positive amount required.')}")
    if amount > bank: return await update.message.reply_text(f"❌ {to_fancy('Insufficient funds.')}")
    
    update_bank_balance(user.id, -amount)
    update_balance(user.id, amount)
    new_wallet = get_balance(user.id)
    
    success_txt = to_fancy("WITHDRAW SUCCESS")
    with_txt = to_fancy("WITHDREW")
    new_wal_txt = to_fancy("NEW WALLET")
    
    msg = (
        f"<blockquote><b>✅ {success_txt}</b></blockquote>"
        f"<blockquote><b>💸 {with_txt} :</b> ₹{amount}\n"
        f"<b>👛 {new_wal_txt} :</b> ₹{new_wallet}</blockquote>"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- 5. LOAN ---
async def take_loan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    current_loan = get_loan(user.id)
    
    if current_loan > 0: 
        err_txt = to_fancy("Pending Loan:")
        return await update.message.reply_text(f"❌ {err_txt} <b>₹{current_loan}</b>", parse_mode=ParseMode.HTML)
        
    try: amount = int(context.args[0])
    except: 
        usage_txt = to_fancy("Usage:")
        return await update.message.reply_text(f"⚠️ <b>{usage_txt}</b> <code>/loan 5000</code>", parse_mode=ParseMode.HTML)
    
    if amount > MAX_LOAN_LIMIT: 
        err_txt = to_fancy("Max Limit:")
        return await update.message.reply_text(f"❌ {err_txt} <b>₹{MAX_LOAN_LIMIT}</b>", parse_mode=ParseMode.HTML)
    
    update_balance(user.id, amount)
    set_loan(user.id, amount)
    
    app_txt = to_fancy("LOAN APPROVED")
    amt_txt = to_fancy("AMOUNT")
    note_txt = to_fancy("NOTE")
    
    msg = (
        f"<blockquote><b>💸 {app_txt}</b></blockquote>"
        f"<blockquote><b>💰 {amt_txt} :</b> ₹{amount}\n"
        f"<b>⚠️ {note_txt} :</b> Repay soon!</blockquote>"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- 6. REPAY LOAN ---
async def repay_loan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    debt = get_loan(user.id)
    wallet = get_balance(user.id)
    
    if debt == 0: 
        return await update.message.reply_text(f"✅ {to_fancy('No active loans.')}")
    
    if wallet < debt: 
        return await update.message.reply_text(f"❌ Need <b>₹{debt}</b>, have <b>₹{wallet}</b>.", parse_mode=ParseMode.HTML)
        
    update_balance(user.id, -debt)
    set_loan(user.id, 0)
    
    repaid_txt = to_fancy("LOAN REPAID")
    paid_txt = to_fancy("PAID")
    stat_txt = to_fancy("STATUS")
    
    msg = (
        f"<blockquote><b>✅ {repaid_txt}</b></blockquote>"
        f"<blockquote><b>💸 {paid_txt} :</b> ₹{debt}\n"
        f"<b>🔓 {stat_txt} :</b> Debt Free</blockquote>"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
        
