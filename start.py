import time
import psutil
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from database import check_registered, register_user
from config import OWNER_ID, OWNER_NAME
from ai_chat import get_mimi_sticker

# --- GLOBAL VARS ---
START_IMG = "https://i.ibb.co/WLB2B31/1000007092.png" 
BOT_START_TIME = time.time()
SUPPORT_LINK = "https://t.me/+N08m5L1mCTU2NTE1"

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
    
    # --- 1. ANIMATION SEQUENCE ---
    try:
        sticker_id = await get_mimi_sticker(context.bot)
        if sticker_id:
            stk = await update.message.reply_sticker(sticker=sticker_id)
            await asyncio.sleep(2) 
            await stk.delete()
    except: pass 

    msg = await update.message.reply_text("⚡")
    await asyncio.sleep(0.5)
    
    # Loading Animation
    bars = [
        "⚡ ʟᴏᴀᴅɪɴɢ █▒▒▒▒",
        "⚡ ʟᴏᴀᴅɪɴɢ ███▒▒",
        "⚡ ʟᴏᴀᴅɪɴɢ █████",
        "✨ ᴄᴏᴍᴘʟᴇᴛᴇᴅ!"
    ]
    for bar in bars:
        try:
            await msg.edit_text(bar)
            await asyncio.sleep(0.3)
        except: pass
    
    await msg.delete()

    # --- 2. SYSTEM STATS ---
    try:
        uptime = get_readable_time()
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
    except:
        uptime = "00:00:00"; cpu=0; ram=0; disk=0

    owner_link = f"[{OWNER_NAME}](tg://user?id={OWNER_ID})"

    caption = f"""┌────── ˹ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ˼─── ⏤‌‌●
┆◍ ʜєʏ, {user.first_name} 🥀
┆◍ ɪ ᴧϻ {bot_name}
└────────────────────•
```
ɪ ᴀᴍ ᴛʜᴇ ғᴀsᴛᴇsᴛ ᴀɴᴅ ᴘᴏᴡᴇʀғᴜʟ ᴇᴄᴏɴᴏᴍʏ & ᴀɪ ʙᴏᴛ ᴡɪᴛʜ sᴏᴍᴇ ᴀᴡᴇsᴏᴍᴇ ғᴇᴀᴛᴜʀᴇs.
'''

```
╭─ ⚙️ SYSTEM STATUS
│ ➥ UPTIME: {uptime}
│ ➥ STORAGE: {disk:.1f}%
│ ➥ CPU LOAD: {cpu:.1f}%
│ ➥ RAM USAGE: {ram:.1f}%
╰───────────────
```
•──────────────────────•
✦ ᴘᴏᴡєʀєᴅ ʙʏ » {owner_link}
"""

    # --- 3. AUTO REGISTER ---
    is_new = False
    if not check_registered(user.id):
        register_user(user.id, user.first_name)
        is_new = True

    # --- 4. BUTTONS (Renamed to st_ to avoid conflict) ---
    keyboard = [
        [
            InlineKeyboardButton("💬 Chat AI", callback_data="start_chat_ai"),
            InlineKeyboardButton("📊 Ranking", callback_data="st_market") 
        ],
        [
            InlineKeyboardButton("🎮 Games", callback_data="st_games"),
            InlineKeyboardButton("🛒 VIP Shop", callback_data="st_shop")
        ],
        [
            InlineKeyboardButton("🚑 Support", url=SUPPORT_LINK),
            InlineKeyboardButton("📚 Commands", callback_data="st_main")
        ],
        [
            InlineKeyboardButton("➕ Add Me To Your Group ➕", url=f"https://t.me/{bot_username}?startgroup=true")
        ]
    ]

    await update.message.reply_photo(
        photo=START_IMG,
        caption=caption,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

    if is_new:
        await update.message.reply_text(f"🎉 **Welcome {user.first_name}!**\n💰 Bonus: ₹500 added!")

# --- CALLBACK HANDLER ---
async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer() # Mandatory
    data = q.data
    user = update.effective_user
    
    # 1. MAIN COMMANDS MENU
    if data == "st_main":
        caption = (
            f"📚 **MAIN MENU**\n"
            f"Select a category:\n\n"
            f"🏦 **Bank:** Deposit, Withdraw\n"
            f"📈 **Market:** Invest, Sell\n"
            f"🎮 **Games:** Betting, WordSeek\n"
            f"🛒 **Shop:** VIP, Items\n"
            f"👮 **Admin:** Warn, Ban, Mute"
        )
        kb = [
            [InlineKeyboardButton("🏦 Bank", callback_data="st_bank"), InlineKeyboardButton("📊 Market", callback_data="st_market")],
            [InlineKeyboardButton("🎮 Games", callback_data="st_games"), InlineKeyboardButton("🛒 Shop", callback_data="st_shop")],
            [InlineKeyboardButton("👮 Admin", callback_data="st_admin"), InlineKeyboardButton("🔮 Extra", callback_data="st_extra")],
            [InlineKeyboardButton("🔙 Back Home", callback_data="back_home")]
        ]
        await q.edit_message_caption(caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

    # 2. SUB MENUS
    elif data == "st_bank":
        text = "🏦 **BANKING**\n\n`/balance` - Check Money\n`/bank` - Bank Account\n`/deposit` - Save Money\n`/withdraw` - Get Cash\n`/loan` - Take Loan\n`/payloan` - Repay Loan"
        kb = [[InlineKeyboardButton("🔙 Back", callback_data="st_main")]]
        await q.edit_message_caption(caption=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

    elif data == "st_market":
        text = "📊 **MARKET**\n\n`/crank` - Chat Rank\n`/top` - Global Rank\n`/market` - Shares\n`/invest` - Buy Shares\n`/topinvest` - Top Investors\n`/sell` - Sell Shares"
        kb = [[InlineKeyboardButton("🔙 Back", callback_data="st_main")]]
        await q.edit_message_caption(caption=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

    elif data == "st_games":
        text = "🎮 **GAMES**\n\n`/new` - WordSeek Game\n`/bet` - Play Mines\n`/rob` - Rob User\n`/kill` - Kill User\n`/pay` - Transfer Money"
        kb = [[InlineKeyboardButton("🔙 Back", callback_data="st_main")]]
        await q.edit_message_caption(caption=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
    
    elif data == "st_shop":
        text = "🛒 **SHOP**\n\n`/shop` - VIP Menu\n`/redeem` - Promo Code\n`/protect` - Buy Shield"
        kb = [[InlineKeyboardButton("🔙 Back", callback_data="st_main")]]
        await q.edit_message_caption(caption=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

    elif data == "st_admin":
        text = "👮 **ADMIN TOOLS**\n\n`.warn` / `.unwarn`\n`.mute` / `.unmute`\n`.ban` / `.unban`\n`.kick`\n`.pin` / `.unpin`\n`.title`\n`.promote` / `.demote`"
        kb = [[InlineKeyboardButton("🔙 Back", callback_data="st_main")]]
        await q.edit_message_caption(caption=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

    elif data == "st_extra":
        text = "🔮 **EXTRA**\n\n`/alive` - Health Check\n`/eco` - Economy Stats\n`Hi Mimi` - AI Chat"
        kb = [[InlineKeyboardButton("🔙 Back", callback_data="st_main")]]
        await q.edit_message_caption(caption=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

    # 3. AI CHAT TOGGLE
    elif data == "start_chat_ai":
        await q.answer("💬 AI Mode Active!", show_alert=False)
        await q.message.reply_text(f"Hey **{user.first_name}**! 👋\nBas **'Mimi'** ya **'Hello'** likho, main reply karungi!")

    # 4. BACK HOME
    elif data == "back_home":
        owner_link = f"[{OWNER_NAME}](tg://user?id={OWNER_ID})"
        try:
            uptime = get_readable_time()
            cpu = psutil.cpu_percent()
            disk = psutil.disk_usage('/').percent
        except: uptime="00:00:00"; cpu=0; disk=0

        caption = f"""┌────── ˹ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ˼─── ⏤‌‌●
┆◍ ʜєʏ, {user.first_name} 🥀
┆◍ ɪ ᴧϻ {context.bot.first_name}
└────────────────────•
```
╭─ ⚙️ SYSTEM STATUS
│ ➥ UPTIME: {uptime}
│ ➥ STORAGE: {disk:.1f}%
│ ➥ CPU LOAD: {cpu:.1f}%
╰───────────────
```
•──────────────────────•
✦ ᴘᴏᴡєʀєᴅ ʙʏ » {owner_link}"""

        kb = [
            [InlineKeyboardButton("💬 Chat AI", callback_data="start_chat_ai"), InlineKeyboardButton("📊 Ranking", callback_data="st_market")],
            [InlineKeyboardButton("🎮 Games", callback_data="st_games"), InlineKeyboardButton("🛒 Shop", callback_data="st_shop")],
            [InlineKeyboardButton("🚑 Support", url=SUPPORT_LINK), InlineKeyboardButton("📚 Commands", callback_data="st_main")],
            [InlineKeyboardButton("➕ Add Me To Your Group ➕", url=f"https://t.me/{context.bot.username}?startgroup=true")]
        ]
        await q.edit_message_caption(caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)