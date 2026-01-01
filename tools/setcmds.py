from telegram import Update, BotCommand
from telegram.ext import ContextTypes, CommandHandler
from config import OWNER_ID

# --- 1. SUDO USERS (Sirf tum aur Owner) ---
# 6356015122 = Tumhara ID
SUDO_USERS = [6356015122, int(OWNER_ID)]

# --- 2. SMALL CAPS CONVERTER ---
def to_small_caps(text):
    mapping = {
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ꜰ', 'g': 'ɢ', 'h': 'ʜ', 'i': 'ɪ',
        'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ',
        's': 's', 't': 'ᴛ', 'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ',
        ' ': ' '
    }
    # Sirf letters convert karega, baaki same rakhega
    return "".join(mapping.get(char.lower(), char) for char in text)

# --- 3. COMMAND LIST (Raw Text) ---
# Yahan normal English likho, code apne aap usse Design mein badal dega
RAW_COMMANDS = [
    # General
    ("start", "start the bot"),
    ("help", "get help menu"),
    ("ping", "check ping"),
    ("stats", "check stats"),
    
    # Music
    ("play", "play music"),
    ("vplay", "play video"),
    ("pause", "pause stream"),
    ("resume", "resume stream"),
    ("skip", "skip song"),
    ("stop", "stop stream"),
    ("queue", "show queue"),
    
    # Admin Tools
    ("admin", "admin list"),
    ("bots", "bot list"),
    ("ban", "ban user"),
    ("unban", "unban user"),
    ("mute", "mute user"),
    ("unmute", "unmute user"),
    ("tmute", "temp mute"),
    ("pin", "pin message"),
    ("unpin", "unpin message"),
    ("unpinall", "clear pins"),
    
    # Settings & Filters
    ("filter", "save filter"),
    ("stop", "delete filter"),
    ("filters", "list filters"),
    ("admincmd", "admin mode on/off"),
    
    # Auth
    ("auth", "add auth user"),
    ("unauth", "remove auth"),
    ("authlist", "check auth list"),
    
    # Broadcast
    ("broadcast", "broadcast dm"),
    ("broadcastgc", "broadcast groups"),
]

# --- 4. THE MAIN COMMAND (/setcmd) ---
async def set_commands_manually(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Sudo Check
    if user.id not in SUDO_USERS:
        return await update.message.reply_text("❌ **ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ!**")

    status = await update.message.reply_text("🔄 **ᴜᴘᴅᴀᴛɪɴɢ ʙᴏᴛ ᴍᴇɴᴜ...**")

    # List ko convert kar rahe hain Design mein
    final_commands = []
    for cmd, desc in RAW_COMMANDS:
        # Description ko Small Caps mein badal diya
        styled_desc = to_small_caps(desc)
        final_commands.append(BotCommand(cmd, styled_desc))

    try:
        # Telegram Server par bhejo
        await context.bot.set_my_commands(final_commands)
        await status.edit_text("✅ **ᴍᴇɴᴜ ʙᴜᴛᴛᴏɴ ᴜᴘᴅᴀᴛᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ!**\nRestart your Telegram app to see changes.")
    except Exception as e:
        await status.edit_text(f"❌ **Error:** {e}")

# --- REGISTER HANDLER ---
def register_handlers(app):
    app.add_handler(CommandHandler("setcmd", set_commands_manually))
    print("  ✅ SetCmd Module Loaded!")
