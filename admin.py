import html
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from config import OWNER_IDS 
from database import (
    users_col, groups_col, codes_col, update_balance, 
    add_api_key, remove_api_key, get_all_keys,
    add_game_key, remove_game_key, get_game_keys,
    add_sticker_pack, remove_sticker_pack, get_sticker_packs,
    wipe_database, set_economy_status, get_economy_status,
    set_logger_group, delete_logger_group,
    # 👇 Naye Database Functions
    get_active_chat_model, set_active_chat_model,
    get_groq_api_key, set_groq_api_key
)

# Global State
ADMIN_INPUT_STATE = {} 

# Fancy Font Helper
def to_fancy(text):
    mapping = {'A': 'Λ', 'E': 'Є', 'S': 'δ', 'O': 'σ', 'T': 'ᴛ', 'N': 'ɴ', 'M': 'ᴍ', 'U': 'ᴜ', 'R': 'ʀ', 'D': 'ᴅ', 'C': 'ᴄ', 'P': 'ᴘ', 'G': 'ɢ', 'B': 'ʙ', 'L': 'ʟ', 'W': 'ᴡ', 'K': 'ᴋ', 'J': 'ᴊ', 'Y': 'ʏ', 'I': 'ɪ', 'H': 'ʜ'}
    return "".join(mapping.get(c.upper(), c) for c in text)

# --- 1. MAIN ADMIN PANEL ---
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in OWNER_IDS: 
        return

    if update.effective_user.id in ADMIN_INPUT_STATE:
        del ADMIN_INPUT_STATE[update.effective_user.id]
    
    eco_status = "🟢 ON" if get_economy_status() else "🔴 OFF"
    current_model = get_active_chat_model().upper() # GEMINI or GROQ
    chat_keys = len(get_all_keys())
    groq_status = "✅ SET" if get_groq_api_key() else "❌ NOT SET"
    game_keys = len(get_game_keys())
    stickers = len(get_sticker_packs())

    text = f"""
<blockquote><b>👮‍♂️ {to_fancy('ADMIN CONTROL PANEL')}</b></blockquote>

<blockquote>
<b>⚙️ ᴇᴄᴏɴᴏᴍʏ :</b> {eco_status}
<b>🤖 ᴍᴏᴅᴇʟ :</b> <code>{current_model}</code>
<b>💬 ᴄʜᴀᴛ ᴋᴇʏs :</b> {chat_keys}
<b>⚡ ɢʀᴏǫ ᴋᴇʏ :</b> {groq_status}
<b>🎮 ɢᴀᴍᴇ ᴋᴇʏs :</b> {game_keys}
<b>👻 sᴛɪᴄᴋᴇʀs :</b> {stickers}
</blockquote>

<blockquote>👇 <b>Select an action below:</b></blockquote>
"""

    kb = [
        [InlineKeyboardButton(f"Economy: {eco_status}", callback_data="admin_toggle_eco"),
         InlineKeyboardButton(f"Model: {current_model}", callback_data="admin_switch_model")],
        
        [InlineKeyboardButton("📢 Broadcast", callback_data="admin_cast_ask"), 
         InlineKeyboardButton("🎁 Create Code", callback_data="admin_code_ask")],
        
        [InlineKeyboardButton("💰 Add Money", callback_data="admin_add_ask"), 
         InlineKeyboardButton("💸 Take Money", callback_data="admin_take_ask")],
        
        # Keys Management
        [InlineKeyboardButton("🔑 Gemini Keys", callback_data="admin_chat_keys_menu"), 
         InlineKeyboardButton("⚡ Groq Key", callback_data="admin_groq_menu")],
        
        [InlineKeyboardButton("🎮 Game Keys", callback_data="admin_game_keys_menu"),
         InlineKeyboardButton("👻 Stickers", callback_data="admin_stickers_menu")],
        
        # Logger
        [InlineKeyboardButton("📝 Logger Settings", callback_data="admin_logger_menu")],
        
        [InlineKeyboardButton("☢️ WIPE DATA", callback_data="admin_wipe_ask"), 
         InlineKeyboardButton("❌ Close", callback_data="admin_close")]
    ]
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)

