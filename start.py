import time
import psutil
import asyncio
import html 
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

# 🔥 Database Imports
from database import check_registered, register_user, get_logger_group 
# ✅ FIX: Ab saare links Config se aayenge
from config import OWNER_ID, OWNER_NAME, GROUP_LINK, INSTAGRAM_LINK 
# 🔥 AI Chat Import
from ai_chat import get_mimi_sticker

# --- GLOBAL VARS ---
START_IMG = "https://i.ibb.co/8gW9bqTd/IMG-20251224-191812-875.jpg" 
BOT_START_TIME = time.time()
UPDATE_CHANNEL = "https://t.me/PRINCE_BOTS_UPDATES" 

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
    bot_name = context.bot.first_name
    bot_username = context.bot.username
    
    first_name = html.escape(user.first_name)
    
    # --- 1. ANIMATION SEQUENCE ---
    try:
        sticker_id = await get_mimi_sticker(context.bot)
        if sticker_id:
            stk = await update.message.reply_sticker(sticker=sticker_id)
            await asyncio.sleep(2)
            await stk.delete()
    except: pass 

    msg = await update.message.reply_text("🍭")
    await asyncio.sleep(0.5)
    
    # Loading Animation
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
    
    await asyncio.sleep(0.5)
    await msg.delete() 

    # --- 2. CAPTION SETUP ---
    try:
        uptime = get_readable_time()
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
    except:
        uptime = "00:00:00"; cpu=0; ram=0; disk=0

    owner_link = f"[{OWNER_NAME}](tg://user?id={OWNER_ID})"
    CodeBlock = "```"

    caption = f"""┌────── ˹ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ˼─── ⏤‌‌●
┆◍ ʜєʏ, {first_name} 🥀
┆◍ ɪ ᴧϻ {bot_name}
└────────────────────•
```
ɪ ᴀᴍ ᴛʜᴇ ᴍᴏsᴛ ᴀᴅᴠᴀɴᴄᴇᴅ ᴍᴜʟᴛɪ-ᴘᴜʀᴘᴏsᴇ ʙᴏᴛ. 
ɪ ᴏғғᴇʀ ʜɪɢʜ-ǫᴜᴀʟɪᴛʏ ᴍᴜsɪᴄ, ɢʟᴏʙᴀʟ ᴇᴄᴏɴᴏᴍʏ
ᴀɪ ᴄʜᴀᴛ & ɢʀᴏᴜᴘ sᴇᴄᴜʀɪᴛʏ.
```

```
╭─ ⚙️ SYSTEM STATUS
│ ➥ UPTIME: {uptime}
│ ➥ SERVER STORAGE: {disk:.1f}%
│ ➥ CPU LOAD: {cpu:.1f}%
│ ➥ RAM CONSUMPTION: {ram:.1f}%
╰───────────────
```
•──────────────────────•
```
✦ ᴘᴏᴡєʀєᴅ ʙʏ © BOSS JI
```
"""

    # --- 3. AUTO REGISTRATION & LOGGER ---
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
        except Exception as e:
            print(f"⚠️ Logger Error: {e}")
            
    # --- 🔥 BUTTONS LAYOUT 🔥 ---
    keyboard = [
        [
            InlineKeyboardButton("➕ Add Me To Your Group ➕", url=f"[https://t.me/](https://t.me/){bot_username}?startgroup=true")
        ],
        [
            InlineKeyboardButton("📚 Help Commands", callback_data="help_main")
        ],
        [
            InlineKeyboardButton("📢 Update", url=UPDATE_CHANNEL),
            # ✅ FIX: Ab ye Config se GROUP_LINK le raha hai
            InlineKeyboardButton("🚑 Support", url=GROUP_LINK) 
        ],
        [
            # ✅ NEW: Insta Button with Bot Name
            InlineKeyboardButton(f"📸 Follow on {bot_name}", url=INSTAGRAM_LINK)
        ],
        [
            InlineKeyboardButton("👑 Owner", url=f"tg://user?id={OWNER_ID}")
        ]
    ]

    # --- 5. SEND MESSAGE ---
    try:
        await update.message.reply_photo(
            photo=START_IMG,
            caption=caption,
            has_spoiler=True,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        print(f"Start Error: {e}")
        await update.message.reply_photo(
            photo=START_IMG,
            caption=caption.replace(CodeBlock, ""),
            has_spoiler=True,
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

    elif data == "start_chat_ai":
         await q.message.reply_text("Hi! I am AI.")

    # 3. BACK HOME
    elif data == "back_home":
        # Owner Link Markdown
        owner_link_md = f"[{OWNER_NAME}](tg://user?id={OWNER_ID})"
        
        try:
            uptime = get_readable_time()
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
        except:
            uptime = "00:00:00"; cpu=0; ram=0; disk=0

        CodeBlock = "```"
        first_name = html.escape(user.first_name)

        caption = f"""┌────── ˹ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ˼─── ⏤‌‌●
┆◍ ʜєʏ, {first_name} 🥀
┆◍ ɪ ᴧϻ {context.bot.first_name}
└────────────────────•
```
ɪ ᴀᴍ ᴛʜᴇ ᴍᴏsᴛ ᴀᴅᴠᴀɴᴄᴇᴅ ᴍᴜʟᴛɪ-ᴘᴜʀᴘᴏsᴇ ʙᴏᴛ. ɪ ᴏғғᴇʀ ʜɪɢʜ-ǫᴜᴀʟɪᴛʏ ᴍᴜsɪᴄ, ɢʟᴏʙᴀʟ ᴇᴄᴏɴᴏᴍʏ, ᴀɪ ᴄʜᴀᴛ & ɢʀᴏᴜᴘ sᴇᴄᴜʀɪᴛʏ.
```

```
╭─ ⚙️ SYSTEM STATUS
│ ➥ UPTIME: {uptime}
│ ➥ SERVER STORAGE: {disk:.1f}%
│ ➥ CPU LOAD: {cpu:.1f}%
│ ➥ RAM CONSUMPTION: {ram:.1f}%
╰───────────────
```
•──────────────────────•
```
✦ᴘᴏᴡєʀєᴅ ʙʏ » BOSS JI 
```
"""
        # ✅ FIX: Updated Keyboard here too
        keyboard = [
            [InlineKeyboardButton("➕ Add Me To Your Group ➕", url=f"https://t.me/{bot_username}?startgroup=true")],
            [InlineKeyboardButton("📚 Help Commands", callback_data="help_main")],
            [InlineKeyboardButton("📢 Update", url=UPDATE_CHANNEL), InlineKeyboardButton("🚑 Support", url=GROUP_LINK)],
            [InlineKeyboardButton(f"📸 Follow on {bot_name}", url=INSTAGRAM_LINK)],
            [InlineKeyboardButton("👑 Owner", url=f"tg://user?id={OWNER_ID}")]
        ]
        
        await q.edit_message_caption(caption=caption, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)
        
