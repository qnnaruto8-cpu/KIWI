import os

# ⚙️ CONFIGURATION
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") 
MONGO_URL = os.getenv("MONGO_URL")
OWNER_ID = 7453179290  # Tumhara (Owner) Telegram ID

# 🤖 AI CHAT CONFIG
OWNER_NAME = "BOSS JI"  # Yahan apna naam likho (Yuki tumhe is naam se bulayegi)

# 🎮 GAME SETTINGS
GRID_SIZE = 4
MAX_LOAN = 5000
LOAN_INTEREST = 0.10
DELETE_TIMER = 17  # Result message kitne seconds baad delete hoga

# 🏆 RANKING IMAGE
# Agar top group ki photo nahi milti toh ye default image dikhegi
DEFAULT_BANNER = "https://i.ibb.co/vzDpQx9/ranking-banner.jpg"

