import edge_tts
import os
import asyncio

# 🔥 Voice ID: "hi-IN-SwaraNeural" (Young Indian Girl - Best for Hinglish)
# Ye awaaz robotic nahi lagti, cute aur natural hai.
VOICE = "hi-IN-SwaraNeural"

async def generate_voice(text):
    """
    Generates voice using Microsoft Edge TTS (Free & High Quality).
    No API Key required.
    """
    try:
        # Unique filename banaya
        output_file = f"mimi_voice_{os.urandom(3).hex()}.mp3"
        
        # Audio generate karo
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(output_file)
        
        return output_file

    except Exception as e:
        print(f"❌ EdgeTTS Error: {e}")
        return None
