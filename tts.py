import requests
import os
from database import get_all_voice_keys, remove_voice_key
# Config se sirf Voice ID lo, API Key ab Database se ayegi
from config import ELEVENLABS_VOICE_ID 

def generate_voice(text):
    """
    Auto-Switching Logic:
    1. DB se keys layega.
    2. Try karega, agar quota khatam to key delete karke next try karega.
    """
    keys = get_all_voice_keys()
    
    if not keys:
        print("❌ No Voice Keys Found in DB!")
        return None

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    CHUNK_SIZE = 1024

    for api_key in keys:
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }

        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
        }

        try:
            print(f"🎤 Trying Key: {api_key[:5]}...") # Debug log
            response = requests.post(url, json=data, headers=headers)
            
            # ✅ SUCCESS
            if response.status_code == 200:
                file_path = f"mimi_{os.urandom(4).hex()}.mp3"
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                        if chunk: f.write(chunk)
                return file_path
            
            # ⚠️ QUOTA FINISHED / INVALID KEY (401 = Unauthorized, 402 = Payment Required)
            elif response.status_code in [401, 402]:
                print(f"🚫 Key Expired/Dead: {api_key[:5]}... Removing from DB.")
                remove_voice_key(api_key) # 🔥 Auto Delete Dead Key
                continue # Next key try karo loop me
            
            else:
                print(f"⚠️ TTS Error ({response.status_code}): {response.text}")
                continue

        except Exception as e:
            print(f"❌ TTS Exception: {e}")
            continue
            
    print("❌ All keys failed or exhausted.")
    return None
