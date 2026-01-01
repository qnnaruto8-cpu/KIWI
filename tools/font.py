from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from telegram.constants import ParseMode

# --- 1. FONT STYLES DATABASE ---
font_styles = {
    "sᴍᴀʟʟ ᴄᴀᴘs": str.maketrans(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"
    ),
    "𝚃𝚢𝚙𝚎𝚠𝚛𝚒𝚝𝚎𝚛": str.maketrans(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        "𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿"
    ),
    "𝕆𝕦𝕥𝕝𝕚𝕟𝕖": str.maketrans(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        "𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ𝟘𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡"
    ),
    "𝐒𝐞𝐫𝐢𝐟 𝐁𝐨𝐥𝐝": str.maketrans(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        "𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗"
    ),
    "Script": str.maketrans(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "𝒶𝒷𝒸𝒹𝑒𝒻𝑔𝒽𝒾𝒿𝓀𝓁𝓂𝓃𝑜𝓅𝓆𝓇𝓈𝓉𝓊𝓋𝓌𝓍𝓎𝓏𝒜𝐵𝒞𝒟𝐸𝐹𝒢𝐻𝐼𝒥𝒦𝐿𝑀𝒩𝒪𝒫𝒬𝑅𝒮𝒯𝒰𝒱𝒲𝒳𝒴𝒵"
    ),
    "Circles": str.maketrans(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        "ⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏ⓪①②③④⑤⑥⑦⑧⑨"
    ),
    "Squares": str.maketrans(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "🄰🄱🄲🄳🄴🄵🄶🄷🄸🄹🄺🄻🄼🄽🄾🄿🅀🅁🅂🅃🅄🅅🅆🅇🅈🅉🄰🄱🄲🄳🄴🄵🄶🄷🄸🄹🄺🄻🄼🄽🄾🄿🅀🅁🅂🅃🅄🅅🅆🅇🅈🅉"
    ),
    "Gothic": str.maketrans(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "𝔞𝔟𝔠𝔡𝔢𝔣𝔤𝔥𝔦𝔧𝔨𝔩𝔪𝔫𝔬𝔭𝔮𝔯𝔰𝔱𝔲𝔳𝔴𝔵𝔶𝔷𝔄𝔅ℭ𝔇𝔈𝔉𝔊ℌℑ𝔍𝔎𝔏𝔐𝔑𝔒𝔓𝔔ℜ𝔖𝔗𝔘𝔙𝔚𝔛𝔜ℨ"
    ),
    "Clouds": str.maketrans(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "ᗩᗷᑕᗪEᖴGᕼIᒍKᒪᗰᑎOᑭᑫᖇᔕTᑘᐯᗯ᙭YᘔᗩᗷᑕᗪEᖴGᕼIᒍKᒪᗰᑎOᑭᑫᖇᔕTᑘᐯᗯ᙭Yᘔ"
    ),
}

# --- 2. PAGINATION HELPER ---
CHUNK_SIZE = 4

def get_font_page(text, page=0):
    styles = list(font_styles.items())
    total_styles = len(styles)
    total_pages = (total_styles + CHUNK_SIZE - 1) // CHUNK_SIZE
    
    # Slice logic
    start = page * CHUNK_SIZE
    end = start + CHUNK_SIZE
    current_batch = styles[start:end]
    
    # Message Build
    msg = f"🎨 **Font Generator**\n📄 Page {page+1}/{total_pages}\n\n"
    msg += "👇 **Tap to Copy:**\n\n"
    
    for name, mapper in current_batch:
        try:
            converted = text.translate(mapper)
            msg += f"🔹 <b>{name}:</b>\n<code>{converted}</code>\n\n"
        except:
            continue
        
    # Buttons Build
    buttons = []
    row = []
    if page > 0:
        row.append(InlineKeyboardButton("⬅️ Back", callback_data=f"font_prev_{page}"))
    if page < total_pages - 1:
        row.append(InlineKeyboardButton("Next ➡️", callback_data=f"font_next_{page}"))
    
    if row: buttons.append(row)
    buttons.append([InlineKeyboardButton("🗑 Close", callback_data="font_close")])
    
    return msg, InlineKeyboardMarkup(buttons)

# --- 3. COMMAND HANDLER ---
async def font_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("ℹ️ **Usage:** `/font Your Text Here`")
    
    text = " ".join(context.args)
    
    # Text ko context mein save kar lo (Buttons ke liye)
    context.user_data['font_text'] = text
    
    msg, markup = get_font_page(text, page=0)
    await update.message.reply_text(msg, reply_markup=markup, parse_mode=ParseMode.HTML)

# --- 4. CALLBACK HANDLER (BUTTONS) ---
async def font_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    # Close Logic
    if data == "font_close":
        await query.message.delete()
        return

    # Text Fetch karo
    text = context.user_data.get('font_text', "Sample Text")
    
    # Page Change Logic
    if data.startswith("font_prev_"):
        current_page = int(data.split("_")[2])
        new_page = current_page - 1
    elif data.startswith("font_next_"):
        current_page = int(data.split("_")[2])
        new_page = current_page + 1
    else:
        return

    msg, markup = get_font_page(text, page=new_page)
    
    # Edit Message
    try:
        await query.edit_message_text(text=msg, reply_markup=markup, parse_mode=ParseMode.HTML)
    except:
        pass 
    await query.answer()

# --- 5. REGISTER HANDLERS ---
def register_handlers(app):
    app.add_handler(CommandHandler("font", font_command))
    
    # 🔥 MAJOR UPDATE: group=1 Add kiya gaya hai
    # Isse buttons ab Main Bot ke handlers se alag hokar chalenge
    app.add_handler(CallbackQueryHandler(font_button_handler, pattern="^font_"), group=1)
    
    print("  ✅ Styled Font Module Loaded!")
    
