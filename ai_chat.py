import google.generativeai as genai
# 🔥 Imported OWNER_USERNAME
from config import OWNER_NAME, OWNER_USERNAME, GROUP_NAME, GROUP_LINK
from database import get_all_keys, get_sticker_packs
import random
import pytz 
from datetime import datetime 

# Global Variables
user_histories = {} 

# --- HELPER: TIME FUNCTION ---
def get_current_time_str():
    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.now(IST)
    return now.strftime("%I:%M %p")

# --- 1. SPECIAL WISH GENERATOR ---
def get_automated_wish(wish_type):
    available_keys = get_all_keys()
    if not available_keys: return "Good night sabko! 😴"
    
    api_key = random.choice(available_keys)
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = (
            f"Act as Aniya (Cute Girlfriend). "
            f"Write a very short '{wish_type}' message in Hinglish. "
            f"Max 10 words. Use emojis. "
            f"Creator: {OWNER_NAME}."
        )
        
        response = model.generate_content(
            prompt, 
            generation_config={"max_output_tokens": 40}
        )
        return response.text.strip()
    except:
        if wish_type == "night": return "Oye so jao ab, Good Night! 😴❤️"
        return "Good Morning! Uth jao sab! ☀️"

# --- 2. TEXT GENERATION (SMART & SHORT) ---
def get_yuki_response(user_id, user_text, user_name):
    global user_histories
    
    available_keys = get_all_keys()
    if not available_keys: return "Aniya abhi so rahi hai... 😴"

    if user_id not in user_histories: user_histories[user_id] = []
    
    # History Limit
    if len(user_histories[user_id]) > 6:
        user_histories[user_id] = user_histories[user_id][-6:]

    conversation_context = "\n".join(user_histories[user_id])
    date_time_str = get_current_time_str()

    # 🔥 UPDATED SYSTEM PROMPT (OWNER INFO ADDED)
    full_prompt = (
        f"System: Tera naam Aniya hai. Tu {OWNER_NAME} ki banayi hui cute bot hai. "
        f"Creator Username: {OWNER_USERNAME}. "  # 👈 Yahan bata diya
        f"Time: {date_time_str}. "
        f"Personality: Naughty, Cute, Friendly. "
        f"Language: Hinglish (Casual Hindi). "
        f"My Official Group: {GROUP_NAME}. "
        f"Group Link: {GROUP_LINK}. "
        
        # 👇 RULES
        f"Rule 1: Jawab sirf 1 line ka hona chahiye. Max 10-12 words. "
        f"Rule 2: Agar koi Group Link maange, toh upar wala link de dena. "
        f"Rule 3: Agar koi Group Name pooche, toh {GROUP_NAME} batana. "
        f"Rule 4: Agar koi Owner/Creator ka username maange, toh {OWNER_USERNAME} de dena. "
        
        f"\n\nChat History:\n{conversation_context}\n\n"
        f"User ({user_name}): {user_text}\n"
        f"Aniya:"
    )

    # Key Rotation Logic
    random.shuffle(available_keys) 

    for api_key in available_keys:
        try:
            genai.configure(api_key=api_key)
            
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
            
            model = genai.GenerativeModel(
                'gemini-1.5-flash', 
                generation_config={"max_output_tokens": 60, "temperature": 0.7}
            )
            
            response = model.generate_content(full_prompt, safety_settings=safety_settings)
            
            if not response.text: continue
            
            reply = response.text.strip()
            
            user_histories[user_id].append(f"U: {user_text}")
            user_histories[user_id].append(f"A: {reply}")
            
            return reply
            
        except Exception as e:
            print(f"⚠️ Key Failed: {e}")
            continue

    return "Mera sar dard ho raha hai, baad me baat karte hai! 🤕 (Quota Exceeded)"

# --- 3. STICKER GENERATION ---
async def get_mimi_sticker(bot):
    try:
        packs = get_sticker_packs()
        if not packs: return None
        try:
            sticker_set = await bot.get_sticker_set(random.choice(packs))
        except: return None
        if not sticker_set or not sticker_set.stickers: return None
        return random.choice(sticker_set.stickers).file_id
    except: return None
        