# --- 2. CALLBACK HANDLER ---
async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data
    user_id = q.from_user.id
    
    if user_id not in OWNER_IDS:
        await q.answer("❌ Only Owner can use this!", show_alert=True)
        return

    # --- MODEL SWITCHER ---
    if data == "admin_switch_model":
        new_model = "groq" if get_active_chat_model() == "gemini" else "gemini"
        set_active_chat_model(new_model)
        await q.answer(f"🚀 Model Switched to {new_model.upper()}!")
        await admin_panel(update, context)
        return

    # --- GROQ MENU ---
    if data == "admin_groq_menu":
        kb = [
            [InlineKeyboardButton("➕ Set Groq Key", callback_data="admin_groq_set")],
            [InlineKeyboardButton("🗑 Delete Groq Key", callback_data="admin_groq_del")],
            [InlineKeyboardButton("🔙 Back", callback_data="admin_back")]
        ]
        status = "<code>SET</code>" if get_groq_api_key() else "<code>NOT SET</code>"
        msg = f"<blockquote><b>⚡ {to_fancy('GROQ API SETTINGS')}</b></blockquote>\n\nStatus: {status}"
        await q.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)
        return

    # --- Gemini Keys Menu ---
    if data == "admin_chat_keys_menu":
        kb = [[InlineKeyboardButton("➕ Add Key", callback_data="admin_key_add")], 
              [InlineKeyboardButton("➖ Del Key", callback_data="admin_key_del")], 
              [InlineKeyboardButton("🔙 Back", callback_data="admin_back")]]
        msg = f"<blockquote><b>🔑 {to_fancy('GEMINI API KEYS')}</b></blockquote>"
        await q.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)
        return

    # --- Game Keys Menu ---
    if data == "admin_game_keys_menu":
        kb = [[InlineKeyboardButton("➕ Add Key", callback_data="admin_game_key_add")], 
              [InlineKeyboardButton("➖ Del Key", callback_data="admin_game_key_del")], 
              [InlineKeyboardButton("🔙 Back", callback_data="admin_back")]]
        msg = f"<blockquote><b>🎮 {to_fancy('GAME API KEYS')} (WordSeek)</b></blockquote>"
        await q.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)
        return

    # --- Stickers Menu ---
    if data == "admin_stickers_menu":
        kb = [[InlineKeyboardButton("➕ Add Pack", callback_data="admin_pack_add")], 
              [InlineKeyboardButton("➖ Del Pack", callback_data="admin_pack_del")], 
              [InlineKeyboardButton("🔙 Back", callback_data="admin_back")]]
        msg = f"<blockquote><b>👻 {to_fancy('STICKER PACKS')}</b></blockquote>"
        await q.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)
        return

    # --- Logger Menu ---
    if data == "admin_logger_menu":
        kb = [[InlineKeyboardButton("📝 Set Logger", callback_data="admin_set_logger")], 
              [InlineKeyboardButton("🗑 Del Logger", callback_data="admin_del_logger")], 
              [InlineKeyboardButton("🔙 Back", callback_data="admin_back")]]
        msg = f"<blockquote><b>📝 {to_fancy('LOGGER SETTINGS')}</b></blockquote>"
        await q.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)
        return

    # --- INPUT TRIGGERS (ADD & DELETE) ---
    
    # 1. Chat Keys
    if data == "admin_key_add":
        ADMIN_INPUT_STATE[user_id] = 'add_key'
        await q.edit_message_text(f"<blockquote>➕ <b>Send Gemini API Key:</b></blockquote>", parse_mode=ParseMode.HTML)
        return
    elif data == "admin_key_del":
        ADMIN_INPUT_STATE[user_id] = 'del_key'
        keys = "\n".join([f"<code>{k}</code>" for k in get_all_keys()])
        msg = f"<blockquote>➖ <b>Send Chat Key to delete:</b></blockquote>\n\n{keys}"
        await q.edit_message_text(msg, parse_mode=ParseMode.HTML)
        return

    # 2. Game Keys
    elif data == "admin_game_key_add":
        ADMIN_INPUT_STATE[user_id] = 'add_game_key'
        await q.edit_message_text(f"<blockquote>🎮 <b>Send WordSeek API Key:</b></blockquote>", parse_mode=ParseMode.HTML)
        return
    elif data == "admin_game_key_del":
        ADMIN_INPUT_STATE[user_id] = 'del_game_key'
        keys = "\n".join([f"<code>{k}</code>" for k in get_game_keys()])
        msg = f"<blockquote>➖ <b>Send Game Key to delete:</b></blockquote>\n\n{keys}"
        await q.edit_message_text(msg, parse_mode=ParseMode.HTML)
        return

    # 3. Stickers
    elif data == "admin_pack_add":
        ADMIN_INPUT_STATE[user_id] = 'add_pack'
        await q.edit_message_text(f"<blockquote>👻 <b>Send Sticker Pack Name or Link:</b></blockquote>", parse_mode=ParseMode.HTML)
        return
    elif data == "admin_pack_del":
        ADMIN_INPUT_STATE[user_id] = 'del_pack'
        packs = "\n".join([f"<code>{p}</code>" for p in get_sticker_packs()])
        msg = f"<blockquote>➖ <b>Send Pack Name to delete:</b></blockquote>\n\n{packs}"
        await q.edit_message_text(msg, parse_mode=ParseMode.HTML)
        return

    # 4. Groq Keys
    elif data == "admin_groq_set":
        ADMIN_INPUT_STATE[user_id] = 'set_groq_key'
        await q.edit_message_text(f"<blockquote>⚡ <b>Send Groq API Key:</b>\n(Starts with <code>gsk_</code>)</blockquote>", parse_mode=ParseMode.HTML)
        return
    elif data == "admin_groq_del":
        set_groq_api_key(None)
        await q.answer("🗑 Groq Key Deleted!", show_alert=True)
        await admin_panel(update, context)
        return

    # 5. Others
    elif data == "admin_cast_ask":
        ADMIN_INPUT_STATE[user_id] = 'broadcast'
        await q.edit_message_text(f"<blockquote>📢 <b>Send anything to Broadcast (Text/Photo/Video):</b></blockquote>", parse_mode=ParseMode.HTML)
        return
    elif data == "admin_add_ask":
        ADMIN_INPUT_STATE[user_id] = 'add_money'
        await q.edit_message_text(f"<blockquote>💰 <b>Format:</b> <code>UserID Amount</code>\n(Ex: <code>12345 5000</code>)</blockquote>", parse_mode=ParseMode.HTML)
        return
    elif data == "admin_take_ask":
        ADMIN_INPUT_STATE[user_id] = 'take_money'
        await q.edit_message_text(f"<blockquote>💸 <b>Format:</b> <code>UserID Amount</code>\n(Ex: <code>12345 5000</code>)</blockquote>", parse_mode=ParseMode.HTML)
        return
    elif data == "admin_set_logger":
        ADMIN_INPUT_STATE[user_id] = "waiting_logger_id"
        await q.edit_message_text(f"<blockquote>📝 <b>Send Logger Group ID:</b></blockquote>", parse_mode=ParseMode.HTML)
        return
    elif data == "admin_code_ask":
        ADMIN_INPUT_STATE[user_id] = 'create_code'
        await q.edit_message_text(f"<blockquote>🎁 <b>Format:</b> <code>Name Amount Limit</code>\n(Ex: <code>MIMI100 500 10</code>)</blockquote>", parse_mode=ParseMode.HTML)
        return

    # --- ACTIONS ---
    elif data == "admin_toggle_eco":
        set_economy_status(not get_economy_status())
        await admin_panel(update, context)
        return
    elif data == "admin_del_logger":
        delete_logger_group()
        await q.answer("🗑 Logger Deleted!", show_alert=True)
        await admin_panel(update, context)
        return
    elif data == "admin_wipe_ask":
        kb = [[InlineKeyboardButton("⚠️ CONFIRM WIPE", callback_data="admin_wipe_confirm")], 
              [InlineKeyboardButton("🔙 Back", callback_data="admin_back")]]
        msg = f"<blockquote>☢️ <b>DATABASE WIPE?</b></blockquote>\n<blockquote>This cannot be undone! Are you sure?</blockquote>"
        await q.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)
        return
    elif data == "admin_wipe_confirm":
        wipe_database()
        await q.edit_message_text("<blockquote>💀 <b>DATABASE WIPED!</b></blockquote>", parse_mode=ParseMode.HTML)
        return
    elif data == "admin_back":
        await admin_panel(update, context)
        return
    elif data == "admin_close":
        await q.message.delete()
        if user_id in ADMIN_INPUT_STATE: 
            del ADMIN_INPUT_STATE[user_id]
        return

