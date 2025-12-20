from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
import random
import asyncio

# Imports
from config import TELEGRAM_TOKEN
from database import update_wordseek_score, get_wordseek_leaderboard

# GAME STATE
active_games = {}

# --- 🔥 WORD LIST (OFFLINE DATA) ---
# Strictly 5-Letter Words
WORD_LIST = [
    {"word": "APPLE", "phonetic": "/ˈæp.əl/", "meaning": "A round fruit with red or green skin."},
    {"word": "TIGER", "phonetic": "/ˈtaɪ.ɡər/", "meaning": "A large wild cat with stripes."},
    {"word": "BREAD", "phonetic": "/bred/", "meaning": "Baked food made of flour and water."},
    {"word": "CHAIR", "phonetic": "/tʃeər/", "meaning": "A seat with a back and legs."},
    {"word": "SMILE", "phonetic": "/smaɪl/", "meaning": "A happy expression on the face."},
    {"word": "BEACH", "phonetic": "/biːtʃ/", "meaning": "Sandy area next to the sea."},
    {"word": "DREAM", "phonetic": "/driːm/", "meaning": "Images in mind while sleeping."},
    {"word": "LIGHT", "phonetic": "/laɪt/", "meaning": "Makes things visible."},
    {"word": "HEART", "phonetic": "/hɑːt/", "meaning": "Organ that pumps blood."},
    {"word": "WATCH", "phonetic": "/wɒtʃ/", "meaning": "Small clock worn on wrist."},
    {"word": "WATER", "phonetic": "/ˈwɔː.tər/", "meaning": "Clear liquid essential for life."},
    {"word": "MUSIC", "phonetic": "/ˈmjuː.zɪk/", "meaning": "Sounds arranged in a pleasing way."},
    {"word": "MONEY", "phonetic": "/ˈmʌn.i/", "meaning": "Coins or notes used to buy things."},
    {"word": "HOUSE", "phonetic": "/haʊs/", "meaning": "Building for people to live in."},
    {"word": "WORLD", "phonetic": "/wɜːld/", "meaning": "The earth and all people on it."},
    {"word": "PHONE", "phonetic": "/fəʊn/", "meaning": "Device used to talk to others."},
    {"word": "TABLE", "phonetic": "/ˈteɪ.bəl/", "meaning": "Furniture with a flat top and legs."},
    {"word": "PAPER", "phonetic": "/ˈpeɪ.pər/", "meaning": "Material used for writing or printing."},
    {"word": "RIVER", "phonetic": "/ˈrɪv.ər/", "meaning": "Large natural stream of water."},
    {"word": "NIGHT", "phonetic": "/naɪt/", "meaning": "Time when it is dark."},
    {"word": "HAPPY", "phonetic": "/ˈhæp.i/", "meaning": "Feeling or showing pleasure."},
    {"word": "GREEN", "phonetic": "/ɡriːn/", "meaning": "Color of grass and leaves."},
    {"word": "QUICK", "phonetic": "/kwɪk/", "meaning": "Moving fast or doing something fast."},
    {"word": "ZEBRA", "phonetic": "/ˈzeb.rə/", "meaning": "African wild horse with black and white stripes."},
    {"word": "CLOUD", "phonetic": "/klaʊd/", "meaning": "White or grey mass in the sky."},
    {"word": "SNAKE", "phonetic": "/sneɪk/", "meaning": "Long reptile with no legs."},
    {"word": "GHOST", "phonetic": "/ɡəʊst/", "meaning": "Spirit of a dead person."},
    {"word": "ROBOT", "phonetic": "/ˈrəʊ.bɒt/", "meaning": "Machine controlled by computer."},
    {"word": "PIZZA", "phonetic": "/ˈpiːt.sə/", "meaning": "Italian dish with dough, cheese, and tomato."},
    {"word": "QUEEN", "phonetic": "/kwiːn/", "meaning": "Female ruler of a country."}
]

# --- 🔥 AUTO END JOB (5 Min Timeout) ---
async def auto_end_job(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.data
    
    if chat_id in active_games:
        game = active_games[chat_id]
        target_word = game['target']
        
        del active_games[chat_id]
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"⏰ **Time's Up!**\nGame end kar diya gaya.\n\n📝 Correct Word: **{target_word}**",
            parse_mode=ParseMode.MARKDOWN
        )

# --- HELPER: GENERATE GRID ---
def generate_grid_string(target, guesses):
    target = target.upper()
    grid_msg = ""

    for guess in guesses:
        guess = guess.upper()
        row_emoji = ""
        
        # Wordle Logic
        for i, char in enumerate(guess):
            if char == target[i]:
                row_emoji += "🟩"
            elif char in target:
                row_emoji += "🟨"
            else:
                row_emoji += "🟥"
        
        formatted_word = " ".join(list(guess))
        grid_msg += f"{row_emoji}   `{formatted_word}`\n"
        
    return grid_msg

