import pymongo 
import time
import datetime 
# 🔥 CHANGE 1: LOGGER_ID yahan import kiya hai
from config import MONGO_URL, LOGGER_ID 

# --- DATABASE CONNECTION ---
try:
    client = pymongo.MongoClient(MONGO_URL)
    db = client["CasinoBot"]

    # Collections
    users_col = db["users"]
    groups_col = db["groups"]
    investments_col = db["investments"]
    codes_col = db["codes"]
    keys_col = db["api_keys"]        
    game_keys_col = db["game_keys"]  
    settings_col = db["settings"]
    wordseek_col = db["wordseek_scores"] 
    warnings_col = db["warnings"]    
    packs_col = db["sticker_packs"]  
    chat_stats_col = db["chat_stats"]
    
    # Voice & Moderation
    voice_keys_col = db["voice_keys"] 
    mutes_col = db["mutes"]           
    bans_col = db["bans"]             

    print("✅ Database Connected!")
except Exception as e:
    print(f"❌ DB Error: {e}")

# --- 1. USER & ECONOMY ---

def update_username(user_id, name):
    users_col.update_one({"_id": user_id}, {"$set": {"name": name}}, upsert=True)

def check_registered(user_id):
    return users_col.find_one({"_id": user_id}) is not None

def register_user(user_id, name):
    if check_registered(user_id): 
        update_username(user_id, name)
        return False
    user = {
        "_id": user_id, "name": name, "balance": 500, "bank_balance": 0,    
        "loan": 0, "titles": [], "kills": 0, "protection": 0, "is_dead": False      
    } 
    users_col.insert_one(user)
    return True

def get_user(user_id):
    return users_col.find_one({"_id": user_id})

def update_balance(user_id, amount):
    users_col.update_one({"_id": user_id}, {"$inc": {"balance": amount}}, upsert=True)

def get_balance(user_id):
    user = users_col.find_one({"_id": user_id})
    return user["balance"] if user else 0

# --- 2. BANK & LOAN ---

def get_bank_balance(user_id):
    user = users_col.find_one({"_id": user_id})
    return user.get("bank_balance", 0) if user else 0

def update_bank_balance(user_id, amount):
    users_col.update_one({"_id": user_id}, {"$inc": {"bank_balance": amount}}, upsert=True)

def get_loan(user_id):
    user = users_col.find_one({"_id": user_id})
    return user.get("loan", 0) if user else 0

def set_loan(user_id, amount):
    users_col.update_one({"_id": user_id}, {"$set": {"loan": amount}}, upsert=True)

# --- 3. RPG STATUS ---

def update_kill_count(user_id):
    users_col.update_one({"_id": user_id}, {"$inc": {"kills": 1}}, upsert=True)

def set_dead(user_id, status: bool):
    users_col.update_one({"_id": user_id}, {"$set": {"is_dead": status}}, upsert=True)

def is_dead(user_id):
    user = users_col.find_one({"_id": user_id})
    return user.get("is_dead", False) if user else False

def set_protection(user_id, duration_hours):
    expiry = time.time() + (duration_hours * 3600)
    users_col.update_one({"_id": user_id}, {"$set": {"protection": expiry}}, upsert=True)

def is_protected(user_id):
    user = users_col.find_one({"_id": user_id})
    if not user or "protection" not in user: return False
    return time.time() < user["protection"]

# --- 4. MODERATION (BAN/MUTE) ---

def mute_user_db(group_id, user_id, duration_mins=None):
    expiry = (time.time() + (duration_mins * 60)) if duration_mins else None
    mutes_col.update_one({"group_id": group_id, "user_id": user_id}, {"$set": {"expiry": expiry}}, upsert=True)

def unmute_user_db(group_id, user_id):
    mutes_col.delete_one({"group_id": group_id, "user_id": user_id})

def is_user_muted(group_id, user_id):
    data = mutes_col.find_one({"group_id": group_id, "user_id": user_id})
    if not data: return False
    if data["expiry"] and time.time() > data["expiry"]:
        unmute_user_db(group_id, user_id)
        return False
    return True

