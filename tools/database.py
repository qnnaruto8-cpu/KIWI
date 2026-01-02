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

    # Collections (Tools & Settings)
    settings_db = db.settings
    filters_db = db.filters
    auth_db = db.auth_users  # ✅ NEW: Auth
    bank_db = db.bank_users  # ✅ NEW: Bank
    
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
#        🛡️ AUTH SYSTEM FUNCTIONS
# ==========================================

async def save_auth_user(chat_id: int, user_id: int, user_name: str, admin_name: str):
    doc = {
        "chat_id": chat_id,
        "user_id": user_id,
        "user_name": user_name,
        "admin_name": admin_name
    }
    await auth_db.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$set": doc},
        upsert=True
    )

async def delete_auth_user(chat_id: int, user_id: int):
    await auth_db.delete_one({"chat_id": chat_id, "user_id": user_id})

async def get_auth_users(chat_id: int):
    users = []
    async for doc in auth_db.find({"chat_id": chat_id}):
        users.append(doc)
    return users

async def is_user_authorized(chat_id: int, user_id: int):
    user = await auth_db.find_one({"chat_id": chat_id, "user_id": user_id})
    return True if user else False

# ==========================================
#        💰 BANK/ECONOMY FUNCTIONS
# ==========================================

async def get_balance(user_id: int):
    user = await bank_db.find_one({"user_id": user_id})
    if not user:
        return 0
    # 🔥 FIXED: Prevents KeyError
    return user.get("balance", 0)

async def set_balance(user_id: int, amount: int):
    await bank_db.update_one(
        {"user_id": user_id},
        {"$set": {"balance": amount}},
        upsert=True
    )

async def add_money(user_id: int, amount: int):
    current = await get_balance(user_id)
    new_bal = current + amount
    await set_balance(user_id, new_bal)
    return new_bal

async def deduct_money(user_id: int, amount: int):
    current = await get_balance(user_id)
    if current < amount:
        return False
    new_bal = current - amount
    await set_balance(user_id, new_bal)
    return True

# ==========================================
#        ⚙️ SETTINGS & MAINTENANCE
# ==========================================

# 1. Admin Command Mode (Legacy)
async def set_admincmd_mode(chat_id: int, state: bool):
    await settings_db.update_one(
        {"chat_id": chat_id},
        {"$set": {"admin_list_enabled": state}},
        upsert=True
    )

async def is_admincmd_enabled(chat_id: int):
    data = await settings_db.find_one({"chat_id": chat_id})
    if not data:
        return True
    return data.get("admin_list_enabled", True)

# 2. Global Music Mode
async def set_global_music(state: bool, reason: str = None):
    data = {"is_enabled": state}
    if reason:
        data["reason"] = reason
    else:
        data["reason"] = None
        
    await settings_db.update_one(
        {"type": "global_music"},
        {"$set": data},
        upsert=True
    )

async def get_music_status():
    data = await settings_db.find_one({"type": "global_music"})
    if not data:
        return True, None
    return data.get("is_enabled", True), data.get("reason", None)

# 🔥 3. NEW: MAINTENANCE MODE (Updated for Status + Custom Message) 🔥
async def get_maintenance_data():
    """Returns a dict: {'state': bool, 'message': str}"""
    try:
        data = await settings_db.find_one({"_id": "MAINTENANCE_STATUS"}) 
        if not data:
            return {"state": False, "message": None}
        return data
    except:
        return {"state": False, "message": None}

async def set_maintenance(state: bool, message: str = None):
    """Set Maintenance Mode with Message"""
    try:
        data = {"state": state}
        if message:
            data["message"] = message
            
        await settings_db.update_one(
            {"_id": "MAINTENANCE_STATUS"},
            {"$set": data},
            upsert=True
        )
    except:
        pass

# ==========================================
#        📝 FILTER SYSTEM FUNCTIONS
# ==========================================

async def save_filter(chat_id: int, keyword: str, file_data: dict):
    await filters_db.update_one(
        {"chat_id": chat_id, "keyword": keyword.lower()},
        {"$set": {"file_data": file_data}},
        upsert=True
    )

async def get_filter(chat_id: int, keyword: str):
    data = await filters_db.find_one({"chat_id": chat_id, "keyword": keyword.lower()})
    return data["file_data"] if data else None

async def delete_filter(chat_id: int, keyword: str):
    result = await filters_db.delete_one({"chat_id": chat_id, "keyword": keyword.lower()})
    return result.deleted_count > 0

async def get_all_filters(chat_id: int):
    keywords = []
    async for doc in filters_db.find({"chat_id": chat_id}):
        keywords.append(doc["keyword"])
    return keywords
    