# --- COMMANDS ---

async def start_wordseek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    if chat_id in active_games:
        await update.message.reply_text("⚠️ Game pehle se chal raha hai! `/end` karo ya guess karo.")
        return

    # 🔥 DIRECT SELECTION (NO LOADING)
    word_data = random.choice(WORD_LIST)

    # Timer Start (5 Mins)
    timer_job = context.job_queue.run_once(auto_end_job, 300, data=chat_id)

    msg = await update.message.reply_text("🎮 **Starting Word Challenge...**")

    active_games[chat_id] = {
        "target": word_data['word'].upper(),
        "data": word_data,
        "guesses": [],
        "message_id": msg.message_id,
        "timer_job": timer_job 
    }
    
    length = len(word_data['word'])
    hint = word_data['meaning']

    text = (
        f"🔥 **WORD GRID CHALLENGE** 🔥\n\n"
        f"🔡 Word Length: **{length} Letters**\n"
        f"👇 *Guess the word below!*\n\n"
        f"> 💡 **Hint:** {hint}"
    )
    
    await msg.edit_text(text, parse_mode=ParseMode.MARKDOWN)

async def stop_wordseek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in active_games:
        # Stop Timer
        job = active_games[chat_id].get("timer_job")
        if job: job.schedule_removal()
        
        del active_games[chat_id]
        await update.message.reply_text("🛑 **Game Ended!**")
    else:
        await update.message.reply_text("❌ Koi game nahi chal raha.")

# --- GUESS HANDLER ---
async def handle_word_guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.id not in active_games: return
    
    game = active_games[chat.id]
    target = game['target']
    user_guess = update.message.text.strip().upper()
    
    # Validation
    if len(user_guess) != len(target): return

    if user_guess in game['guesses']:
        await update.message.reply_text("Someone has already guessed your word. Please try another one!", quote=True)
        return

    # 🔥 RESET TIMER
    old_job = game.get("timer_job")
    if old_job: old_job.schedule_removal()
    new_job = context.job_queue.run_once(auto_end_job, 300, data=chat.id)
    game['timer_job'] = new_job

    game['guesses'].append(user_guess)
    
    # WIN SCENARIO
    if user_guess == target:
        user = update.effective_user
        points = 9
        update_wordseek_score(user.id, user.first_name, points, str(chat.id))
        
        # Stop Timer
        if new_job: new_job.schedule_removal()
        
        data = game['data']
        del active_games[chat.id]
        
        await update.message.reply_text(
            f"🚬 ~ ` {user.first_name} ` ~ 🍷\n"
            f"{user_guess.title()}\n\n"
            f"Congrats! You guessed it correctly.\n"
            f"Added {points} to the leaderboard.\n"
            f"Start with /new\n\n"
            f"> **Correct Word:** {data['word']}\n"
            f"> **{data['word']}** {data.get('phonetic', '')}\n"
            f"> **Meaning:** {data['meaning']}",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        # WRONG GUESS - UPDATE GRID
        try:
            grid_text = generate_grid_string(target, game['guesses'])
            hint = game['data']['meaning']
            
            new_text = (
                f"🔥 **WORD GRID CHALLENGE** 🔥\n\n"
                f"{grid_text}\n"
                f"> 💡 **Hint:** {hint}"
            )
            
            await context.bot.edit_message_text(
                chat_id=chat.id,
                message_id=game['message_id'],
                text=new_text,
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception: pass

# --- LEADERBOARD ---
async def wordseek_rank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("🌍 Global Top", callback_data="wrank_global"), InlineKeyboardButton("👥 Group Top", callback_data="wrank_group")]]
    await update.message.reply_text("🏆 **WordSeek Leaderboard**\nSelect Category 👇", reply_markup=InlineKeyboardMarkup(kb))

async def wordseek_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data
    
    if data.startswith("wrank_"):
        mode = data.split("_")[1]
        group_id = str(update.effective_chat.id) if mode == "group" else None
        
        leaderboard = get_wordseek_leaderboard(group_id)
        title = "🌍 Global" if mode == "global" else "👥 Group"
        msg = f"🏆 **{title} Leaderboard** 🏆\n\n"
        
        if not leaderboard: msg += "❌ No Data Found!"
        else:
            for i, p in enumerate(leaderboard, 1):
                score = p.get('global_score', 0) if mode == "global" else p.get('group_scores', {}).get(group_id, 0)
                msg += f"{i}. {p['name']} - 💎 {score}\n"
        
        kb = [[InlineKeyboardButton("🔙 Back", callback_data="close_wrank")]]
        await q.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

    if data == "close_wrank": await q.message.delete()
