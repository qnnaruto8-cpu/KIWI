
from telegram import Update
from telegram.ext import ContextTypes, ApplicationHandlerStop
from config import OWNER_ID
# Note: get_maintenance_data naya function import kiya hai
from tools.database import get_maintenance_data, set_maintenance

# --- VARIABLES ---
MAINTENANCE_MODE = False

# Default Message (Small Caps Style)
DEFAULT_MSG = "sᴏʀʀʏ, ʙᴏᴛ ɪs ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ.\nᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ."
CURRENT_MSG = DEFAULT_MSG

# 🔥 NEW: Dusra Admin ID (Tumhari ID)
CO_OWNER_ID = 6356015122

# --- SMALL CAPS CONVERTER ---
def make_small_caps(text):
    mapping = str.maketrans(
        "abcdefghijklmnopqrstuvwxyz", 
        "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"
    )
    return text.lower().translate(mapping)

# --- SYNC FUNCTION (Startup ke liye) ---
async def sync_maintenance():
    global MAINTENANCE_MODE, CURRENT_MSG
    
    data = await get_maintenance_data()
    MAINTENANCE_MODE = data.get("state", False)
    
    # Agar database me custom message hai to wo load karo, nahi to Default
    saved_msg = data.get("message")
    if saved_msg:
        CURRENT_MSG = saved_msg
    else:
        CURRENT_MSG = DEFAULT_MSG
        
    print(f"🔧 Maintenance: {MAINTENANCE_MODE} | Msg: {CURRENT_MSG}")

# --- 1. GATEKEEPER (USER BLOCKER) ---
async def maintenance_gatekeeper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global MAINTENANCE_MODE, CURRENT_MSG
    
    if not MAINTENANCE_MODE:
        return

    user = update.effective_user
    if not user:
        return

    # 🔥 Owner OR Co-Owner Access
    if user.id == OWNER_ID or user.id == CO_OWNER_ID:
        return

    if update.message:
        # User ko Current Message bhejo (Small Caps)
        await update.message.reply_text(f"**🚧 {CURRENT_MSG}**", parse_mode="Markdown")
    
    elif update.callback_query:
        await update.callback_query.answer("🚧 ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ ɪs ᴏɴ!", show_alert=True)

    raise ApplicationHandlerStop

# --- 2. COMMAND HANDLER ---
async def maintenance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global MAINTENANCE_MODE, CURRENT_MSG
    
    user = update.effective_user
    
    # 🔥 Sirf Owner OR Co-Owner
    if user.id != OWNER_ID and user.id != CO_OWNER_ID:
        return

    if not context.args:
        # Help Message in Small Caps
        txt = (
            "⚠️ **ᴜsᴀɢᴇ:**\n"
            "`/maintenance on` (ᴅᴇꜰᴀᴜʟᴛ ᴍsɢ)\n"
            "`/maintenance on Server Update` (ᴄᴜsᴛᴏᴍ ᴍsɢ)\n"
            "`/maintenance off`"
        )
        await update.message.reply_text(txt)
        return

    action = context.args[0].lower()
    
    if action == "on":
        MAINTENANCE_MODE = True
        
        # Check karo agar user ne msg diya hai
        if len(context.args) > 1:
            raw_text = " ".join(context.args[1:]) 
            CURRENT_MSG = make_small_caps(raw_text) # Custom Msg Convert
        else:
            CURRENT_MSG = DEFAULT_MSG # Default Msg
            
        # Database me save karo
        await set_maintenance(True, CURRENT_MSG)
        
        await update.message.reply_text(f"✅ **ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴏɴ!**\n\n💬 **ᴍᴇssᴀɢᴇ:**\n{CURRENT_MSG}")
        
    elif action == "off":
        MAINTENANCE_MODE = False
        await set_maintenance(False, None) # DB update
        await update.message.reply_text("✅ **ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴅɪsᴀʙʟᴇᴅ!**\nʙᴏᴛ ɪs ʟɪᴠᴇ.")
    else:
        await update.message.reply_text("❌ ᴜsᴇ `on` ᴏʀ `off`.")
        
