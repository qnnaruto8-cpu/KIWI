from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📚 **COMMAND LIST**\n\n"
        
        "🎮 **GAME:**\n"
        "`/bet <amount>` - Play Mines (e.g. /bet 100)\n"
        "`/balance` - Check Paisa\n\n"
        
        "🔫 **CRIME & ECONOMY:**\n"
        "`/pay <amount>` - Paise bhejo (Reply to user)\n"
        "`/rob` - Chori karo (Reply to user)\n"
        "`/kill` - Supari do (Reply to user)\n"
        "`/protect` - Buy Shield (24 Hours)\n"
        "`/alive` - Check Shield & Status\n\n"
        
        "📈 **MARKET:**\n"
        "`/ranking` - Top Groups\n"
        "`/market` - Share Price\n"
        "`/invest <amount>` - Invest Karo\n"
        "`/sell` - Profit Book Karo\n\n"
        
        "🛒 **SHOP & EXTRAS:**\n"
        "`/shop` - VIP Titles\n"
        "`/top` - Leaderboard (Rich & Killers)\n"
        "`/redeem <code>` - Promo Code\n\n"
        
        "🔐 **ADMIN ONLY:**\n"
        "`/eco` - Economy ON/OFF\n"
        "`/reset` - Wipe Database (Danger)\n"
        "`/addkey <key>` - Add API Key\n"
        "`/delkey <key>` - Remove API Key\n"
        "`/keys` - Count Keys\n"
        "`/cast <msg>` - Broadcast\n"
        "`/code <name> <amt> <limit>` - Create Code\n"
        "`/add <id> <money>` - Give Money"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    
