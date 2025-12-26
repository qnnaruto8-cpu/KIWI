import google.generativeai as genai
from config import OWNER_NAME, OWNER_USERNAME, GROUP_NAME, GROUP_LINK
from database import get_all_keys, get_sticker_packs
import random
import pytz 
from datetime import datetime 
import asyncio 

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
        prompt = (f"Act as Aniya (Cute Bestie). Write a short '{wish_type}' msg. Max 10 words.")
        response = model.generate_content(prompt, generation_config={"max_output_tokens": 40})
        return response.text.strip()
    except:
        return "Good Morning/Night! ☀️"

# --- 2. TEXT & REACTION GENERATION (SITUATION BASED) ---
# 🔥 Async function taaki Reaction de sake
async def get_yuki_response(user_id, user_text, user_name, message_object):
    global user_histories
    
    available_keys = get_all_keys()
    if not available_keys: return "Aniya abhi so rahi hai... 😴"

    if user_id not in user_histories: user_histories[user_id] = []
    
    # Context Window (Last 6 messages)
    if len(user_histories[user_id]) > 6:
        user_histories[user_id] = user_histories[user_id][-6:]

    conversation_context = "\n".join(user_histories[user_id])
    date_time_str = get_current_time_str()

    # 🔥 SMART PROMPT: Situation + Reaction + Politeness
    full_prompt = (
        f"System: Tera naam Aniya hai. Tu {OWNER_NAME} ki banayi hui ekdum Cute aur Sweet bot hai. "
        f"Creator: {OWNER_USERNAME}. Time: {date_time_str}. "
        f"Personality: Loving, Helpful, Soft, Polite (Bilkul Rude nahi hona). "
        f"Group Info: {GROUP_NAME} ({GROUP_LINK}). "
        
        f"TASK: User ke message ka reply de aur uska mood samajh kar Reaction Emoji choose kar.\n"
        
        f"🔴 IMPORTANT RULES (Follow Strictly):\n"
        f"1. **No One-Word Replies:** Sirf 'Han', 'Na', 'Mera' mat bolna. Pura sentence bolna. (e.g., 'Mera official group ye hai...' instead of just 'Mera')\n"
        f"2. **Group/Owner Queries:** Agar koi Group link maange toh link dena. Owner maange toh username dena.\n"
        f"3. **Reaction Logic:** Agar user ki baat Funny/Sad/Cute/Love wali hai, toh start mein <Emoji> lagana. Agar normal baat hai toh mat lagana.\n"
        
        f"FORMAT EXAMPLES:\n"
        f"- User: 'I love you' -> Output: <❤️> Aww, love you too baby!\n"
        f"- User: 'Group link do' -> Output: Ye lo mera official group join karlo! ✨\n"
        f"- User: 'Mai gir gaya' -> Output: <🥺> Oh no! Dhyaan rakha karo na apna.\n"
        
        f"\n\nChat History:\n{conversation_context}\n\n"
        f"User ({user_name}): {user_text}\n"
        f"Aniya:"
    )

    random.shuffle(available_keys) 

    for api_key in available_keys:
        try:
            genai.configure(api_key=api_key)
            # Tokens increased to 100 for full sentences
            model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"max_output_tokens": 100, "temperature": 0.7})
            
            # Async Call
            response = await model.generate_content_async(full_prompt)
            
            if not response.text: continue
            
            raw_text = response.text.strip()
            final_reply = raw_text
            
            # --- 🔥 REACTION PARSING LOGIC ---
            # AI output check karega: "<Emoji> Text"
            if raw_text.startswith("<") and ">" in raw_text:
                try:
                    parts = raw_text.split(">", 1) 
                    reaction_emoji = parts[0].replace("<", "").strip() 
                    final_reply = parts[1].strip()
                    
                    # Telegram Reaction Set Karo
                    if message_object:
                        await message_object.set_reaction(reaction=reaction_emoji)
                except:
                    pass # Format error ignore karo
            
            # History Update
            user_histories[user_id].append(f"U: {user_text}")
            user_histories[user_id].append(f"A: {final_reply}")
            
            return final_reply
            
        except Exception as e:
            print(f"⚠️ Key Failed: {e}")
            continue

    return "Mera sar dard ho raha hai... baad me baat karte hai! 🤕"

# --- 3. STICKER ---
async def get_mimi_sticker(bot):
    try:
        packs = get_sticker_packs()
        if not packs: return None
        sticker_set = await bot.get_sticker_set(random.choice(packs))
        if not sticker_set or not sticker_set.stickers: return None
        return random.choice(sticker_set.stickers).file_id
    except: return None
        
