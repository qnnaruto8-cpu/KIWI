import pymongo 
import motor.motor_asyncio
from config import MONGO_DB_URI

# --- 1. SYNC CONNECTION (Sirf Startup Cleanup ke liye) ---
# Ye bot start hone se pehle purana kachra saaf karega
try:
    cli_sync = pymongo.MongoClient(MONGO_DB_URI)
    db_sync = cli_sync["MusicBot_Tools"]
    
    # Safai Abhiyan (Active Chats Clean)
    db_sync.active_chats.delete_many({})
    db_sync.video_chats.delete_many({})
    print("🧹 Active Chat Data Cleared for Fresh Start.")
except Exception as e:
    print(f"⚠️ Startup Cleanup Failed: {e}")

# --- 2. ASYNC CONNECTION (Bot ke chalne ke liye) ---
# Ye actual music play hone ke time kaam aayega (No Lag)
if not MONGO_DB_URI:
    print("❌ ERROR: MONGO_DB_URI config.py mein nahi mila!")
    exit()

try:
    mongo_async = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DB_URI)
    db = mongo_async["MusicBot_Tools"]
    
    # Collections
    active_db = db.active_chats
    video_db = db.video_chats
    queue_db = db.queues
    
    print("✅ Async Database Connected Successfully!")
except Exception as e:
    print(f"❌ Database Connection Error: {e}")
    exit()

# --- ACTIVE CHAT FUNCTIONS ---

async def get_active_chats():
    """Start hone par active chats ki list deta hai"""
    chats = []
    # Async loop se data nikalna padta hai
    async for x in active_db.find({}):
        chats.append(x["chat_id"])
    return chats

async def is_active_chat(chat_id: int):
    """Check agar Audio Play ho raha hai"""
    data = await active_db.find_one({"chat_id": chat_id})
    return True if data else False

async def add_active_chat(chat_id: int):
    """Group ko Audio Active list mein daalo"""
    # Duplicate check
    check = await is_active_chat(chat_id)
    if not check:
        await active_db.insert_one({"chat_id": chat_id})

async def remove_active_chat(chat_id: int):
    """Group ko Audio Active list se hatao"""
    await active_db.delete_one({"chat_id": chat_id})

# --- VIDEO CHAT FUNCTIONS ---

async def is_active_video_chat(chat_id: int):
    data = await video_db.find_one({"chat_id": chat_id})
    return True if data else False

async def add_active_video_chat(chat_id: int):
    check = await is_active_video_chat(chat_id)
    if not check:
        await video_db.insert_one({"chat_id": chat_id})

async def remove_active_video_chat(chat_id: int):
    await video_db.delete_one({"chat_id": chat_id})

# --- QUEUE FUNCTIONS ---

async def get_db_queue(chat_id: int):
    data = await queue_db.find_one({"chat_id": chat_id})
    if data:
        return data.get("queue", [])
    return []

async def save_db_queue(chat_id: int, queue_list: list):
    # Update One (Upsert=True ka matlab: nahi hai to naya banao, hai to update karo)
    await queue_db.update_one(
        {"chat_id": chat_id},
        {"$set": {"queue": queue_list}},
        upsert=True
    )

async def clear_db_queue(chat_id: int):
    await queue_db.delete_one({"chat_id": chat_id})
    
# --- CACHE FUNCTIONS (Fast Play ke liye) ---
# Jo humne /fplay ke liye discuss kiya tha

async def save_cached_song(query, result):
    collection = db["Music_Cache"]
    exist = await collection.find_one({"query": query.lower().strip()})
    if not exist:
        data = {
            "query": query.lower().strip(),
            "data": result
        }
        await collection.insert_one(data)

async def get_cached_song(query):
    collection = db["Music_Cache"]
    result = await collection.find_one({"query": query.lower().strip()})
    if result:
        return result["data"]
    return None

