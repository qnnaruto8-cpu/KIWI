import time
import psutil
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from database import check_registered, register_user
from config import OWNER_ID, OWNER_NAME # Make sure OWNER_NAME config.py me ho

# --- GLOBAL VARS ---
START_IMG = "https://i.ibb.co/WLB2B31/1000007092.png" 
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
    bot_name = context.bot.first_name
    bot_username = context.bot.username
    
    # --- 1. SYSTEM STATS ---
    uptime = get_readable_time()
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    # --- 2. AUTO REGISTRATION LOGIC ---
    is_new_user = False
    if not check_registered(user.id):
        register_user(user.id, user.first_name)
        is_new_user = True

    # --- 3. STYLISH CAPTION ---
    # Owner Name Link (Blue Color in Telegram)
    owner_link = f"[{OWNER_NAME}](tg://user?id={OWNER_ID})"

    caption = f"""┌────── ˹ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ˼─── ⏤‌‌●
┆◍ ʜєʏ, {user.first_name} 🥀
┆◍ ɪ ᴧϻ {bot_name}
└────────────────────•
ɪ ᴀᴍ ᴛʜᴇ ғᴀsᴛᴇsᴛ ᴀɴᴅ ᴘᴏᴡᴇʀғᴜʟ ᴇᴄᴏɴᴏᴍʏ & ᴀɪ ʙᴏᴛ ᴡɪᴛʜ sᴏᴍᴇ ᴀᴡᴇsᴏᴍᴇ ғᴇᴀᴛᴜʀᴇs.

➥ᴜᴘᴛɪᴍᴇ: `{uptime}`
➥sᴇʀᴠᴇʀ sᴛᴏʀᴀɢᴇ: `{disk}%`
➥ᴄᴘᴜ ʟᴏᴀᴅ: `{cpu}%`
➥ʀᴀᴍ ᴄᴏɴsᴜᴍᴘᴛɪᴏɴ: `{ram}%`
•──────────────────────•
✦ᴘᴏᴡєʀєᴅ ʙʏ » {owner_link}"""

    # --- 4. BUTTONS ---
    keyboard = [
        [
            InlineKeyboardButton("💬 Chat AI", callback_data="start_chat_ai"),
            InlineKeyboardButton("🚑 Support", url=f"tg://user?id={OWNER_ID}")
        ],
        [
            InlineKeyboardButton("👑 Owner", url=f"tg://user?id={OWNER_ID}"),
            InlineKeyboardButton("📚 Help & Menu", callback_data="help_main")
        ],
        [
            InlineKeyboardButton("➕ Add Me To Your Group ➕", url=f"https://t.me/{bot_username}?startgroup=true")
        ]
    ]

    # Main Photo Bhejo
    await update.message.reply_photo(
        photo=START_IMG,
        caption=caption,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

    # --- 5. BONUS MESSAGE (Only for New Users) ---
    if is_new_user:
        await update.message.reply_text(
            f"🎉 **Welcome {user.first_name}!**\n"
            f"✅ Account Created Successfully.\n"
            f"💰 **You received ₹500 Free Bonus!**",
            parse_mode=ParseMode.MARKDOWN
        )

# --- CALLBACK HANDLER (MENU LOGIC - Same as before) ---
async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data
    user = update.effective_user
    
    # 1. HELP MAIN MENU
    if data == "help_main":
        caption = (
            f"📚 **MAIN MENU**\n"
            f"Select a category to see commands:\n\n"
            f"🏦 **Bank:** Deposit, Withdraw, Loans\n"
            f"📈 **Market:** Invest, Sell, Ranking\n"
            f"🎮 **Games:** Mines, Betting\n"
            f"🛒 **Shop:** Buy VIP, Items"
        )
        kb = [
            [InlineKeyboardButton("🏦 Bank", callback_data="help_bank"), InlineKeyboardButton("📈 Market", callback_data="help_market")],
            [InlineKeyboardButton("🎮 Games", callback_data="help_games"), InlineKeyboardButton("🛒 Shop", callback_data="help_shop")],
            [InlineKeyboardButton("➡️ Next Page", callback_data="help_next")],
            [InlineKeyboardButton("🔙 Back Home", callback_data="back_home")]
        ]
        await q.edit_message_caption(caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

    # 2. SUB MENUS
    elif data == "help_bank":
        text = (
            "🏦 **BANKING SYSTEM**\n\n"
            "• `/balance` - Check wallet\n"
            "• `/bank` - Check bank account\n"
            "• `/deposit [amount]` - Save money\n"
            "• `/withdraw [amount]` - Get cash\n"
            "• `/loan` - Take loan\n"
            "• `/payloan` - Repay loan"
        )
        kb = [[InlineKeyboardButton("🔙 Back", callback_data="help_main")]]
        await q.edit_message_caption(caption=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

    elif data == "help_market":
        text = (
            "📈 **STOCK MARKET**\n\n"
            "• `/market` - View Share Prices\n"
            "• `/invest [group_id] [amount]` - Buy Shares\n"
            "• `/sell [group_id]` - Sell Shares\n"
            "• `/ranking` - Top Groups"
        )
        kb = [[InlineKeyboardButton("🔙 Back", callback_data="help_main")]]
        await q.edit_message_caption(caption=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

    elif data == "help_games":
        text = (
            "🎮 **GAMES & CASINO**\n\n"
            "• `/bet [amount]` - Play Mines 💣\n"
            "• `/rob` - Rob someone (Reply)\n"
            "• `/kill` - Kill someone (Reply)\n"
            "• `/pay [amount]` - Give money"
        )
        kb = [[InlineKeyboardButton("🔙 Back", callback_data="help_main")]]
        await q.edit_message_caption(caption=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
    
    elif data == "help_shop":
        text = (
            "🛒 **VIP SHOP**\n\n"
            "• `/shop` - Open Shop Menu\n"
            "• `/redeem [code]` - Get Free Money\n"
            "• `/protect` - Buy Shield (24h)"
        )
        kb = [[InlineKeyboardButton("🔙 Back", callback_data="help_main")]]
        await q.edit_message_caption(caption=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

    elif data == "help_next":
        text = (
            "🔮 **EXTRA COMMANDS**\n\n"
            "• `/top` - Global Leaderboard\n"
            "• `/alive` - Check Health\n"
            "• `/eco` - Economy Status\n"
            "• `Hi Yuki` - Chat with AI"
        )
        kb = [[InlineKeyboardButton("🔙 Back", callback_data="help_main")]]
        await q.edit_message_caption(caption=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

    # 3. START CHAT (AI)
    elif data == "start_chat_ai":
        await q.answer("💬 AI Mode Active!", show_alert=False)
        await q.message.reply_text(f"Hey **{user.first_name}**! 👋\nBas **'Hi Yuki'** ya **'Hello'** likho, main turant reply karungi!")

    # 4. BACK HOME
    elif data == "back_home":
        # Owner Link Re-calculate for Back Home
        owner_link = f"[{OWNER_NAME}](tg://user?id={OWNER_ID})"
        
        # Stats recalculate (Optional, can keep old values to be fast)
        uptime = get_readable_time()
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent

        caption = f"""┌────── ˹ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ˼─── ⏤‌‌●
┆◍ ʜєʏ, {user.first_name} 🥀
┆◍ ɪ ᴧϻ {context.bot.first_name}
└────────────────────•
ɪ ᴀᴍ ᴛʜᴇ ғᴀsᴛᴇsᴛ ᴀɴᴅ ᴘᴏᴡᴇʀғᴜʟ ᴇᴄᴏɴᴏᴍʏ & ᴀɪ ʙᴏᴛ ᴡɪᴛʜ sᴏᴍᴇ ᴀᴡᴇsᴏᴍᴇ ғᴇᴀᴛᴜʀᴇs.

➥ᴜᴘᴛɪᴍᴇ: `{uptime}`
➥sᴇʀᴠᴇʀ sᴛᴏʀᴀɢᴇ: `{disk}%`
➥ᴄᴘᴜ ʟᴏᴀᴅ: `{cpu}%`
➥ʀᴀᴍ ᴄᴏɴsᴜᴍᴘᴛɪᴏɴ: `{ram}%`
•──────────────────────•
✦ᴘᴏᴡєʀєᴅ ʙʏ » {owner_link}"""

        keyboard = [
            [InlineKeyboardButton("💬 Chat AI", callback_data="start_chat_ai"), InlineKeyboardButton("🚑 Support", url="https://t.me/+N08m5L1mCTU2NTE1")],
            [InlineKeyboardButton("👑 Owner", url=f"tg://user?id={OWNER_ID}"), InlineKeyboardButton("📚 Help & Menu", callback_data="help_main")],
            [InlineKeyboardButton("➕ Add Me To Your Group ➕", url=f"https://t.me/{context.bot.username}?startgroup=true")]
        ]
        # Use edit_message_media if changing image, else edit_caption
        # Assuming image is same, just caption update
        await q.edit_message_caption(caption=caption, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)