def ban_user_db(group_id, user_id, reason="Admin Action"):
    bans_col.update_one({"group_id": group_id, "user_id": user_id}, {"$set": {"reason": reason, "time": time.time()}}, upsert=True)

def unban_user_db(group_id, user_id):
    bans_col.delete_one({"group_id": group_id, "user_id": user_id})

def is_user_banned(group_id, user_id):
    return bans_col.find_one({"group_id": group_id, "user_id": user_id}) is not None

def add_warning(group_id, user_id):
    data = warnings_col.find_one({"group_id": group_id, "user_id": user_id})
    if data:
        new_count = data["count"] + 1
        warnings_col.update_one({"_id": data["_id"]}, {"$set": {"count": new_count}})
        return new_count
    else:
        warnings_col.insert_one({"group_id": group_id, "user_id": user_id, "count": 1})
        return 1

def remove_warning(group_id, user_id):
    data = warnings_col.find_one({"group_id": group_id, "user_id": user_id})
    if data and data["count"] > 0:
        new_count = data["count"] - 1
        if new_count == 0: warnings_col.delete_one({"_id": data["_id"]})
        else: warnings_col.update_one({"_id": data["_id"]}, {"$set": {"count": new_count}})
        return new_count
    return 0

def reset_warnings(group_id, user_id):
    warnings_col.delete_one({"group_id": group_id, "user_id": user_id})

# --- 5. WORDSEEK GAME SCORES ---

def update_wordseek_score(user_id, name, points, group_id):
    wordseek_col.update_one({"_id": user_id}, {"$inc": {"global_score": points}, "$set": {"name": name}}, upsert=True)
    wordseek_col.update_one({"_id": user_id}, {"$inc": {f"group_scores.{group_id}": points}})

def get_wordseek_leaderboard(group_id=None):
    if group_id:
        cursor = wordseek_col.find({f"group_scores.{group_id}": {"$exists": True}})
        data = list(cursor)
        data.sort(key=lambda x: x.get("group_scores", {}).get(str(group_id), 0), reverse=True)
        return data[:10]
    else:
        cursor = wordseek_col.find().sort("global_score", -1).limit(10)
        return list(cursor)

# --- 6. ADMIN ---

def get_economy_status():
    status = settings_col.find_one({"_id": "economy_status"})
    return status["active"] if status else True

def set_economy_status(status: bool):
    settings_col.update_one({"_id": "economy_status"}, {"$set": {"active": status}}, upsert=True)

def wipe_database():
    cols = [users_col, investments_col, wordseek_col, warnings_col, packs_col, chat_stats_col, groups_col, mutes_col, bans_col]
    for col in cols: col.delete_many({})
    return True

# --- 7. API KEYS (with whitespace fix) ---

def add_api_key(api_key):
    clean_key = api_key.strip()
    if keys_col.find_one({"key": clean_key}): return False 
    keys_col.insert_one({"key": clean_key})
    return True
def remove_api_key(api_key): return keys_col.delete_one({"key": api_key.strip()}).deleted_count > 0
def get_all_keys(): return [k["key"] for k in list(keys_col.find({}, {"_id": 0, "key": 1}))]

def add_voice_key(api_key):
    clean_key = api_key.strip()
    if voice_keys_col.find_one({"key": clean_key}): return False 
    voice_keys_col.insert_one({"key": clean_key})
    return True
def remove_voice_key(api_key): return voice_keys_col.delete_one({"key": api_key.strip()}).deleted_count > 0
def get_all_voice_keys(): return [k["key"] for k in list(voice_keys_col.find({}, {"_id": 0, "key": 1}))]
def set_custom_voice(voice_id): settings_col.update_one({"_id": "voice_settings"}, {"$set": {"voice_id": voice_id.strip()}}, upsert=True)
def get_custom_voice():
    data = settings_col.find_one({"_id": "voice_settings"})
    return data["voice_id"] if data else "21m00Tcm4TlvDq8ikWAM"

def add_game_key(api_key):
    clean_key = api_key.strip()
    if game_keys_col.find_one({"key": clean_key}): return False 
    game_keys_col.insert_one({"key": clean_key})
    return True
