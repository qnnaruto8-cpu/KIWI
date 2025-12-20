import google.generativeai as genai
from config import OWNER_NAME
from database import get_all_keys
import random

# Global Variables
current_key_index = 0
user_histories = {}  # 🧠 MEMORY STORE

def get_yuki_response(user_id, user_text, user_name):
    global current_key_index, user_histories
    
    # 1. Database se Keys lao
    available_keys = get_all_keys()
    if not available_keys: return "Arre yaar, pehle /addkey se API Key toh daal! 🙄"

    # 2. History Retrieve karo
    if user_id not in user_histories:
        user_histories[user_id] = []
    
    # History context string banao
    conversation_context = "\n".join(user_histories[user_id])

    # 3. System Prompt (Strict Persona)
    # Isse Model ke andar direct inject karenge
    system_instruction = (
        f"Tera naam Yuki hai. Tu 17 saal ki Delhi wali ladki hai. "
        f"Tu Class 12th mein hai. "
        f"Tera mood thoda Moody hai (Kabhi gussa, kabhi emotional, kabhi chill). "
        f"Tera Creator {OWNER_NAME} hai. "
        f"Language: Hinglish, Delhi slang (yaar, whh, scene, op, bkl). "
        f"Rule 1: Sirf 1 line mein reply karna (Max 10-20 words). "
        f"Rule 2: Hi/Hello se baat shuru hoti hai toh end tak usi topic par baat karna. Topic change mat karna khud se. "
        f"Rule 3: Tu AI nahi hai, tu insaan hai. "
    )

    # 4. Safety Settings (Taaki Bot Block na ho Slang use karne par)
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

    # 5. Loop through keys until success
    for _ in range(len(available_keys)):
        try:
            # Current Key nikalo
            api_key = available_keys[current_key_index]
            genai.configure(api_key=api_key)
            
            # 🔥 FIX: Model Name & System Instruction Direct Injection
            model = genai.GenerativeModel(
                model_name='gemini-1.5-flash',
                system_instruction=system_instruction
            )
            
            # Request generate karo (History + New Msg)
            full_prompt = f"Chat History:\n{conversation_context}\n\nUser ({user_name}): {user_text}\nYuki:"
            
            response = model.generate_content(
                full_prompt,
                safety_settings=safety_settings
            )
            
            # Check for valid text
            if not response.text: 
                raise Exception("Empty Response (Blocked by Safety)")
            
            reply = response.text.strip()

            # 6. History Update
            user_histories[user_id].append(f"{user_name}: {user_text}")
            user_histories[user_id].append(f"Yuki: {reply}")
            
            # Memory Limit (Last 10 messages taaki context bana rahe)
            if len(user_histories[user_id]) > 10:
                user_histories[user_id] = user_histories[user_id][-10:]
            
            return reply
            
        except Exception as e:
            print(f"⚠️ Key Failed (Index {current_key_index}): {e}")
            
            # Key Rotate logic
            current_key_index = (current_key_index + 1) % len(available_keys)
            continue

    return "Mood kharab hai abhi, baad mein baat karungi! 😒 (Server Busy)"

