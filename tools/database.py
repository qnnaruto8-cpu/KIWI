import pymongo 
import motor.motor_asyncio
from config import MONGO_DB_URI

# --- 1. SYNC CONNECTION (Sirf Startup Cleanup ke liye) ---
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
if not MONGO_DB_URI:
    print("❌ ERROR: MONGO_DB_URI config.py mein nahi mila!")
    exit()

try:
    mongo_async = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DB_URI)
    db = mongo_async["MusicBot_Tools"]
    
    # Collections (Music)
    active_db = db.active_chats
    video_db = db.video_chats
    queue_db = db.queues
    
    # Collections (Broadcast Data)
    users_db = db.served_users
    chats_db = db.served_chats

    # Collections (Settings) 🔥 NEW
    settings_db = db.settings
    
    print("✅ Async Database Connected Successfully!")
except Exception as e:
    print(f"❌ Database Connection Error: {e}")
    exit()

# ==========================================
#        🎵 MUSIC BOT FUNCTIONS
# ==========================================

# --- ACTIVE CHAT FUNCTIONS ---
async def get_active_chats():
    chats = []
    async for x in active_db.find({}):
        chats.append(x["chat_id"])
    return chats

async def is_active_chat(chat_id: int):
    data = await active_db.find_one({"chat_id": chat_id})
    return True if data else False

async def add_active_chat(chat_id: int):
    check = await is_active_chat(chat_id)
    if not check:
        await active_db.insert_one({"chat_id": chat_id})

async def remove_active_chat(chat_id: int):
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
    await queue_db.update_one(
        {"chat_id": chat_id},
        {"$set": {"queue": queue_list}},
        upsert=True
    )

async def clear_db_queue(chat_id: int):
    await queue_db.delete_one({"chat_id": chat_id})
    
# --- CACHE FUNCTIONS ---
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

# ==========================================
#        📢 BROADCAST FUNCTIONS
# ==========================================

# 1. Served Users (DMs ke liye)
async def get_served_users():
    users_list = []
    async for user in users_db.find({"user_id": {"$gt": 0}}):
        users_list.append(user["user_id"])
    return users_list

async def add_served_user(user_id: int):
    is_served = await users_db.find_one({"user_id": user_id})
    if not is_served:
        await users_db.insert_one({"user_id": user_id})

# 2. Served Chats (Groups ke liye)
async def get_served_chats():
    chats_list = []
    async for chat in chats_db.find({"chat_id": {"$lt": 0}}):
        chats_list.append(chat["chat_id"])
    return chats_list

async def add_served_chat(chat_id: int):
    is_served = await chats_db.find_one({"chat_id": chat_id})
    if not is_served:
        await chats_db.insert_one({"chat_id": chat_id})

# ==========================================
#        ⚙️ SETTINGS FUNCTIONS (NEW)
# ==========================================

async def set_admincmd_mode(chat_id: int, state: bool):
    """Admin List command ko ON/OFF set karta hai"""
    await settings_db.update_one(
        {"chat_id": chat_id},
        {"$set": {"admin_list_enabled": state}},
        upsert=True
    )

async def is_admincmd_enabled(chat_id: int):
    """Check karta hai ki Admin List command ON hai ya OFF (Default: ON)"""
    data = await settings_db.find_one({"chat_id": chat_id})
    if not data:
        return True # Default ON rahega
    return data.get("admin_list_enabled", True)

# --- FILTER SYSTEM (tools/database.py ke end mein add karo) ---

filters_db = db.filters

async def save_filter(chat_id: int, keyword: str, file_data: dict):
    """Filter save karta hai (Keyword -> Content)"""
    await filters_db.update_one(
        {"chat_id": chat_id, "keyword": keyword.lower()},
        {"$set": {"file_data": file_data}},
        upsert=True
    )

async def get_filter(chat_id: int, keyword: str):
    """Keyword match hone par content deta hai"""
    data = await filters_db.find_one({"chat_id": chat_id, "keyword": keyword.lower()})
    return data["file_data"] if data else None

async def delete_filter(chat_id: int, keyword: str):
    """Filter delete karta hai"""
    result = await filters_db.delete_one({"chat_id": chat_id, "keyword": keyword.lower()})
    return result.deleted_count > 0

async def get_all_filters(chat_id: int):
    """Group ke saare filters ki list deta hai"""
    keywords = []
    async for doc in filters_db.find({"chat_id": chat_id}):
        keywords.append(doc["keyword"])
    return keywords
    
    
