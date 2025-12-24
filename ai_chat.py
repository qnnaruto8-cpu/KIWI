import google.generativeai as genai
from config import OWNER_NAME
from database import get_all_keys, get_sticker_packs
import random
import pytz 
from datetime import datetime 

# Global Variables
current_key_index = 0
user_histories = {} 

# --- HELPER: TIME FUNCTION ---
def get_current_time_str():
    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.now(IST)
    return now.strftime("%A, %d %B %Y | Time: %I:%M %p")

# --- 1. SPECIAL WISH GENERATOR (For Auto Voice Note) ---
def get_automated_wish(wish_type):
    """
    Ye function bina history ke Good Morning/Night msg generate karega.
    wish_type: 'morning' or 'night'
    """
    available_keys = get_all_keys()
    if not available_keys: return "Good night sabko! (No API Key)"
    
    api_key = random.choice(available_keys)
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    time_str = get_current_time_str()
    
    prompt = (
        f"System: Tera naam aniya hai. Tu ek cute girlfriend/bestie ki tarah baat karti hai. "
        f"Task: Ek chhota sa '{wish_type}' message likh voice note ke liye. "
        f"Current Time: {time_str}. "
        f"Creator:{OWNER_NAME}. "
        f"Creator username:{OWNER_USERNAME} "
        f"Style: "
        f"- Hinglish (Roman Hindi) use kar. "
        f"- Message bohot cute aur caring hona chahiye. "
        f"- Max 15-20 words. "
        f"- Emojis use kar. "
        f"- Example Night: 'Oye so jao ab, bohot raat ho gayi. Good Night! 😴❤️' "
        f"- Example Morning: 'Good Morning! Uth jao, naya din wait kar raha hai! ☀️' "
        f"Message:"
        
    )
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        if wish_type == "night": return "Oye so jao ab, Good Night! 😴❤️"
        return "Good Morning! Have a nice day! ☀️"

# --- 2. TEXT GENERATION (Normal Chat) ---
def get_yuki_response(user_id, user_text, user_name):
    global current_key_index, user_histories
    
    available_keys = get_all_keys()
    if not available_keys: return "aniya abhi so rahi hai... (No API Key) 😴"

    if user_id not in user_histories: user_histories[user_id] = []
    
    conversation_context = "\n".join(user_histories[user_id])
    date_time_str = get_current_time_str()

    full_prompt = (
        f"System: Tera naam aniya hai. Tu 17 saal ki cute college student hai. "
        f"Tera Creator: {OWNER_NAME}. "
        f" Creator username {OWNER_USERNAME}"
        f"Abhi ka Time: {date_time_str}. "
        f"Personality: Friendly, bubbly aur thodi naughty. "
        f"Language: Hinglish. "
        f"Style: Short reply (Max 15 words), Emojis use kar. "
        f"\n\nChat History:\n{conversation_context}\n\n"
        f"User ({user_name}): {user_text}\n"
        f"- tera group ya home ye hai join link https://t.me/+aw9rUJoO2JYwNjQ1."
        f"- tera group name chilvibe hai "
        f"aniya:"
    )

    last_error = ""

    for _ in range(len(available_keys)):
        try:
            current_key_index = current_key_index % len(available_keys)
            api_key = available_keys[current_key_index]
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            response = model.generate_content(full_prompt)
            if not response.text: raise Exception("Empty")
            
            reply = response.text.strip()
            user_histories[user_id].append(f"{user_name}: {user_text}")
            user_histories[user_id].append(f"Mimi: {reply}")
            
            if len(user_histories[user_id]) > 10:
                user_histories[user_id] = user_histories[user_id][-10:]
            
            return reply
            
        except Exception as e:
            last_error = str(e)
            current_key_index += 1
            continue

    return f"aniya busy hai! (Error: {last_error})"

# --- 3. STICKER GENERATION ---
async def get_mimi_sticker(bot):
    try:
        packs = get_sticker_packs()
        if not packs: return None
        
        # Safe Sticker Fetching
        try:
            sticker_set = await bot.get_sticker_set(random.choice(packs))
        except: return None
        
        if not sticker_set or not sticker_set.stickers: return None
        return random.choice(sticker_set.stickers).file_id
    except: return None