def remove_game_key(api_key): return game_keys_col.delete_one({"key": api_key.strip()}).deleted_count > 0
def get_game_keys(): return [k["key"] for k in list(game_keys_col.find({}, {"_id": 0, "key": 1}))]

# --- 8. STICKERS & STATS ---

def add_sticker_pack(pack_name):
    clean_pack = pack_name.strip()
    if not packs_col.find_one({"name": clean_pack}):
        packs_col.insert_one({"name": clean_pack})
        return True
    return False
def remove_sticker_pack(pack_name):
    if packs_col.find_one({"name": pack_name.strip()}):
        packs_col.delete_one({"name": pack_name.strip()})
        return True
    return False
def get_sticker_packs(): return [d["name"] for d in list(packs_col.find())]

def update_chat_stats(group_id, user_id, name):
    now = datetime.datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    week_str = now.strftime("%Y-%W")
    
    data = chat_stats_col.find_one({"group_id": group_id, "user_id": user_id})
    if not data:
        chat_stats_col.insert_one({
            "group_id": group_id, "user_id": user_id, "name": name, 
            "overall": 1, "today": 1, "week": 1,
            "last_date": today_str, "last_week": week_str
        })
    else:
        update_query = {"$inc": {"overall": 1}, "$set": {"name": name}}
        
        if data.get("last_date") != today_str:
            update_query["$set"]["today"] = 1
            update_query["$set"]["last_date"] = today_str
        else: update_query["$inc"]["today"] = 1
        
        if data.get("last_week") != week_str:
            update_query["$set"]["week"] = 1
            update_query["$set"]["last_week"] = week_str
        else: update_query["$inc"]["week"] = 1
            
        chat_stats_col.update_one({"_id": data["_id"]}, update_query)

def get_top_chatters(group_id, mode="overall"):
    sort_key = "overall" 
    if mode == "today": sort_key = "today"
    elif mode == "week": sort_key = "week"
    cursor = chat_stats_col.find({"group_id": group_id}).sort(sort_key, -1).limit(10)
    return list(cursor)

def get_total_messages(group_id):
    pipeline = [{"$match": {"group_id": group_id}}, {"$group": {"_id": None, "total": {"$sum": "$overall"}}}]
    result = list(chat_stats_col.aggregate(pipeline))
    return result[0]["total"] if result else 0

# --- 9. GROUPS & LOGGER ---

def update_group_activity(group_id, group_name):
    groups_col.update_one({"_id": group_id}, {"$set": {"name": group_name}, "$inc": {"activity": 1}}, upsert=True)

def remove_group(group_id): 
    groups_col.delete_one({"_id": group_id})

def get_group_price(group_id):
    grp = groups_col.find_one({"_id": group_id})
    if not grp: return 10.0
    return round(10 + (grp.get("activity", 0) * 0.1), 2)

def set_logger_group(group_id): settings_col.update_one({"_id": "logger_settings"}, {"$set": {"group_id": int(group_id)}}, upsert=True)

# 🔥 CHANGE 2: Updated Logic to check Config first
def get_logger_group():
    # Pehle Config Check karo
    if LOGGER_ID:
        return int(LOGGER_ID)
    
    # Agar Config me nahi hai toh Database check karo
    data = settings_col.find_one({"_id": "logger_settings"})
    return data["group_id"] if data else None

def delete_logger_group(): settings_col.delete_one({"_id": "logger_settings"})

# Global Counts
def get_total_users(): return users_col.count_documents({})
def get_total_groups(): return groups_col.count_documents({})

# --- ADD THIS TO database.py ---
# These functions are needed for Gchat/Gsticker settings

def set_group_setting(chat_id, setting_type, value):
    groups_col.update_one(
        {"chat_id": chat_id},
        {"$set": {f"settings.{setting_type}": value}},
        upsert=True
    )

def get_group_settings(chat_id):
    data = groups_col.find_one({"chat_id": chat_id})
    if not data or "settings" not in data:
        return {"chat_mode": True, "sticker_mode": True}
    
    settings = data.get("settings", {})
    return {
        "chat_mode": settings.get("chat_mode", True),
        "sticker_mode": settings.get("sticker_mode", True)
    }
    
