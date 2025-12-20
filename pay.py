import time
import random
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
PROTECT_COST = 5000   
HOSPITAL_FEE = 5000   
ROB_FAIL_PENALTY = 500 
KILL_REWARD = 900     
AUTO_REVIVE_TIME = 1800 # 30 Minutes

# --- HELPER: REGISTER BUTTON ---
async def send_register_button(update):
    user = update.effective_user
    kb = [[InlineKeyboardButton("📝 Register Now", callback_data=f"reg_start_{user.id}")]]
    await update.message.reply_text(
        f"🛑 **{user.first_name}, Register First!**\nGame khelne ke liye register karna zaroori hai.",
        reply_markup=InlineKeyboardMarkup(kb),
        quote=True
    )

# --- 🔥 AUTO REVIVE JOB ---
async def auto_revive_job(context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = context.job.data
        if is_dead(user_id):
            set_dead(user_id, False) 
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text="✨ **Miracle!**\n30 minute pure ho gaye. Tum automatically **Zinda** ho gaye ho! 🧘‍♂️",
                    parse_mode=ParseMode.MARKDOWN
                )
            except: pass
    except Exception as e:
        print(f"❌ Auto Revive Error: {e}")

# --- 3. ROB (Chori) ---
async def rob_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 1. Check Economy
    if not get_economy_status(): return await update.message.reply_text("🔴 Economy OFF.")
    
    thief = update.effective_user
    
    # 2. Check Registration
    if not check_registered(thief.id):
        await send_register_button(update)
        return

    # 3. Check Dead Status
    if is_dead(thief.id): return await update.message.reply_text("👻 Bhoot chori nahi kar sakte!")

    # 4. Check Reply (IMPORTANT)
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ **Galti!**\nJisko lootna hai uske message par **Reply** karke `/rob` likho.")
    
    victim = update.message.reply_to_message.from_user
    
    # 5. Victim Checks
    if not victim or victim.is_bot: return await update.message.reply_text("👮 Bot ko nahi loot sakte!")
    if thief.id == victim.id: return await update.message.reply_text("❌ Khud ki jeb katega?")
    
    if not check_registered(victim.id):
        return await update.message.reply_text(f"⚠️ **Fail!** {victim.first_name} registered nahi hai.")

    if is_dead(victim.id): return await update.message.reply_text("☠️ Wo pehle se mara hua hai!")
    
    if is_protected(victim.id):
        return await update.message.reply_text(f"🛡️ **Fail!** {victim.first_name} ke paas Shield hai!")
    
    victim_bal = get_balance(victim.id)
    if victim_bal < 100:
        return await update.message.reply_text("❌ Is bhikari ke paas 100 rupay bhi nahi hain!")

    # 6. Robbery Logic
    if random.random() < 0.4: # 40% Chance Success
        loot = int(victim_bal * random.uniform(0.1, 0.4)) 
        
        # Database Update
        update_balance(victim.id, -loot)
        update_balance(thief.id, loot)
        
        await update.message.reply_text(f"🔫 **ROBBERY SUCCESS!**\nTune {victim.first_name} ke ₹{loot} uda liye! 🏃‍♂️💨")
        
        # Notify Victim
        try:
            await context.bot.send_message(
                chat_id=victim.id,
                text=(f"⚠️ **YOU WERE ROBBED!**\nRobber: 👤 {thief.first_name}\nLost: ₹{loot}\nUse `/bank` to save money!")
            )
        except: pass

    else:
        # Failure
        update_balance(thief.id, -ROB_FAIL_PENALTY)
        await update.message.reply_text(f"👮 **POLICE AA GAYI!**\nChori pakdi gayi.\nFine: ₹{ROB_FAIL_PENALTY} kat gaye!")


# --- 4. KILL (Murder) ---
async def kill_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 1. Economy Check
    if not get_economy_status(): return await update.message.reply_text("🔴 Economy OFF.")
    
    killer = update.effective_user
    
    # 2. Registration Check
    if not check_registered(killer.id):
        await send_register_button(update)
        return

    if is_dead(killer.id): return await update.message.reply_text("👻 **Tu khud dead hai!**")

    # 3. Reply Check (IMPORTANT)
    if not update.message.reply_to_message: 
        return await update.message.reply_text("⚠️ **Galti!**\nJisko maarna hai uske message par **Reply** karke `/kill` likho.")
    
    victim = update.message.reply_to_message.from_user
    
    # 4. Victim Checks
    if not victim or victim.is_bot: return await update.message.reply_text("🤖 Main Amar hu! Mujhe koi nahi maar sakta.")
    if killer.id == victim.id: return await update.message.reply_text("❌ Suicide mat kar bhai! ❤️")
    
    if not check_registered(victim.id):
        # Agar victim register nahi hai, to register kar do taaki game chale
        register_user(victim.id, victim.first_name)
    
    if is_dead(victim.id):
        return await update.message.reply_text(f"☠️ **Already Dead!**\n{victim.first_name} pehle se mara hua hai.")

    if is_protected(victim.id):
        return await update.message.reply_text(f"🛡️ **Fail!** {victim.first_name} Protected hai.")

    # 5. Kill Logic
    try:
        victim_bal = get_balance(victim.id)
        if victim_bal > 0:
            loss = int(victim_bal * 0.5) # 50% Paisa loss
            update_balance(victim.id, -loss)
        
        update_balance(killer.id, KILL_REWARD)
        
        set_dead(victim.id, True)
        update_kill_count(killer.id)
        
        # 🔥 JOB QUEUE CHECK
        if context.job_queue:
            context.job_queue.run_once(auto_revive_job, AUTO_REVIVE_TIME, data=victim.id)
        else:
            print("❌ Error: JobQueue setup nahi hai main.py me!")
        
        kb = [[InlineKeyboardButton(f"🏥 Instant Revive (₹{HOSPITAL_FEE})", callback_data=f"revive_{victim.id}")]]
        
        await update.message.reply_text(
            f"💀 **MURDER!**\n"
            f"🔪 **Killer:** {killer.first_name}\n"
            f"🩸 **Victim:** {victim.first_name} (DIED)\n"
            f"💰 **Bounty:** Killer got ₹{KILL_REWARD}!\n"
            f"⏳ **Note:** Victim 30 mins mein apne aap zinda ho jayega.",
            reply_markup=InlineKeyboardMarkup(kb)
        )

        try:
            await context.bot.send_message(
                chat_id=victim.id,
                text=(f"⚠️ **You were killed!**\nKiller: 👤 {killer.first_name}\nStatus: ☠️ DEAD\n\n💡 Tum 30 min baad automatic zinda ho jaoge.")
            )
        except: pass

    except Exception as e:
        print(f"❌ Kill Error: {e}")
        await update.message.reply_text("❌ Error aa gaya database me.")
