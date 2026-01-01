import asyncio
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from telegram.constants import ParseMode

# Configs
from config import OWNER_ID
from tools.stream import worker_app  # Assistant Client
# ⚠️ DHYAAN DO: Ye functions tumhare database.py mein hone chahiye
from database import get_served_users, get_served_chats 

# --- SUDO SETTINGS ---
# Tumhara ID aur Owner ID (config se)
SUDO_USERS = [6356015122, int(OWNER_ID)]

# --- 1. BROADCAST USERS (DM) ---
async def broadcast_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in SUDO_USERS: return

    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ **Message par Reply karke command do.**")

    status_msg = await update.message.reply_text("🔄 **Broadcasting to Users (DMs)...**")
    
    # Database se users list nikalo
    users = await get_served_users()
    sent = 0
    failed = 0
    
    msg = update.message.reply_to_message
    
    for user_id in users:
        try:
            # Copy Message (Text, Media, Sticker sab kuch copy hota hai)
            await context.bot.copy_message(chat_id=user_id, from_chat_id=msg.chat.id, message_id=msg.message_id)
            sent += 1
            await asyncio.sleep(0.1) # Floodwait se bachne ke liye
        except:
            failed += 1
            
    await status_msg.edit_text(f"✅ **DM Broadcast Done**\n\nSent: {sent}\nFailed: {failed}")

# --- 2. BROADCAST GROUPS (GC) ---
async def broadcast_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in SUDO_USERS: return

    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ **Message par Reply karke command do.**")

    status_msg = await update.message.reply_text("🔄 **Broadcasting to Groups...**")
    
    chats = await get_served_chats()
    sent = 0
    failed = 0
    
    msg = update.message.reply_to_message
    
    for chat_id in chats:
        try:
            await context.bot.copy_message(chat_id=chat_id, from_chat_id=msg.chat.id, message_id=msg.message_id)
            sent += 1
            await asyncio.sleep(0.1)
        except:
            failed += 1
            
    await status_msg.edit_text(f"✅ **Group Broadcast Done**\n\nSent: {sent}\nFailed: {failed}")

# --- 3. BROADCAST ASSISTANT (AC) ---
async def broadcast_assistant(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in SUDO_USERS: return

    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ **Message par Reply karke command do.**")

    status_msg = await update.message.reply_text("🔄 **Assistant Broadcasting...**")
    
    reply = update.message.reply_to_message
    # Text ya Caption nikalo
    query = reply.text or reply.caption
    
    chats = await get_served_chats()
    sent = 0
    failed = 0

    # Assistant Logic: Sirf Text/Link bhejega taaki fast rahe aur media download ka issue na ho
    if not query:
         return await status_msg.edit_text("❌ Assistant Broadcast ke liye message mein TEXT hona zaroori hai.")

    for chat_id in chats:
        try:
            # Assistant Groups mein bhejega
            await worker_app.send_message(chat_id, query)
            sent += 1
            await asyncio.sleep(1.5) # Assistant ko slow rakhna padta hai (Ban Safety)
        except:
            failed += 1

    await status_msg.edit_text(f"✅ **Assistant Broadcast Done**\n\nSent: {sent}\nFailed: {failed}")

# --- 🔥 4. BROADCAST ALL (MEGA COMMAND) ---
async def broadcast_all_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in SUDO_USERS: return

    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ **Message par Reply karke `/broadcastall` likho.**")

    status_msg = await update.message.reply_text("🚀 **Starting GLOBAL Broadcast (Bot + Assistant)...**\nYe thoda time lega, please wait karein.")

    msg = update.message.reply_to_message
    query = msg.text or msg.caption
    
    # Database Fetch
    users_list = await get_served_users()
    chats_list = await get_served_chats()
    
    dm_sent, dm_fail = 0, 0
    gc_sent, gc_fail = 0, 0
    ac_sent, ac_fail = 0, 0

    # PHASE 1: BOT -> DMs
    await status_msg.edit_text("🔄 **Phase 1: Bot Sending to DMs...**")
    for u_id in users_list:
        try:
            await context.bot.copy_message(chat_id=u_id, from_chat_id=msg.chat.id, message_id=msg.message_id)
            dm_sent += 1
            await asyncio.sleep(0.1)
        except: dm_fail += 1

    # PHASE 2: BOT -> GROUPS
    await status_msg.edit_text(f"✅ DMs Done ({dm_sent}).\n🔄 **Phase 2: Bot Sending to Groups...**")
    for c_id in chats_list:
        try:
            await context.bot.copy_message(chat_id=c_id, from_chat_id=msg.chat.id, message_id=msg.message_id)
            gc_sent += 1
            await asyncio.sleep(0.1)
        except: gc_fail += 1

    # PHASE 3: ASSISTANT -> GROUPS
    # Assistant sirf Text bhejega. Agar Text nahi hai to ye step skip hoga.
    if query:
        await status_msg.edit_text(f"✅ Bot Groups Done ({gc_sent}).\n🔄 **Phase 3: Assistant Sending to Groups...**")
        for c_id in chats_list:
            try:
                await worker_app.send_message(c_id, query)
                ac_sent += 1
                await asyncio.sleep(1.5) # Safety Sleep
            except: ac_fail += 1
    else:
        await status_msg.edit_text("⚠️ Message mein Text nahi tha, isliye Assistant Broadcast Skip kiya gaya.")

    # FINAL REPORT
    report = f"""
✅ **GLOBAL BROADCAST COMPLETE**

👤 **Bot DMs:** {dm_sent} (Fail: {dm_fail})
📢 **Bot Groups:** {gc_sent} (Fail: {gc_fail})
🎸 **Assistant Groups:** {ac_sent} (Fail: {ac_fail})

⚡ **Powered by:** {user.first_name}
"""
    await status_msg.edit_text(report)

# --- HANDLER REGISTRATION ---
def register_broadcast_handlers(app):
    app.add_handler(CommandHandler(["broadcast", "broadcastdm"], broadcast_users))
    app.add_handler(CommandHandler(["broadcastgc", "broadcastgroup"], broadcast_groups))
    app.add_handler(CommandHandler(["broadcastac"], broadcast_assistant))
    app.add_handler(CommandHandler(["broadcastall", "bcall"], broadcast_all_command))
    print("📢 Broadcast Module Loaded!")
  
