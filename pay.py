import time
import random
import html
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from database import (
    update_balance, get_balance, get_user, 
    set_protection, is_protected, get_economy_status, 
    update_kill_count, set_dead, is_dead,
    check_registered, register_user
)

# --- ECONOMY CONFIGS ---
PROTECT_COST_PER_DAY = 5000   # Cost for 1 Day
HOSPITAL_FEE = 5000           # Revive Cost
ROB_FAIL_PENALTY = 500 
KILL_REWARD = 900     
AUTO_REVIVE_TIME = 1800 

# --- 🔥 HELPER: FONT STYLER (Small Caps) ---
def to_fancy(text):
    normal = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    stylish = "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ"
    try:
        table = str.maketrans(normal, stylish)
        return text.translate(table)
    except:
        return text

# --- HELPER: REGISTER BUTTON ---
async def send_register_button(update):
    user = update.effective_user
    kb = [[InlineKeyboardButton("📝 Register Now", callback_data=f"reg_start_{user.id}")]]
    await update.message.reply_text(
        f"🛑 <b>{user.first_name}, {to_fancy('Register First!')}</b>",
        reply_markup=InlineKeyboardMarkup(kb),
        quote=True,
        parse_mode=ParseMode.HTML
    )

# --- 🔥 AUTO REVIVE JOB ---
async def auto_revive_job(context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = context.job.data
        if is_dead(user_id):
            set_dead(user_id, False) 
            try:
                msg = to_fancy("Miracle! You have been automatically revived!")
                await context.bot.send_message(user_id, f"✨ <b>{msg}</b> 🧘‍♂️", parse_mode=ParseMode.HTML)
            except: pass
    except Exception as e:
        print(f"❌ Auto Revive Error: {e}")

# --- 1. PAY (Transfer Money) ---
async def pay_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not get_economy_status(): 
        return await update.message.reply_text(f"🔴 <b>{to_fancy('Economy is OFF!')}</b>")
    
    sender = update.effective_user
    
    if not check_registered(sender.id): return await send_register_button(update)
    if is_dead(sender.id): 
        return await update.message.reply_text(f"👻 <b>{to_fancy('Ghosts cannot use the bank! Revive first.')}</b>")

    if not update.message.reply_to_message:
        return await update.message.reply_text(f"⚠️ <b>{to_fancy('Usage:')}</b> {to_fancy('Reply to a user with')} <code>/pay 100</code>", parse_mode=ParseMode.HTML)
    
    receiver = update.message.reply_to_message.from_user
    if receiver.is_bot or sender.id == receiver.id: 
        return await update.message.reply_text(f"❌ {to_fancy('Invalid transaction!')}")
    
    if not check_registered(receiver.id): 
        return await update.message.reply_text(f"❌ <b>{receiver.first_name}</b> {to_fancy('is not registered.')}", parse_mode=ParseMode.HTML)

    try: 
        amount = int(context.args[0])
        if amount <= 0: raise ValueError
    except: 
        return await update.message.reply_text(f"⚠️ <b>{to_fancy('Usage:')}</b> <code>/pay 100</code>", parse_mode=ParseMode.HTML)
    
    if get_balance(sender.id) < amount: 
        return await update.message.reply_text(f"❌ {to_fancy('Insufficient funds!')}")
    
    update_balance(sender.id, -amount)
    update_balance(receiver.id, amount)
    
    txt = to_fancy(f"Transfer: ₹{amount} sent to")
    await update.message.reply_text(f"💸 <b>{txt} {html.escape(receiver.first_name)}</b> ✅", parse_mode=ParseMode.HTML)

# --- 2. PROTECT (Shield) ---
async def protect_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not get_economy_status(): return
    user = update.effective_user
    
    if not check_registered(user.id): return await send_register_button(update)
    if is_dead(user.id): 
        return await update.message.reply_text(f"👻 {to_fancy('Dead bodies cannot buy protection.')}")

    # Logic for /protect 1d, /protect 2d etc.
    days = 1
    if context.args:
        arg = context.args[0].lower()
        if arg.endswith("d") and arg[:-1].isdigit():
            days = int(arg[:-1])
        else:
            return await update.message.reply_text(f"⚠️ <b>{to_fancy('Usage:')}</b> `/protect 1d` ({to_fancy('for 1 day')})", parse_mode=ParseMode.MARKDOWN)

    total_cost = PROTECT_COST_PER_DAY * days

    if get_balance(user.id) < total_cost:
        msg = to_fancy(f"You need ₹{total_cost} for {days} days protection!")
        return await update.message.reply_text(f"❌ {msg}")
        
    if is_protected(user.id):
        return await update.message.reply_text(f"🛡️ {to_fancy('You are already Protected!')}")
    
    update_balance(user.id, -total_cost)
    set_protection(user.id, 24 * days) 
    
    # 🔥 SHORT MESSAGE
    t1 = to_fancy("Shield Activated!")
    t2 = to_fancy("Cost:")
    await update.message.reply_text(f"🛡️ <b>{t1}</b> ({days} Days)\n💸 {t2} ₹{total_cost}", parse_mode=ParseMode.HTML)

# --- 3. ROB (Steal) ---
async def rob_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not get_economy_status(): return
    thief = update.effective_user
    
    if not check_registered(thief.id): return await send_register_button(update)
    if is_dead(thief.id): 
        return await update.message.reply_text(f"👻 {to_fancy('Ghosts cannot rob!')}")

    if not update.message.reply_to_message:
        return await update.message.reply_text(f"⚠️ {to_fancy('Reply with')} <code>/rob</code>.", parse_mode=ParseMode.HTML)
    
    victim = update.message.reply_to_message.from_user
    if not victim or victim.is_bot or thief.id == victim.id: return
    
    if not check_registered(victim.id): 
        return await update.message.reply_text(f"⚠️ <b>{victim.first_name}</b> {to_fancy('is not registered.')}", parse_mode=ParseMode.HTML)
    
    if is_dead(victim.id): 
        return await update.message.reply_text(f"☠️ {to_fancy('Cannot loot a dead body!')}")
    
    if is_protected(victim.id): 
        return await update.message.reply_text(f"🛡️ {to_fancy('Target is Protected!')}")
    
    victim_bal = get_balance(victim.id)
    if victim_bal < 100: 
        return await update.message.reply_text(f"❌ {to_fancy('Target is too poor.')}")

    if random.random() < 0.4:
        loot = int(victim_bal * random.uniform(0.1, 0.4)) 
        update_balance(victim.id, -loot)
        update_balance(thief.id, loot)
        
        msg = to_fancy(f"You robbed ₹{loot} from")
        await update.message.reply_text(f"🔫 <b>{msg} {html.escape(victim.first_name)}!</b> 😈", parse_mode=ParseMode.HTML)
    else:
        update_balance(thief.id, -ROB_FAIL_PENALTY)
        msg = to_fancy("Police Caught You! Fined:")
        await update.message.reply_text(f"👮 <b>{msg} ₹{ROB_FAIL_PENALTY}</b>", parse_mode=ParseMode.HTML)

# --- 4. KILL (Murder) ---
async def kill_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not get_economy_status(): return
    killer = update.effective_user
    
    if not check_registered(killer.id): return await send_register_button(update)
    if is_dead(killer.id): 
        return await update.message.reply_text(f"👻 {to_fancy('You are dead!')}")
    
    if not update.message.reply_to_message: 
        return await update.message.reply_text(f"⚠️ {to_fancy('Reply with')} <code>/kill</code>.", parse_mode=ParseMode.HTML)
    
    victim = update.message.reply_to_message.from_user
    if not victim or victim.is_bot or killer.id == victim.id: return
    
    if not check_registered(victim.id): register_user(victim.id, victim.first_name)
    if is_dead(victim.id): 
        return await update.message.reply_text(f"☠️ {to_fancy('Already Dead!')}")
    
    if is_protected(victim.id): 
        return await update.message.reply_text(f"🛡️ {to_fancy('Target is Protected.')}")

    try:
        victim_bal = get_balance(victim.id)
        if victim_bal > 0:
            loss = int(victim_bal * 0.5)
            update_balance(victim.id, -loss)
        
        update_balance(killer.id, KILL_REWARD)
        set_dead(victim.id, True)
        update_kill_count(killer.id)
        
        if context.job_queue:
            context.job_queue.run_once(auto_revive_job, AUTO_REVIVE_TIME, data=victim.id)
        
        # 🔥 SHORT & STYLISH MESSAGE
        k_name = to_fancy(killer.first_name)
        v_name = to_fancy(victim.first_name)
        killed_txt = to_fancy("killed")
        earned_txt = to_fancy("Earned:")
        
        msg = f"👤 <b>{k_name}</b> {killed_txt} <b>{v_name}</b>!\n💰 <b>{earned_txt}</b> ₹{KILL_REWARD}"
        await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
        
    except Exception as e:
        print(f"❌ Kill Error: {e}")

# --- 5. REVIVE COMMAND ---
async def revive_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payer = update.effective_user
    
    if not check_registered(payer.id): return await send_register_button(update)
    
    target = payer
    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user
        
    if not is_dead(target.id):
        msg = to_fancy("is already alive!")
        return await update.message.reply_text(f"🏥 <b>{target.first_name}</b> {msg}", parse_mode=ParseMode.HTML)
    
    if get_balance(payer.id) < HOSPITAL_FEE:
        msg = to_fancy(f"You need ₹{HOSPITAL_FEE} to revive!")
        return await update.message.reply_text(f"❌ {msg}", parse_mode=ParseMode.HTML)
    
    update_balance(payer.id, -HOSPITAL_FEE)
    set_dead(target.id, False)
    
    fee_txt = to_fancy(f"Fee: ₹{HOSPITAL_FEE}")
    
    if payer.id == target.id:
        revived_txt = to_fancy("You Revived Yourself!")
        await update.message.reply_text(f"✨ <b>{revived_txt}</b>\n💸 {fee_txt}", parse_mode=ParseMode.HTML)
    else:
        revived_txt = to_fancy(f"You Revived {target.first_name}!")
        paid_txt = to_fancy("(Paid by you)")
        await update.message.reply_text(f"✨ <b>{revived_txt}</b>\n💸 {fee_txt} {paid_txt}", parse_mode=ParseMode.HTML)

# --- 6. ALIVE / STATUS ---
async def check_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not check_registered(user.id): return
    
    if is_dead(user.id):
        status = f"☠️ <b>{to_fancy('DEAD')}</b>"
    elif is_protected(user.id):
        status = f"🛡️ <b>{to_fancy('PROTECTED')}</b>"
    else:
        status = f"⚠️ <b>{to_fancy('VULNERABLE')}</b>"
    
    money_txt = to_fancy("Money:")
    status_txt = to_fancy("Status:")
    
    await update.message.reply_text(f"❤️ <b>{status_txt}</b> {status}\n💰 <b>{money_txt}</b> ₹{get_balance(user.id)}", parse_mode=ParseMode.HTML)

