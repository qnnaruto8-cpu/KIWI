import html
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from database import get_balance, update_balance, get_bank_balance, update_bank_balance, get_loan, set_loan

# Config
MAX_LOAN_LIMIT = 50000  # Max loan amount

# Fancy Font Helper
def to_fancy(text):
    mapping = {'A': 'Λ', 'E': 'Є', 'S': 'δ', 'O': 'σ', 'T': 'ᴛ', 'N': 'ɴ', 'M': 'ᴍ', 'U': 'ᴜ', 'R': 'ʀ', 'D': 'ᴅ', 'C': 'ᴄ', 'P': 'ᴘ', 'G': 'ɢ', 'B': 'ʙ', 'L': 'ʟ', 'W': 'ᴡ', 'K': 'ᴋ', 'J': 'ᴊ', 'Y': 'ʏ', 'I': 'ɪ', 'H': 'ʜ'}
    return "".join(mapping.get(c.upper(), c) for c in text)

async def bank_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows User Wallet and Bank Status"""
    user = update.effective_user
    wallet = get_balance(user.id)
    bank = get_bank_balance(user.id)
    loan = get_loan(user.id)
    
    msg = f"""
<blockquote><b>🏦 {to_fancy("BANK STATEMENT")}</b></blockquote>

<blockquote>
<b>👤 ᴀᴄᴄᴏᴜɴᴛ :</b> {html.escape(user.first_name)}
<b>👛 ᴡᴀʟʟᴇᴛ :</b> ₹{wallet} (Unsafe)
<b>💎 ʙᴀɴᴋ :</b> ₹{bank} (Safe)
<b>💸 ʟᴏᴀɴ :</b> ₹{loan}
</blockquote>

<blockquote>
<b>🕹 {to_fancy("COMMANDS")}</b>
<code>/deposit [amount/all]</code>
<code>/withdraw [amount/all]</code>
<code>/loan [amount]</code>
<code>/payloan [amount]</code>
</blockquote>
"""
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    wallet = get_balance(user.id)
    
    if not context.args: 
        return await update.message.reply_text("⚠️ <b>Usage:</b> <code>/deposit 100</code> or <code>/deposit all</code>", parse_mode=ParseMode.HTML)
    
    # Logic for 'all'
    if context.args[0].lower() == "all":
        amount = wallet
    else:
        try: amount = int(context.args[0])
        except: return await update.message.reply_text("❌ Please enter a valid number.")

    if amount <= 0: return await update.message.reply_text("❌ Amount must be greater than 0.")
    if amount > wallet: return await update.message.reply_text("❌ Insufficient funds in wallet!")
    
    # Transaction
    update_balance(user.id, -amount)       # Deduct from Wallet
    update_bank_balance(user.id, amount)   # Add to Bank
    
    new_bank = get_bank_balance(user.id)
    
    msg = f"""
<blockquote><b>✅ {to_fancy("DEPOSIT SUCCESS")}</b></blockquote>

<blockquote>
<b>💰 ᴅᴇᴘᴏsɪᴛᴇᴅ :</b> ₹{amount}
<b>💎 ɴᴇᴡ ʙᴀʟᴀɴᴄᴇ :</b> ₹{new_bank}
</blockquote>
"""
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bank = get_bank_balance(user.id)
    
    if not context.args: 
        return await update.message.reply_text("⚠️ <b>Usage:</b> <code>/withdraw 100</code> or <code>/withdraw all</code>", parse_mode=ParseMode.HTML)
    
    if context.args[0].lower() == "all":
        amount = bank
    else:
        try: amount = int(context.args[0])
        except: return await update.message.reply_text("❌ Please enter a valid number.")

    if amount <= 0: return await update.message.reply_text("❌ Amount must be greater than 0.")
    if amount > bank: return await update.message.reply_text("❌ Insufficient funds in Bank!")
    
    # Transaction
    update_bank_balance(user.id, -amount)  # Deduct from Bank
    update_balance(user.id, amount)        # Add to Wallet
    
    new_wallet = get_balance(user.id)
    
    msg = f"""
<blockquote><b>✅ {to_fancy("WITHDRAW SUCCESS")}</b></blockquote>

<blockquote>
<b>💸 ᴡɪᴛʜᴅʀᴇᴡ :</b> ₹{amount}
<b>👛 ɴᴇᴡ ᴡᴀʟʟᴇᴛ :</b> ₹{new_wallet}
</blockquote>
"""
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

async def take_loan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    current_loan = get_loan(user.id)
    
    if current_loan > 0:
        return await update.message.reply_text(f"❌ You already have an active loan of <b>₹{current_loan}</b>! Repay it first.", parse_mode=ParseMode.HTML)
        
    try: amount = int(context.args[0])
    except: return await update.message.reply_text("⚠️ <b>Usage:</b> <code>/loan 5000</code>", parse_mode=ParseMode.HTML)
    
    if amount > MAX_LOAN_LIMIT:
        return await update.message.reply_text(f"❌ Limit Exceeded! Max Loan: <b>₹{MAX_LOAN_LIMIT}</b>", parse_mode=ParseMode.HTML)
    
    # Give Loan
    update_balance(user.id, amount)  # Add to Wallet
    set_loan(user.id, amount)        # Set Debt
    
    msg = f"""
<blockquote><b>💸 {to_fancy("LOAN APPROVED")}</b></blockquote>

<blockquote>
<b>💰 ᴀᴍᴏᴜɴᴛ :</b> ₹{amount}
<b>👤 ʙᴏʀʀᴏᴡᴇʀ :</b> {html.escape(user.first_name)}
<b>⚠️ ɴᴏᴛᴇ :</b> Repay this soon!
</blockquote>
"""
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

async def repay_loan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    debt = get_loan(user.id)
    wallet = get_balance(user.id)
    
    if debt == 0: return await update.message.reply_text("✅ You have no active loans.")
    
    # Auto calculate repayment
    amount_to_pay = debt
    if wallet < debt:
        return await update.message.reply_text(f"❌ You need <b>₹{debt}</b> to repay. You only have <b>₹{wallet}</b>.", parse_mode=ParseMode.HTML)
        
    # Repay
    update_balance(user.id, -amount_to_pay)
    set_loan(user.id, 0)
    
    msg = f"""
<blockquote><b>✅ {to_fancy("LOAN REPAID")}</b></blockquote>

<blockquote>
<b>💸 ᴘᴀɪᴅ :</b> ₹{amount_to_pay}
<b>🔓 sᴛᴀᴛᴜs :</b> Debt Free
</blockquote>
"""
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
