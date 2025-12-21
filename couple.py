import os
import random
import io
import asyncio
import html
from PIL import Image, ImageDraw, ImageFont, ImageOps
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
# 🔥 IMPORT CHAT STATS COLLECTION
from database import chat_stats_col

# --- CONFIGURATION ---
BG_IMAGE = "ccpic.png"
FONT_PATH = "arial.ttf"

# 🔥 COORDINATES (Updated for Alignment)
POS_1 = (120, 160)   # Left Circle
POS_2 = (760, 160)   # Right Circle
CIRCLE_SIZE = 400    # Circle Diameter

def to_fancy(text):
    mapping = {'A': 'Λ', 'E': 'Є', 'S': 'δ', 'O': 'σ', 'T': 'ᴛ', 'N': 'ɴ', 'M': 'ᴍ', 'U': 'ᴜ', 'R': 'ʀ', 'D': 'ᴅ', 'C': 'ᴄ', 'P': 'ᴘ', 'G': 'ɢ', 'B': 'ʙ', 'L': 'ʟ', 'W': 'ᴡ', 'K': 'ᴋ', 'J': 'ᴊ', 'Y': 'ʏ', 'I': 'ɪ', 'H': 'ʜ'}
    return "".join(mapping.get(c.upper(), c) for c in text)

