import google.generativeai as genai
from config import OWNER_NAME, OWNER_USERNAME, GROUP_NAME, GROUP_LINK
from database import get_all_keys, get_sticker_packs
import random
import pytz 
from datetime import datetime 
import asyncio 

# Global Variables
user_histories = {} 

# --- 🔥 HELPER: UPDATED TIME FUNCTION (Date + Day + Time) ---
def get_current_time_str():
    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.now(IST)
    # Ab ye return karega: "Friday, 02 January 2026 | 09:45 PM"
    return now.strftime("%A, %d %B %Y | %I:%M %p")

# --- 🔥 HELPER: FONT STYLER (Small Caps) ---
def style_text(text):
    # Ye function normal text ko Aesthetic Small Caps me badal dega
    normal = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    stylish = "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ"
    try:
        table = str.maketrans(normal, stylish)
        return text.translate(table)
    except:
        return text 

# --- 1. SPECIAL WISH GENERATOR ---
def get_automated_wish(wish_type):
    available_keys = get_all_keys()
    if not available_keys: return style_text("Time dekha hai? So jao chupchap! 😴")
    
    api_key = random.choice(available_keys)
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = (f"Act as Aniya (Funny Bestie). Write a short, cute '{wish_type}' msg for group. Max 10 words.")
        response = model.generate_content(prompt, generation_config={"max_output_tokens": 100})
        return style_text(response.text.strip())
    except:
        return style_text("Good Morning/Night doston! ✨")

# --- 2. TEXT & REACTION GENERATION ---
async def get_yuki_response(user_id, user_text, user_name, message_object):
    global user_histories
    
    available_keys = get_all_keys()
    if not available_keys: return style_text("Mera mood off hai, baad me aana... 😒")

    if user_id not in user_histories: user_histories[user_id] = []
    
    # History Context (Last 6 messages)
    if len(user_histories[user_id]) > 6:
        user_histories[user_id] = user_histories[user_id][-6:]

    conversation_context = "\n".join(user_histories[user_id])
    
    # ✅ Yahan ab PURI Date aur Time aayega
    date_time_str = get_current_time_str()

    # 🔥 PROMPT (Updated for Date Awareness) 🔥
    full_prompt = (
        f"System: Tera naam Aniya hai. Tu ek **Single** ladki hai (Naughty Bestie vibe). "
        f"Creator: {OWNER_NAME} (@{OWNER_USERNAME}). "
        f"Current Date & Time: {date_time_str} (India Time). "
        f"Group Link: {GROUP_LINK} (Sirf tab dena jab koi maange)."
        
        f"IMPORTANT INSTRUCTION regarding DATE:\n"
        f"1. Tujhe ab Date pata hai. Agar user puche 'Aaj konsa din hai', toh upar diye gaye Date se sahi jawab dena.\n"
        f"2. **FESTIVALS:** Agar aaj ki Date kisi special festival (New Year, Diwali, Eid, Christmas) ki hai, toh reply me WISH jarur karna.\n"
        
        f"PERSONALITY SWITCH (Follow Strictly):\n"
        f"1. **CUTE & SOFT MODE:** Jab user normal baat kare, haal-chal puche -> Sweet rehna.\n"
        f"2. **ROAST & RUDE MODE:** Jab user flirt kare, faltu bakwas kare -> Ganda Roast karna.\n"
        
        f"RULES:\n"
        f"- Short lines mein reply kar.\n"
        f"- **REACTION RULE:** Har reply ke start mein <Emoji> laga jo tere mood ko dikhaye.\n"
        
        f"\n\nChat History:\n{conversation_context}\n\n"
        f"User ({user_name}): {user_text}\n"
        f"Aniya:"
    )

    random.shuffle(available_keys) 

    for api_key in available_keys:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"max_output_tokens": 800, "temperature": 0.8})
            
            response = await model.generate_content_async(full_prompt)
            
            if not response.text: continue
            
            raw_text = response.text.strip()
            final_reply = raw_text
            
            # --- 🔥 REACTION & FONT LOGIC ---
            if raw_text.startswith("<") and ">" in raw_text:
                try:
                    parts = raw_text.split(">", 1) 
                    reaction_emoji = parts[0].replace("<", "").strip() 
                    text_part = parts[1].strip()
                    
                    if message_object:
                        try: await message_object.set_reaction(reaction=reaction_emoji)
                        except: pass
                    
                    final_reply = style_text(text_part)
                except:
                    final_reply = style_text(raw_text)
            else:
                final_reply = style_text(raw_text)
            
            user_histories[user_id].append(f"U: {user_text}")
            user_histories[user_id].append(f"A: {raw_text}")
            
            return final_reply
            
        except Exception as e:
            print(f"⚠️ Key Failed: {e}")
            continue

    return style_text("Server slow hai yaar... 🐢")

# --- 3. STICKER ---
async def get_mimi_sticker(bot):
    try:
        packs = get_sticker_packs()
        if not packs: return None
        sticker_set = await bot.get_sticker_set(random.choice(packs))
        if not sticker_set or not sticker_set.stickers: return None
        return random.choice(sticker_set.stickers).file_id
    except: return None
        
