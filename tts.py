import edge_tts
import os
import re

# 🔥 VOICE: "en-IN-NeerjaNeural" (Indian English - Best for Hinglish)
VOICE = "en-IN-NeerjaNeural"

def clean_text(text):
    """
    1. Emojis hatata hai (Sirf Text rakhta hai).
    2. Markdown (*, _) hatata hai taaki bot 'Star' na bole.
    """
    # 1. Remove Markdown (*bold*, _italic_)
    text = text.replace("*", "").replace("_", "").replace("`", "")
    
    # 2. Remove Emojis (Simple Hack: Sirf ASCII characters rakho)
    # Hinglish roman script me hoti hai, isliye ASCII rakhna safe hai.
    # Ye saare emojis uda dega.
    text = text.encode('ascii', 'ignore').decode('ascii')
    
    return text.strip()

async def generate_voice(text):
    """
    Generates voice using Microsoft Edge TTS (Free).
    Clean text -> Stable Audio.
    """
    try:
        # Step 1: Text saaf karo (No Emojis)
        cleaned_text = clean_text(text)
        
        # Agar text khali ho gaya (sirf emoji tha), to kuch mat bhejo
        if not cleaned_text: return None

        output_file = f"mimi_voice_{os.urandom(3).hex()}.mp3"
        
        # 🔥 SETTINGS UPDATE:
        # 'pitch' aur 'rate' hata diya hai taaki awaaz 'Atke' nahi.
        # Normal speed sabse stable hoti hai.
        communicate = edge_tts.Communicate(cleaned_text, VOICE)
        
        await communicate.save(output_file)
        return output_file

    except Exception as e:
        print(f"❌ EdgeTTS Error: {e}")
        return None