# --- SYNC IMAGE PROCESSING ---
def process_image_sync(bg_path, pfp1_bytes, pfp2_bytes, name1, name2):
    print(f"🎨 Processing image: {name1} & {name2}")
    try:
        bg = Image.open(bg_path).convert("RGBA")
    except Exception as e:
        print(f"⚠️ Background Error: {e}")
        bg = Image.new('RGBA', (1280, 720), (200, 0, 0, 255))

    def process_pfp(img_bytes, label_name):
        img = None
        if img_bytes:
            try:
                img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
                print(f"✅ PFP Loaded: {label_name}")
            except Exception as e:
                print(f"⚠️ PFP Load Failed: {e}")

        # Fallback if no PFP
        if img is None:
            img = Image.new('RGBA', (CIRCLE_SIZE, CIRCLE_SIZE), (random.randint(50, 150), random.randint(50, 150), random.randint(150, 250)))
            d = ImageDraw.Draw(img)
            char = label_name[0].upper() if label_name else "?"
            try:
                fnt = ImageFont.truetype(FONT_PATH, 140)
            except:
                fnt = ImageFont.load_default()
            
            bbox = d.textbbox((0, 0), char, font=fnt)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            d.text(((CIRCLE_SIZE - w) / 2, (CIRCLE_SIZE - h) / 2), char, fill="white", font=fnt)

        # Masking
        img = ImageOps.fit(img, (CIRCLE_SIZE, CIRCLE_SIZE), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
        mask = Image.new('L', (CIRCLE_SIZE, CIRCLE_SIZE), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, CIRCLE_SIZE, CIRCLE_SIZE), fill=255)
        
        result = Image.new('RGBA', (CIRCLE_SIZE, CIRCLE_SIZE), (0, 0, 0, 0))
        result.paste(img, (0, 0), mask=mask)
        return result

    img1 = process_pfp(pfp1_bytes, name1)
    img2 = process_pfp(pfp2_bytes, name2)

    bg.paste(img1, POS_1, img1)
    bg.paste(img2, POS_2, img2)

    # Names
    draw = ImageDraw.Draw(bg)
    try:
        font = ImageFont.truetype(FONT_PATH, 35)
    except:
        font = ImageFont.load_default()

    # Draw Name 1
    name1_disp = name1[:15]
    bbox1 = draw.textbbox((0, 0), name1_disp, font=font)
    w1 = bbox1[2] - bbox1[0]
    draw.text((POS_1[0] + (CIRCLE_SIZE - w1) // 2, POS_1[1] + CIRCLE_SIZE + 30), name1_disp, font=font, fill="white")

    # Draw Name 2
    name2_disp = name2[:15]
    bbox2 = draw.textbbox((0, 0), name2_disp, font=font)
    w2 = bbox2[2] - bbox2[0]
    draw.text((POS_2[0] + (CIRCLE_SIZE - w2) // 2, POS_2[1] + CIRCLE_SIZE + 30), name2_disp, font=font, fill="white")

    bio = io.BytesIO()
    bio.name = "couple.png"
    bg.save(bio, "PNG")
    bio.seek(0)
    return bio

# --- ASYNC WRAPPER ---
async def make_couple_img(user1, user2, context):
    async def get_bytes(u_id):
        if not u_id: return None
        print(f"📥 Downloading PFP for: {u_id}")
        try:
            # 🔥 CRITICAL FIX HERE: 'get_user_profile_photos'
            photos = await context.bot.get_user_profile_photos(u_id, limit=1)
            
            if photos.total_count > 0:
                file = await context.bot.get_file(photos.photos[0][-1].file_id)
                f_stream = io.BytesIO()
                await file.download_to_memory(out=f_stream)
                f_stream.seek(0) # 🔥 FIX GREY BOX
                print(f"✅ Downloaded bytes for {u_id}")
                return f_stream.getvalue()
            else:
                print(f"ℹ️ No PFP for {u_id}")
        except Exception as e:
            print(f"⚠️ Error Downloading PFP: {e}")
        return None

    pfp1_bytes, pfp2_bytes = await asyncio.gather(
        get_bytes(user1['id']),
        get_bytes(user2['id'])
    )

    loop = asyncio.get_running_loop()
    final_img = await loop.run_in_executor(
        None, 
        process_image_sync, 
        BG_IMAGE, pfp1_bytes, pfp2_bytes, user1['first_name'], user2['first_name']
    )
    return final_img

# --- COMMAND ---
async def couple_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    bot_id = context.bot.id
    
    msg = await update.message.reply_text("🔍 **Finding active lovers...**", parse_mode=ParseMode.MARKDOWN)

    try:
        pipeline = [
            {"$match": {"group_id": chat_id, "user_id": {"$ne": bot_id}}}, 
            {"$sample": {"size": 2}}
        ]
        
        random_users = list(chat_stats_col.aggregate(pipeline))
        
        if len(random_users) < 2:
            print("⚠️ Using fallback data for testing.")
            u1_data = {'user_id': update.effective_user.id, 'first_name': update.effective_user.first_name}
            u2_data = {'user_id': 0, 'first_name': 'No User'}
        else:
            u1 = random_users[0]
            u2 = random_users[1]
            
            async def resolve_user(u_doc):
                uid = u_doc.get('user_id')
                name = u_doc.get('first_name', 'Unknown')
                if name == 'Unknown' or name is None:
                    try:
                        chat_member = await context.bot.get_chat_member(chat_id, uid)
                        name = chat_member.user.first_name
                    except: pass
                return {'user_id': uid, 'first_name': name}

            u1_data = await resolve_user(u1)
            u2_data = await resolve_user(u2)

        user1_final = {'id': u1_data['user_id'], 'first_name': u1_data.get('first_name', 'Lover 1')}
        user2_final = {'id': u2_data['user_id'], 'first_name': u2_data.get('first_name', 'Lover 2')}

        photo = await make_couple_img(user1_final, user2_final, context)
        
        caption = f"""
<blockquote><b>💘 {to_fancy("TODAY'S COUPLE")}</b></blockquote>

<blockquote>
<b>🦁 ʙᴏʏ :</b> {html.escape(user1_final['first_name'])}
<b>🐰 ɢɪʀʟ :</b> {html.escape(user2_final['first_name'])}
</blockquote>

<blockquote>
<b>✨ ᴍᴀᴛᴄʜ :</b> 100% ❤️
<b>📅 ᴅᴀᴛᴇ :</b> {to_fancy("FOREVER")}
</blockquote>
"""
        kb = [[InlineKeyboardButton("👨‍💻 Support", url="https://t.me/Dev_Digan")]]
        
        if photo:
            await update.message.reply_photo(
                photo=photo,
                caption=caption,
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode=ParseMode.HTML
            )
        else:
            await msg.edit_text("❌ Image Gen Failed.")
            
        await msg.delete()

    except Exception as e:
        print(f"❌ Error: {e}")
        await msg.edit_text(f"❌ Error: {e}")
