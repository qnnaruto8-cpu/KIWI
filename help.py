from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

# --- MAIN HELP COMMAND ---
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📚 **HELP MENU**\n\n"
        "Select a category below to see available commands:"
    )

    kb = [
        [
            InlineKeyboardButton("🏦 Bank & Economy", callback_data="help_bank"),
            InlineKeyboardButton("🎮 Games & Activity", callback_data="help_game")
        ],
        [
            InlineKeyboardButton("🔫 Crime & RPG", callback_data="help_crime"),
            InlineKeyboardButton("📈 Market & Stats", callback_data="help_market")
        ],
        [
            InlineKeyboardButton("🛒 Shop & Extras", callback_data="help_shop"),
            InlineKeyboardButton("🛠 Group Tools", callback_data="help_tools")
        ],
        [
            InlineKeyboardButton("👮 Admin Only", callback_data="help_admin")
        ],
        [
            InlineKeyboardButton("❌ Close", callback_data="close_help")
        ]
    ]

    if update.callback_query:
        q = update.callback_query
        await q.answer()
        await q.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode=ParseMode.MARKDOWN
        )


# --- CALLBACK HANDLER FOR HELP BUTTONS ---
async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    # ❌ Close help
    if data == "close_help":
        await q.message.delete()
        return

    # 🔙 Back to main help menu
    if data == "help_home":
        await help_command(update, context)
        return

    # 🏦 BANK
    if data == "help_bank":
        text = (
            "🏦 **BANKING & ECONOMY**\n\n"
            "• `/bal` - Check Wallet Balance\n"
            "• `/bank` - Check Bank Account\n"
            "• `/deposit <amount>` - Save Money in Bank\n"
            "• `/withdraw <amount>` - Withdraw Cash\n"
            "• `/loan <amount>` - Take Loan from Bank\n"
            "• `/payloan <amount>` - Repay Bank Loan"
        )

    # 🎮 GAMES
    elif data == "help_game":
        text = (
            "🎮 **GAMES & ACTIVITY**\n\n"
            "• `/bet <amount>` - Play Mines\n"
            "• `/new` - Start WordSeek Game\n"
            "• `/wrank` - WordSeek Leaderboard\n"
            "• `/crank` - Chat Message Ranking"
        )

    # 🔫 CRIME
    elif data == "help_crime":
        text = (
            "🔫 **CRIME & RPG**\n\n"
            "• `/rob` - Rob a user (Reply)\n"
            "• `/kill` - Kill a user (Reply)\n"
            "• `/pay <amount>` - Give Money\n"
            "• `/protect` - Buy Shield (24h)\n"
            "• `/alive` - Check Life Status"
        )

    # 📈 MARKET
    elif data == "help_market":
        text = (
            "📈 **MARKET & STATS**\n\n"
            "• `/market` - Group Share Prices\n"
            "• `/invest <group_id> <amount>` - Buy Shares\n"
            "• `/sell <group_id>` - Sell Shares\n"
            "• `/ranking` - Top Groups\n"
            "• `/top` - Global Rich List"
        )

    # 🛒 SHOP
    elif data == "help_shop":
        text = (
            "🛒 **SHOP & EXTRAS**\n\n"
            "• `/shop` - Buy VIP Titles\n"
            "• `/redeem <code>` - Claim Promo Code\n"
            "• `/id` - Get User / Group ID\n"
            "• `/ping` - Bot Speed\n"
            "• `/stats` - Bot Statistics"
        )

    # 🛠 TOOLS
    elif data == "help_tools":
        text = (
            "🛠 **GROUP ADMIN TOOLS** _(Use . or /)_\n\n"
            "• `.warn` / `.unwarn`\n"
            "• `.mute` / `.unmute`\n"
            "• `.ban` / `.unban`\n"
            "• `.kick`\n"
            "• `.pin` / `.d`"
        )

    # 👮 ADMIN
    elif data == "help_admin":
        text = (
            "👮 **OWNER COMMANDS**\n\n"
            "• `/admin` - Open Control Panel\n"
            "• `/restart` - Restart Bot\n"
            "• `/stats` - Database Stats\n"
            "• `/ping` - System Status"
        )

    else:
        return

    kb = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="help_home")]]

    await q.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode=ParseMode.MARKDOWN
    )