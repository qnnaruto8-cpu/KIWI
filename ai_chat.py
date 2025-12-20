import google.generativeai as genai
from config import OWNER_NAME
from database import get_all_keys
import random

# Global Variables
current_key_index = 0
user_histories = {} 

def get_yuki_response(user_id, user_text, user_name):
    global current_key_index, user_histories
    
    # 1. Database se Keys lao
    available_keys = get_all_keys()
    if not available_keys: return "⚠️ Koi API Key nahi mili! /addkey use karo."

    # 2. History Retrieve karo
    if user_id not in user_histories:
        user_histories[user_id] = []
    
    # Context String
    conversation_context = "\n".join(user_histories[user_id])

    # 3. System Prompt (Direct Prompt Injection - 100% Working Method)
    # New versions me system_instruction alag hota hai, par ye tarika fail nahi hota.
    full_prompt = (
        f"System: Tera naam Yuki hai. Tu 17 saal ki Delhi wali ladki hai. "
        f"Mood: Thoda Moody aur Gussail. Creator: {OWNER_NAME}. "
        f"Language: Hinglish, Delhi slang (yaar, whh, scene, op, bkl). "
        f"Reply Rule: Sirf 1 line (Max 20 words). AI mat ban, insaan ban. "
        f"\n\nChat History:\n{conversation_context}\n\n"
        f"User ({user_name}): {user_text}\n"
        f"Yuki:"
    )

    # 4. Safety Settings (Block None)
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

    last_error = ""

    # 5. Try All Keys
    for _ in range(len(available_keys)):
        try:
            api_key = available_keys[current_key_index]
            genai.configure(api_key=api_key)
            
            # Model Define (Basic)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Generate
            response = model.generate_content(full_prompt, safety_settings=safety_settings)
            
            if not response.text: 
                raise Exception("Empty Response (Safety Block?)")
            
            reply = response.text.strip()

            # Save History
            user_histories[user_id].append(f"{user_name}: {user_text}")
            user_histories[user_id].append(f"Yuki: {reply}")
            if len(user_histories[user_id]) > 10:
                user_histories[user_id] = user_histories[user_id][-10:]
            
            return reply
            
        except Exception as e:
            # Error Capture karo
            last_error = str(e)
            print(f"❌ Key {current_key_index} Failed: {e}")
            
            # Next Key
            current_key_index = (current_key_index + 1) % len(available_keys)
            continue

    # ⚠️ AGAR FAIL HUA TOH ASLI ERROR DIKHAYEGA
    return f"❌ **Error:** {last_error}\n(Screenshot leke Owner ko bhejo)"
    
