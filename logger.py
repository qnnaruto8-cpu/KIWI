import time
import sys
import os
import psutil
import html
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
# Yahan OWNER_IDS import kiya hai (List wala)
from config import OWNER_IDS 
from database import get_total_users, get_total_groups, get_logger_group

# Fancy Font Helper
def to_fancy(text):
    mapping = {'A': 'Λ', 'E': 'Є', 'S': 'δ', 'O': 'σ', 'T': 'ᴛ', 'N': 'ɴ', 'M': 'ᴍ', 'U': 'ᴜ', 'R': 'ʀ', 'D': 'ᴅ', 'C': 'ᴄ', 'P': 'ᴘ', 'I': 'ɪ', 'G': 'ɢ', 'B': 'ʙ', 'L': 'ʟ'}
    return "".join(mapping.get(c.upper(), c) for c in text)

# --- RESTART COMMAND ---
async def restart_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # CHANGE: Ab ye List me check karega
    if user.id not in OWNER_IDS: 
        return

    msg = await update.message.reply_text(
        f"<blockquote><b>🔄 {to_fancy('RESTARTING SYSTEM')}...</b></blockquote>", 
        parse_mode=ParseMode.HTML
    )
    time.sleep(2)
    await msg.edit_text(
        f"<blockquote><b>✅ {to_fancy('SYSTEM REBOOTED')}!</b>\nBack online in 5 seconds.</blockquote>",
        parse_mode=ParseMode.HTML
    )
    
    os.execl(sys.executable, sys.executable, *sys.argv)

# --- PING COMMAND ---
async def ping_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = time.time()
    msg = await update.message.reply_text("⚡")
    end_time = time.time()
    
    ping_ms = round((end_time - start_time) * 1000)
    
    try:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
    except:
        cpu = 0; ram = 0; disk = 0
    
    modules_list = ["Admin", "Bank", "Economy", "Games", "Market", "Anti-Spam", "Voice-AI"]
    modules_str = " | ".join(modules_list)
    
    # Direct Image Link
    PING_IMG = "https://i.ibb.co/QGGKVnw/image.png" 
    
    caption = f"""
<blockquote><b>🤖 {to_fancy("SYSTEM STATUS")}</b></blockquote>

<blockquote>
<b>⚡ ᴘɪɴɢ :</b> <code>{ping_ms}ms</code>
<b>💻 ᴄᴘᴜ :</b> <code>{cpu}%</code>
<b>💾 ʀᴀᴍ :</b> <code>{ram}%</code>
<b>💿 ᴅɪsᴋ :</b> <code>{disk}%</code>
</blockquote>

<blockquote>
<b>📚 {to_fancy("LOADED MODULES")}</b>
<code>{modules_str}</code>
</blockquote>
"""

    kb = [[InlineKeyboardButton("❌ Close", callback_data="close_ping")]]

    try: await msg.delete()
    except: pass
    
    try:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=PING_IMG,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"⚠️ <b>Image Error:</b> <code>{e}</code>\n\n{caption}",
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode=ParseMode.HTML
        )

# --- STATS COMMAND (OWNER ONLY) ---
async def stats_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # CHANGE: Ab ye List me check karega
    if user.id not in OWNER_IDS: 
        return

    try:
        users = get_total_users()
        groups = get_total_groups()
    except:
        users = 0; groups = 0

    text = f"""
<blockquote><b>📊 {to_fancy("DATABASE STATS")}</b></blockquote>

<blockquote>
<b>👤 ᴛᴏᴛᴀʟ ᴜsᴇʀs :</b> <code>{users}</code>
<b>👥 ᴛᴏᴛᴀʟ ɢʀᴏᴜᴘs :</b> <code>{groups}</code>
<b>⚡ sᴇʀᴠᴇʀ :</b> <code>Online</code>
</blockquote>
"""
    kb = [[InlineKeyboardButton("🗑 Close Stats", callback_data="close_log")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)
    
