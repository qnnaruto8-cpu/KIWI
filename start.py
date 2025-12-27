import time
import psutil
import asyncio
import html 
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, CallbackQueryHandler

# 🔥 Database Imports
from database import check_registered, register_user, get_logger_group 
from config import OWNER_ID, OWNER_NAME, GROUP_LINK, INSTAGRAM_LINK, UPDATE_CHANNEL, BOT_NAME 
from ai_chat import get_mimi_sticker

# --- GLOBAL VARS ---
START_IMG = "https://i.ibb.co/8gW9bqTd/IMG-20251224-191812-875.jpg" 
BOT_START_TIME = time.time()

# --- HELPER: GET UPTIME ---
def get_readable_time():
    seconds = int(time.time() - BOT_START_TIME)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    if d > 0:
        return f"{d}d:{h}h:{m}m:{s}s"
    return f"{h}h:{m}m:{s}s"

# --- MAIN START COMMAND ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    bot_username = context.bot.username
    bot_name = context.bot.first_name
    
    first_name = html.escape(user.first_name)

    # 🔥 1. GROUP LOGIC (Fancy DM Message)
    if chat.type != "private":
        # Fancy Design Text
        txt = "<blockquote><b>Start in DM me</b></blockquote>"
        
        # Inline Button for DM
        kb = [[InlineKeyboardButton("Start in DM ↗️", url=f"https://t.me/{bot_username}?start=true")]]
        
        await update.message.reply_text(
            txt, 
            reply_markup=InlineKeyboardMarkup(kb), 
            parse_mode=ParseMode.HTML
        )
        return

    # --- 2. DM (PRIVATE) LOGIC ---
    
    # Animation
    try:
        sticker_id = await get_mimi_sticker(context.bot)
        if sticker_id:
            stk = await update.message.reply_sticker(sticker=sticker_id)
            await asyncio.sleep(2)
            await stk.delete()
    except: pass 

    msg = await update.message.reply_text("🍭")
    await asyncio.sleep(0.5)
    
    # Loading Bars
    bars = [
        "⚡ 𝚲𝛈𝛊𝛄𝛂 ɪs ʟᴏᴀᴅɪɴɢ....🌷🍡",
        "💕 𝚲𝛈𝛊𝛄𝛂 ɪs ʟᴏᴀᴅɪɴɢ..🌷 ",
        "👀 𝚲𝛈𝛊𝛄𝛂 ɪs ʟᴏᴀᴅɪɴɢ...🍡",
        "🍷 𝚲𝛈𝛊𝛄𝛂 ɪs ʟᴏᴀᴅɪɴɢ.... ",
        "🍫 𝚲𝛈𝛊𝛄𝛂 ɪs ʟᴏᴀᴅɪɴɢ. ",
        "🫀 𝚲𝛈𝛊𝛄𝛂 ɪs ʟᴏᴀᴅɪɴɢ.. ",
        "🥂 𝚲𝛈𝛊𝛄𝛂 ɪs ʟᴏᴀᴅɪɴɢ...🌷🍡!"
    ]
    for bar in bars:
        try:
            await msg.edit_text(bar)
            await asyncio.sleep(0.3)
        except: pass
    await msg.delete() 

    # Caption Info
    try:
        uptime = get_readable_time()
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
    except:
        uptime = "00:00:00"; cpu=0; ram=0; disk=0

    # Main Caption
    caption = f"""┌────── ˹ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ˼─── ⏤‌‌●
┆◍ ʜєʏ, {first_name} 🥀
┆◍ ɪ ᴧϻ {bot_name}
└────────────────────•
<pre>
ɪ ᴀᴍ ᴛʜᴇ ᴍᴏsᴛ ᴀᴅᴠᴀɴᴄᴇᴅ ᴍᴜʟᴛɪ-ᴘᴜʀᴘᴏsᴇ ʙᴏᴛ. 
ɪ ᴏғғᴇʀ ʜɪɢʜ-ǫᴜᴀʟɪᴛʏ ᴍᴜsɪᴄ, ɢʟᴏʙᴀʟ ᴇᴄᴏɴᴏᴍʏ
ᴀɪ ᴄʜᴀᴛ & ɢʀᴏᴜᴘ sᴇᴄᴜʀɪᴛʏ.
<pre>
<pre>
╭─ ⚙️ SYSTEM STATUS
│ ➥ UPTIME: {uptime}
│ ➥ SERVER STORAGE: {disk:.1f}%
│ ➥ CPU LOAD: {cpu:.1f}%
│ ➥ RAM CONSUMPTION: {ram:.1f}%
╰───────────────
<pre>
•──────────────────────•
<pre>
✦ ᴘᴏᴡєʀєᴅ ʙʏ © BOSS JI
<pre>
"""

    # Register & Log
    is_new_user = False
    if not check_registered(user.id):
        register_user(user.id, user.first_name)
        is_new_user = True
        
    logger_id = get_logger_group()
    if logger_id:
        try:
            log_msg = f"""
<blockquote><b>📢 ᴜsᴇʀ sᴛᴀʀᴛᴇᴅ ʙᴏᴛ</b></blockquote>

<blockquote>
<b>👤 ɴᴀᴍᴇ :</b> {user.mention_html()}
<b>🆔 ᴜsᴇʀ ɪᴅ :</b> <code>{user.id}</code>
<b>🔗 ᴜsᴇʀɴᴀᴍᴇ :</b> @{user.username if user.username else 'No Username'}
</blockquote>
"""
            await context.bot.send_message(chat_id=logger_id, text=log_msg, parse_mode=ParseMode.HTML)
        except: pass
            
    # Buttons
    keyboard = [
        [InlineKeyboardButton("➕ Add Me To Your Group ➕", url=f"https://t.me/{bot_username}?startgroup=true")],
        [InlineKeyboardButton("📚 Help Commands", callback_data="help_main")],
        [InlineKeyboardButton("📢 Update", url=UPDATE_CHANNEL), InlineKeyboardButton("🚑 Support", url=GROUP_LINK)],
        [InlineKeyboardButton(f"📸 Follow on {bot_name}", url=INSTAGRAM_LINK)],
        [InlineKeyboardButton("👑 Owner", url=f"tg://user?id={OWNER_ID}")]
    ]

    try:
        await update.message.reply_photo(
            photo=START_IMG,
            caption=caption,
            has_spoiler=True,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        print(f"Start Error: {e}")
        # Fallback
        await update.message.reply_photo(
            photo=START_IMG,
            caption=caption.replace("<pre>", "").replace("</pre>", ""),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=None
        )

    if is_new_user:
        await update.message.reply_text("🎉 **Welcome!** You received ₹500 Free Bonus!", parse_mode=ParseMode.MARKDOWN)

# --- CALLBACK HANDLER ---
async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    user = update.effective_user
    bot_username = context.bot.username
    bot_name = context.bot.first_name
    
    # 1. HELP MAIN
    if data == "help_main":
        caption = "📚 **MAIN MENU**\nSelect a category:"
        kb = [
            [InlineKeyboardButton("🏦 Bank", callback_data="help_bank"), InlineKeyboardButton("📊 Market", callback_data="help_market")],
            [InlineKeyboardButton("🎮 Games", callback_data="help_games"), InlineKeyboardButton("🛒 Shop", callback_data="help_shop")],
            [InlineKeyboardButton("👮 Admin", callback_data="help_admin"), InlineKeyboardButton("🔮 Extra", callback_data="help_next")],
            [InlineKeyboardButton("🔙 Back Home", callback_data="back_home")]
        ]
        await q.edit_message_caption(caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

    # 2. SUB MENUS
    elif data in ["help_bank", "help_market", "help_games", "help_shop", "help_admin", "help_next"]:
        text = "ℹ️ **Category Help**\nClick Back to go to menu."
        kb = [[InlineKeyboardButton("🔙 Back", callback_data="help_main")]]
        await q.edit_message_caption(caption=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

    # 3. BACK HOME
    elif data == "back_home":
        # ... (Same logic as above, just refreshing the start message)
        try:
            uptime = get_readable_time()
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
        except:
            uptime = "00:00:00"; cpu=0; ram=0; disk=0

        first_name = html.escape(user.first_name)
        caption = f"""┌────── ˹ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ˼─── ⏤‌‌●
┆◍ ʜєʏ, {first_name} 🥀
┆◍ ɪ ᴧϻ {context.bot.first_name}
└────────────────────•
<pre>
ɪ ᴀᴍ ᴛʜᴇ ᴍᴏsᴛ ᴀᴅᴠᴀɴᴄᴇᴅ ᴍᴜʟᴛɪ-ᴘᴜʀᴘᴏsᴇ ʙᴏᴛ. 
ɪ ᴏғғᴇʀ ʜɪɢʜ-ǫᴜᴀʟɪᴛʏ ᴍᴜsɪᴄ, ɢʟᴏʙᴀʟ ᴇᴄᴏɴᴏᴍʏ
ᴀɪ ᴄʜᴀᴛ & ɢʀᴏᴜᴘ sᴇᴄᴜʀɪᴛʏ.
<pre>
<pre>
╭─ ⚙️ SYSTEM STATUS
│ ➥ UPTIME: {uptime}
│ ➥ SERVER STORAGE: {disk:.1f}%
│ ➥ CPU LOAD: {cpu:.1f}%
│ ➥ RAM CONSUMPTION: {ram:.1f}%
╰───────────────
</pre>
•──────────────────────•
<pre>
✦ᴘᴏᴡєʀєᴅ ʙʏ » BOSS JI 
<pre>
"""
        keyboard = [
            [InlineKeyboardButton("➕ Add Me To Your Group ➕", url=f"https://t.me/{bot_username}?startgroup=true")],
            [InlineKeyboardButton("📚 Help Commands", callback_data="help_main")],
            [InlineKeyboardButton("📢 Update", url=UPDATE_CHANNEL), InlineKeyboardButton("🚑 Support", url=GROUP_LINK)],
            [InlineKeyboardButton(f"📸 Follow on {bot_name}", url=INSTAGRAM_LINK)],
            [InlineKeyboardButton("👑 Owner", url=f"tg://user?id={OWNER_ID}")]
        ]
        await q.edit_message_caption(caption=caption, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)
        