# --- 3. INPUT HANDLER ---
async def handle_admin_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in OWNER_IDS: 
        return False
    
    state = ADMIN_INPUT_STATE.get(user_id)
    if not state: 
        return False

    msg = update.message
    text = msg.text.strip() if msg.text else None

    # 🔥 1. BROADCAST LOGIC (ANY MEDIA) 🔥
    if state == 'broadcast':
        users = list(users_col.find({}))
        groups = list(groups_col.find({}))
        count = 0
        status_msg = await msg.reply_text("📢 Sending...")
        for chat in users + groups:
            try: 
                await context.bot.copy_message(chat_id=chat["_id"], from_chat_id=msg.chat_id, message_id=msg.message_id)
                count += 1
            except: 
                pass
        await status_msg.edit_text(f"✅ Sent to {count} chats!")
        del ADMIN_INPUT_STATE[user_id]
        return True

    if not text: 
        return False

    # 🔥 2. GROQ KEY HANDLER 🔥
    if state == 'set_groq_key':
        set_groq_api_key(text)
        await msg.reply_text("✅ Groq API Key Updated!")
        del ADMIN_INPUT_STATE[user_id]
        return True

    # 🔥 3. CHAT KEYS (GEMINI) 🔥
    if state == 'add_key':
        if add_api_key(text): 
            await msg.reply_text("✅ Gemini Key Added!")
        else: 
            await msg.reply_text("⚠️ Already Exists!")
    
    elif state == 'del_key':
        if remove_api_key(text): 
            await msg.reply_text("🗑 Gemini Key Deleted!")
        else: 
            await msg.reply_text("❌ Not Found.")

    # 🔥 4. GAME KEYS (WORDSEEK) 🔥
    elif state == 'add_game_key':
        if add_game_key(text): 
            await msg.reply_text("✅ Game Key Added!")
        else: 
            await msg.reply_text("⚠️ Already Exists!")

    elif state == 'del_game_key':
        if remove_game_key(text): 
            await msg.reply_text("🗑 Game Key Deleted!")
        else: 
            await msg.reply_text("❌ Not Found.")

    # 🔥 5. STICKER PACKS 🔥
    elif state == 'add_pack':
        pname = text.split('/')[-1]
        try:
            await context.bot.get_sticker_set(pname)
            if add_sticker_pack(pname): 
                await msg.reply_text(f"✅ Pack Added: `{pname}`")
            else: 
                await msg.reply_text("⚠️ Already Exists!")
        except: 
            await msg.reply_text("❌ Invalid Pack!")
    
    elif state == 'del_pack':
        if remove_sticker_pack(text): 
            await msg.reply_text("🗑 Pack Deleted!")
        else: 
            await msg.reply_text("❌ Not Found.")

    # 🔥 6. MONEY & OTHERS 🔥
    elif state in ['add_money', 'take_money']:
        try:
            parts = text.split()
            tid, amt = int(parts[0]), int(parts[1])
            if state == 'take_money': 
                amt = -amt
            update_balance(tid, amt)
            await msg.reply_text("✅ Balance Updated!")
        except: 
            await msg.reply_text("❌ Error! Format: `ID Amount`")

    elif state == 'create_code':
        try:
            parts = text.split()
            codes_col.insert_one({"code": parts[0], "amount": int(parts[1]), "limit": int(parts[2]), "redeemed_by": []})
            await msg.reply_text(f"🎁 Code Created: `{parts[0]}`")
        except: 
            await msg.reply_text("❌ Error!")

    elif state == 'waiting_logger_id':
        try:
            set_logger_group(int(text))
            await msg.reply_text(f"✅ Logger Set: `{text}`")
        except: 
            await msg.reply_text("❌ Invalid ID")

    # Clear state
    del ADMIN_INPUT_STATE[user_id]
    return True
