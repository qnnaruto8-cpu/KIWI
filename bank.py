from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from database import get_balance, update_balance, get_bank_balance, update_bank_balance, get_loan, set_loan

# Config
MAX_LOAN_LIMIT = 50000  # Max loan amount

async def bank_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User ka Wallet aur Bank status dikhayega"""
    user = update.effective_user
    wallet = get_balance(user.id)
    bank = get_bank_balance(user.id)
    loan = get_loan(user.id)
    
    msg = (
        f"🏦 **BANK OF {user.first_name}** 🏦\n\n"
        f"👛 **Wallet:** ₹{wallet} (Unsafe)\n"
        f"💎 **Bank:** ₹{bank} (Safe)\n"
        f"💸 **Loan:** ₹{loan}\n\n"
        f"Commands:\n"
        f"`/deposit <amount>` - Bank me daalo\n"
        f"`/withdraw <amount>` - Bank se nikalo\n"
        f"`/loan <amount>` - Loan lo\n"
        f"`/payloan <amount>` - Loan chukao"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    wallet = get_balance(user.id)
    
    if not context.args: return await update.message.reply_text("⚠️ Usage: `/deposit 100` or `/deposit all`")
    
    # Logic for 'all'
    if context.args[0].lower() == "all":
        amount = wallet
    else:
        try: amount = int(context.args[0])
        except: return await update.message.reply_text("❌ Number likh bhai!")

    if amount <= 0: return await update.message.reply_text("❌ 0 se zyada daal!")
    if amount > wallet: return await update.message.reply_text("❌ Jeb me itna paisa nahi hai!")
    
    # Transaction
    update_balance(user.id, -amount)       # Wallet se kaato
    update_bank_balance(user.id, amount)   # Bank me daalo
    
    await update.message.reply_text(f"✅ **Deposited ₹{amount}**\n🏦 Bank Balance: ₹{get_bank_balance(user.id)}")

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bank = get_bank_balance(user.id)
    
    if not context.args: return await update.message.reply_text("⚠️ Usage: `/withdraw 100` or `/withdraw all`")
    
    if context.args[0].lower() == "all":
        amount = bank
    else:
        try: amount = int(context.args[0])
        except: return await update.message.reply_text("❌ Number likh bhai!")

    if amount <= 0: return await update.message.reply_text("❌ 0 se zyada nikal!")
    if amount > bank: return await update.message.reply_text("❌ Bank me itna paisa nahi hai!")
    
    # Transaction
    update_bank_balance(user.id, -amount)  # Bank se kaato
    update_balance(user.id, amount)        # Wallet me daalo
    
    await update.message.reply_text(f"✅ **Withdrew ₹{amount}**\n👛 Wallet Balance: ₹{get_balance(user.id)}")

async def take_loan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    current_loan = get_loan(user.id)
    
    if current_loan > 0:
        return await update.message.reply_text(f"❌ Pehle purana loan (₹{current_loan}) chukao!")
        
    try: amount = int(context.args[0])
    except: return await update.message.reply_text("⚠️ Usage: `/loan 5000`")
    
    if amount > MAX_LOAN_LIMIT:
        return await update.message.reply_text(f"❌ Bank Limit Exceeded! Max Loan: ₹{MAX_LOAN_LIMIT}")
    
    # Give Loan
    update_balance(user.id, amount)  # Wallet me paisa
    set_loan(user.id, amount)        # Karza chadh gaya
    
    await update.message.reply_text(f"💸 **Loan Approved!**\nAdded ₹{amount} to wallet.\nJaldi wapis kar dena!")

async def repay_loan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    debt = get_loan(user.id)
    wallet = get_balance(user.id)
    
    if debt == 0: return await update.message.reply_text("✅ Tumhare upar koi loan nahi hai.")
    
    # Auto calculate repayment
    amount_to_pay = debt
    if wallet < debt:
        return await update.message.reply_text(f"❌ Loan chukane ke liye ₹{debt} chahiye. Tumhare paas sirf ₹{wallet} hai.")
        
    # Repay
    update_balance(user.id, -amount_to_pay)
    set_loan(user.id, 0)
    
    await update.message.reply_text(f"✅ **Loan Paid!**\nTum ab karz-mukt ho gaye.")
  
