import os
import re
from os import getenv
from dotenv import load_dotenv

load_dotenv()

# =========================================
# 🤖 BOT & SESSION CONFIGURATION
# =========================================
API_ID = int(getenv("API_ID", "0"))
API_HASH = getenv("API_HASH", "")

# 🔥 Ye 3 nayi lines add karo:
OWNER_USERNAME = "@Prince_Username"  # Apna Username yahan daalo (bina @ ke bhi chalega string hai)
GROUP_NAME = "Prince Support"        # Apne Group ka naam
GROUP_LINK = "https://t.me/Kiwi_musicsupport" # Apne Group ka Link

# config.py
INSTAGRAM_LINK = "https://t.me/Kiwi_musicsupport" # Yahan apna link daal den

# --- FIX IS HERE ---
# Humne BOT_TOKEN define kiya, aur TELEGRAM_TOKEN ko uska copy bana diya
BOT_TOKEN = getenv("BOT_TOKEN") or getenv("TELEGRAM_TOKEN", "")
TELEGRAM_TOKEN = BOT_TOKEN  # <--- Ye line missing thi, ab add kar di hai ✅

SESSION = getenv("STRING_SESSION", "")

# =========================================
# 🗄️ DATABASE CONFIGURATION
# =========================================
MONGO_DB_URI = getenv("MONGO_DB_URI") or getenv("MONGO_URL", "")
MONGO_URL = MONGO_DB_URI # Alias for Main.py support

# =========================================
# 👑 OWNER & ASSISTANT CONFIGURATION
# =========================================
OWNER_IDS = [8560671423, 6356015122]

OWNER_ID = int(getenv("OWNER_ID", OWNER_IDS[0]))
OWNER_USERNAME = getenv("OWNER_USERNAME", "II_Mikey")
OWNER_NAME = getenv("OWNER_NAME", "mikey")

ASSISTANT_ID = int(getenv("ASSISTANT_ID", "8457855985"))
LOGGER_ID = int(getenv("LOGGER_ID", "-1003639584506"))
LOG_GROUP_ID = -1003639584506

BOT_NAME = getenv("BOT_NAME", "ℳ𝒾𝓈𝓈 𝒮𝒽𝒾𝓃𝒿𝓊 ")

# =========================================
# 🎮 GAME & ECONOMY SETTINGS
# =========================================
GRID_SIZE = 4
MAX_LOAN = 5000
LOAN_INTEREST = 0.10
DELETE_TIMER = 17 
DEFAULT_BANNER = "https://i.ibb.co/vzDpQx9/ranking-banner.jpg"

# =========================================
# 🎵 MUSIC LIMITS & SETTINGS
# =========================================
DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", "1000"))
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", "25"))
SONG_DOWNLOAD_DURATION = int(getenv("SONG_DOWNLOAD_DURATION", "9999999"))

# =========================================
# 🖼️ IMAGES
# =========================================
START_IMG_URL = getenv("START_IMG_URL", "https://files.catbox.moe/nob5yp.jpg")
PING_IMG_URL = getenv("PING_IMG_URL", "https://telegra.ph/file/7bb907999ea7156227283.jpg")
PLAYLIST_IMG_URL = "https://telegra.ph/file/d723f4c80da157fca1678.jpg"
STATS_IMG_URL = "https://telegra.ph/file/d30d11c4365c025c25e3e.jpg"
TELEGRAM_AUDIO_URL = "https://telegra.ph/file/13afb9ee5c5da17930f1e.png"
TELEGRAM_VIDEO_URL = "https://telegra.ph/file/13afb9ee5c5da17930f1e.png"
STREAM_IMG_URL = "https://telegra.ph/file/03efec694e41e891b29dc.jpg"
SOUNCLOUD_IMG_URL = "https://telegra.ph/file/d723f4c80da157fca1678.jpg"
YOUTUBE_IMG_URL = "https://telegra.ph/file/4dc854f961cd3ce46899b.jpg"
SPOTIFY_ARTIST_IMG_URL = "https://telegra.ph/file/d723f4c80da157fca1678.jpg"
SPOTIFY_ALBUM_IMG_URL = "https://telegra.ph/file/6c741a6bc1e1663ac96fc.jpg"
SPOTIFY_PLAYLIST_IMG_URL = "https://telegra.ph/file/6c741a6bc1e1663ac96fc.jpg"

# =========================================
# 🛠️ HELPER FUNCTIONS & RUNTIME VARS
# =========================================
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))

DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))

BANNED_USERS = []
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}

SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/hehe_heeeeee")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/hehe_heeeeee")
UPDATE_CHANNEL = "https://t.me/Kiwi_musicsupport"

if SUPPORT_CHANNEL and not re.match("(?:http|https)://", SUPPORT_CHANNEL):
    print("[WARN] - Your SUPPORT_CHANNEL url is wrong.")
    
