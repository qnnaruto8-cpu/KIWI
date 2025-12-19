from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📚 **COMMANDS**\n"
        "🎮 `/bet 100` - Play Mines\n"
        "🏆 `/top` - Rich List (Leaderboard)\n"
        "🏢 `/ranking` - Group Market\n"
        "🛒 `/shop` - Buy VIP Titles\n"
        "💰 `/balance` - Check Money\n"
        "📈 `/market` - Check Share Price\n"
        "🎁 `/redeem <code>` - Promo Code"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    
