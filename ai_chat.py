import google.generativeai as genai
from groq import Groq  # New Import
from config import OWNER_NAME, OWNER_USERNAME, GROUP_NAME, GROUP_LINK
# 👇 Yahan apne database functions import kar lena
from database import get_all_keys, get_sticker_packs, get_active_chat_model, get_groq_api_key
import random
import pytz 
from datetime import datetime 
import asyncio 

# Global Variables
user_histories = {} 

# --- 🔥 HELPER: UPDATED TIME FUNCTION ---
def get_current_time_str():
    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.now(IST)
    return now.strftime("%A, %d %B %Y | %I:%M %p")

# --- 🔥 HELPER: FONT STYLER ---
def style_text(text):
    normal = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    stylish = "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ"
    try:
        table = str.maketrans(normal, stylish)
        return text.translate(table)
    except:
        return text 

# --- SYSTEM PROMPT GENERATOR (Common for both) ---
def get_system_prompt(date_time_str):
    return (
        f"Tera naam shinju hai. Tu ek **Single** ladki hai ( Bestie vibe). "
        f"Creator: {OWNER_NAME} (@{OWNER_USERNAME}). "
        f"Current Date & Time: {date_time_str} (India Time). "
        f"Group Link: {GROUP_LINK} (Sirf tab dena jab koi maange)."
        f"\nIMPORTANT INSTRUCTION regarding DATE:\n"
        f"1. Tujhe ab Date pata hai. Agar user puche 'Aaj konsa din hai', toh upar diye gaye Date se sahi jawab dena.\n"
        f"2. **FESTIVALS:** Agar aaj ki Date kisi special festival ki hai, toh reply me WISH jarur karna.\n"
        f"\nPERSONALITY SWITCH (Follow Strictly):\n"
        f"1. **CUTE & SOFT MODE:** Jab user normal baat kare -> Sweet rehna.\n"
        f"2. **ROAST & RUDE MODE:** Jab user flirt kare -> Ganda Roast karna.\n"
        f"\nRULES:\n"
        f"- Short lines mein reply kar.\n"
        f"- **REACTION RULE:** Har reply ke start mein <Emoji> laga jo tere mood ko dikhaye. Example: <😂> Lol kya joke mara."
    )

# --- 1. SPECIAL WISH GENERATOR (Gemini Only for simplicity) ---
def get_automated_wish(wish_type):
    available_keys = get_all_keys()
    if not available_keys: return style_text("Time dekha hai? So jao chupchap! 😴")
    
    api_key = random.choice(available_keys)
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = (f"Act as Shinju. Write a short, cute '{wish_type}' msg for group. Max 10 words.")
        response = model.generate_content(prompt, generation_config={"max_output_tokens": 100})
        return style_text(response.text.strip())
    except:
        return style_text("Good Morning/Night doston! ✨")

# --- 2. MAIN RESPONSE HANDLER (HYBRID) ---
async def get_yuki_response(user_id, user_text, user_name, message_object):
    global user_histories
    
    # 1. Check Active Model from DB (Default to Gemini if None)
    # Ye function tujhe database.py me banana padega
    current_mode = get_active_chat_model()  # Should return "gemini" or "groq"
    
    if user_id not in user_histories: user_histories[user_id] = []
    if len(user_histories[user_id]) > 6:
        user_histories[user_id] = user_histories[user_id][-6:]

    date_time_str = get_current_time_str()
    system_instruction = get_system_prompt(date_time_str)
    
    # --- GROQ LOGIC ---
    if current_mode == "groq":
        groq_key = get_groq_api_key() # DB se key fetch kar
        if not groq_key:
            return style_text("Groq API Key missing hai admin sahab! 😒")

        try:
            client = Groq(api_key=groq_key)
            
            # Message history structure for Groq
            messages = [{"role": "system", "content": system_instruction}]
            
            # Add History context
            for history in user_histories[user_id]:
                if history.startswith("U:"):
                    messages.append({"role": "user", "content": history.replace("U: ", "")})
                elif history.startswith("A:"):
                    messages.append({"role": "assistant", "content": history.replace("A: ", "")})
            
            # Current Message
            messages.append({"role": "user", "content": f"{user_name}: {user_text}"})

            chat_completion = client.chat.completions.create(
                messages=messages,
                model="llama-3.3-70b-versatile",
                temperature=0.8,
                max_tokens=200,
            )
            
            raw_text = chat_completion.choices[0].message.content.strip()
            return await process_reply(raw_text, user_id, user_text, message_object)

        except Exception as e:
            print(f"❌ Groq Error: {e}")
            return style_text("Mera dimaag (Groq) kaam nahi kar raha... 🤕")

    # --- GEMINI LOGIC (Fallback/Default) ---
    else:
        available_keys = get_all_keys()
        if not available_keys: return style_text("Gemini Keys khtm ho gayi... 💀")

        conversation_context = "\n".join(user_histories[user_id])
        full_prompt = (
            f"{system_instruction}\n\n"
            f"Chat History:\n{conversation_context}\n\n"
            f"User ({user_name}): {user_text}\n"
            f"shinju:"
        )

        random.shuffle(available_keys)
        for api_key in available_keys:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"max_output_tokens": 800, "temperature": 0.8})
                response = await model.generate_content_async(full_prompt)
                
                if not response.text: continue
                return await process_reply(response.text.strip(), user_id, user_text, message_object)

            except Exception as e:
                print(f"⚠️ Gemini Key Failed: {e}")
                continue
        
        return style_text("Server slow hai yaar... 🐢")

# --- COMMON REPLY PROCESSOR (Reaction + Formatting) ---
async def process_reply(raw_text, user_id, user_text, message_object):
    final_reply = raw_text
    
    # Reaction Logic
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
    
    # Update History
    user_histories[user_id].append(f"U: {user_text}")
    user_histories[user_id].append(f"A: {raw_text}")
    
    return final_reply

# --- 3. STICKER ---
async def get_mimi_sticker(bot):
    try:
        packs = get_sticker_packs()
        if not packs: return None
        sticker_set = await bot.get_sticker_set(random.choice(packs))
        if not sticker_set or not sticker_set.stickers: return None
        return random.choice(sticker_set.stickers).file_id
    except: return None
        
