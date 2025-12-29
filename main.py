import random
import os
import importlib 
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# IMPORTS
from config import TELEGRAM_TOKEN, BOT_NAME 
from database import (
    users_col, codes_col, update_balance, get_balance, 
    check_registered, register_user, update_group_activity, 
    update_username, update_chat_stats,
    is_user_muted, is_user_banned,
    get_logger_group,
    set_group_setting, get_group_settings 
)
from ai_chat import get_yuki_response, get_mimi_sticker
from tts import generate_voice 

# ✅ Music Assistant Import
from tools.stream import start_music_worker
import tools.stream 

# MODULES 
import admin, start, group, leaderboard, pay, bet, wordseek, chatstat, logger, events, info, tictactoe, couple
import livetime  
import dmspam 
import bank 
from bank import check_balance 
from antispam import check_spam
import wordgrid 

# --- FLASK SERVER ---
app = Flask('')
@app.route('/')
def home(): return "I am Alive! 24/7"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): t = Thread(target=run); t.start()

# VARS
SHOP_ITEMS = {
    "vip":   {"name": "👑 VIP", "price": 10000},
    "god":   {"name": "⚡ God", "price": 50000},
    "rich":  {"name": "💸 Rich", "price": 100000}
}

# --- 🔌 AUTO LOADER FUNCTION ---
def load_plugins(application: Application):
    plugin_dir = "tools"
    if not os.path.exists(plugin_dir):
        try: os.makedirs(plugin_dir); print(f"📁 Created '{plugin_dir}' directory.")
        except: pass
        return

    path_list = [f for f in os.listdir(plugin_dir) if f.endswith(".py") and f != "__init__.py"]
    print(f"🔌 Loading {len(path_list)} plugins from '{plugin_dir}'...")

    for file in path_list:
        module_name = file[:-3]
        try:
            module = importlib.import_module(f"{plugin_dir}.{module_name}")
            if hasattr(module, "register_handlers"):
                module.register_handlers(application)
                print(f"  ✅ Loaded: {module_name}")
        except Exception as e:
            print(f"  ❌ FAILED to load {module_name}!")
            print(f"     Error: {e}")

# --- STARTUP MESSAGE ---
async def on_startup(application: Application):
    print(f"🚀 {BOT_NAME} IS STARTING...")
    print("🔵 Starting Music Assistant...")
    try: await start_music_worker()
    except Exception as e: print(f"❌ Assistant Start Failed: {e}")

    logger_id = get_logger_group()
    if logger_id:
        try:
            me = await application.bot.get_me()
            txt = f"<blockquote><b>{BOT_NAME}ʙᴏᴛ active 🍭</b></blockquote>\n@{me.username}"
            await application.bot.send_message(chat_id=logger_id, text=txt, parse_mode=ParseMode.HTML)
        except Exception as e: 
            print(f"⚠️ Logger Error: {e}")

# --- ⚙️ NEW COMMANDS: GCHAT & GSTICKER (STYLED) ---

async def toggle_gchat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    
    # Admin Check
    if chat.type in ["group", "supergroup"]:
        member = await chat.get_member(user.id)
        if member.status not in ["administrator", "creator"]:
            return await update.message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴄʜᴀɴɢᴇ ᴛʜɪꜱ ꜱᴇᴛᴛɪɴɢ!")

    if not context.args:
        return await update.message.reply_text("⚠️ ᴜꜱᴀɢᴇ: `/ɢᴄʜᴀᴛ ᴏɴ` ᴏʀ `/ɢᴄʜᴀᴛ ᴏꜰꜰ`")

    state = context.args[0].lower()
    if state == "on":
        set_group_setting(chat.id, "chat_mode", True)
        await update.message.reply_text(f"✅ **ᴄʜᴀᴛ ᴍᴏᴅᴇ ᴇɴᴀʙʟᴇᴅ!**\nɪ ᴡɪʟʟ ᴛᴀʟᴋ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ ɴᴏᴡ.")
    elif state == "off":
        set_group_setting(chat.id, "chat_mode", False)
        await update.message.reply_text(f"🔇 **ᴄʜᴀᴛ ᴍᴏᴅᴇ ᴅɪꜱᴀʙʟᴇᴅ!**\nɪ ᴡɪʟʟ ʙᴇ ǫᴜɪᴇᴛ ɴᴏᴡ.")
    else:
        await update.message.reply_text("⚠️ ᴜꜱᴀɢᴇ: `/ɢᴄʜᴀᴛ ᴏɴ` ᴏʀ `/ɢᴄʜᴀᴛ ᴏꜰꜰ`")

async def toggle_gsticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    # Admin Check
    if chat.type in ["group", "supergroup"]:
        member = await chat.get_member(user.id)
        if member.status not in ["administrator", "creator"]:
            return await update.message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴄʜᴀɴɢᴇ ᴛʜɪꜱ ꜱᴇᴛᴛɪɴɢ!")

    if not context.args:
        return await update.message.reply_text("⚠️ ᴜꜱᴀɢᴇ: `/ɢꜱᴛɪᴄᴋᴇʀ ᴏɴ` ᴏʀ `/ɢꜱᴛɪᴄᴋᴇʀ ᴏꜰꜰ`")

    state = context.args[0].lower()
    if state == "on":
        set_group_setting(chat.id, "sticker_mode", True)
        await update.message.reply_text(f"✅ **ꜱᴛɪᴄᴋᴇʀ ᴍᴏᴅᴇ ᴇɴᴀʙʟᴇᴅ!**\nɪ ᴡɪʟʟ ʀᴇᴘʟʏ ᴡɪᴛʜ ꜱᴛɪᴄᴋᴇʀꜱ.")
    elif state == "off":
        set_group_setting(chat.id, "sticker_mode", False)
        await update.message.reply_text(f"🚫 **ꜱᴛɪᴄᴋᴇʀ ᴍᴏᴅᴇ ᴅɪꜱᴀʙʟᴇᴅ!**\nɴᴏ ᴍᴏʀᴇ ꜱᴛɪᴄᴋᴇʀꜱ ɪɴ ʀᴇᴘʟʏ.")
    else:
        await update.message.reply_text("⚠️ ᴜꜱᴀɢᴇ: `/ɢꜱᴛɪᴄᴋᴇʀ ᴏɴ` ᴏʀ `/ɢꜱᴛɪᴄᴋᴇʀ ᴏꜰꜰ`")

# --- SHOP MENU ---
async def shop_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        uid = update.callback_query.from_user.id
        msg_func = update.callback_query.message.edit_text 
    else:
        uid = update.effective_user.id
        msg_func = update.message.reply_text

    kb = []
    for k, v in SHOP_ITEMS.items():
        kb.append([InlineKeyboardButton(f"{v['name']} - ₹{v['price']}", callback_data=f"buy_{k}_{uid}")])
    kb.append([InlineKeyboardButton("🔙 Back", callback_data="back_home")])
    await msg_func("🛒 **VIP SHOP**\nBuy special titles here:", reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

async def redeem_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not context.args: return await update.message.reply_text("⚠️ Usage: `/redeem CODE`")
    code = context.args[0]
    data = codes_col.find_one({"code": code})
    if not data: return await update.message.reply_text("❌ Invalid Code!")
    if user.id in data["redeemed_by"]: return await update.message.reply_text("⚠️ Already Redeemed!")
    
    update_balance(user.id, data["amount"])
    codes_col.update_one({"code": code}, {"$push": {"redeemed_by": user.id}})
    await update.message.reply_text(f"🎉 Redeemed ₹{data['amount']}!")

# --- CALLBACK HANDLER ---
async def callback_handler(update, context):
    q = update.callback_query
    data = q.data
    uid = q.from_user.id
    chat_id = update.effective_chat.id
    
    # 🔥 1. MUSIC PLAYER CONTROLS
    if data.startswith("music_"):
        await q.answer()
        action = data.split("_")[1]
        
        if action == "pause":
            await tools.stream.pause_stream(chat_id)
            await q.message.reply_text("II Stream Paused", quote=True)
        elif action == "resume":
            await tools.stream.resume_stream(chat_id)
            await q.message.reply_text("▶ Stream Resumed", quote=True)
        elif action == "skip":
            await tools.stream.skip_stream(chat_id)
            await q.message.reply_text("⏭ Skipped", quote=True)
        elif action == "stop":
            await tools.stream.stop_stream(chat_id)
            await q.message.delete()
            await q.message.reply_text("⏹ Stream Stopped", quote=True)
        return

    # 🔥 2. FORCE CLOSE
    if data == "force_close":
        try: await q.message.delete()
        except: await q.answer("❌ Delete nahi kar sakta!", show_alert=True)
        return

    # --- STANDARD HANDLERS ---
    if data in ["close_log", "close_ping"]:
        try: await q.message.delete()
        except: pass
        return

    if data == "help_main" or data.startswith("help_"):
        await start.start_callback(update, context)
        return

    if data == "back_home":
        await q.answer()
        await start.start_callback(update, context)
        return

    if data == "open_shop":
        await q.answer()
        await shop_menu(update, context)
        return
    
    if data == "open_games":
        await q.answer()
        kb = [[InlineKeyboardButton("🔙 Back", callback_data="back_home")]]
        msg = "🎮 **GAME MENU**\n\n🎲 `/bet` - Bomb Game\n🔠 `/new` - Word Seek\n🔠 `/wordgrid` - Word Grid\n❌ `/zero` - Tic Tac Toe\n💰 `/invest` - Stock Market"
        await q.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
        return

    if data == "open_ranking":
        await q.answer()
        await leaderboard.user_leaderboard(update, context) 
        return

    if data.startswith(("start_", "st_")):
        await start.start_callback(update, context)
        return

    if data.startswith("admin_"):
        await admin.admin_callback(update, context)
        return

    if data.startswith(("wrank_", "new_wordseek_", "close_wrank", "end_wordseek")):
        await wordseek.wordseek_callback(update, context)
        return

    if data.startswith(("rank_", "hide_rank")):
        await chatstat.rank_callback(update, context)
        return
        
    if data.startswith(("set_", "clk_", "cash_", "close_", "noop_", "rebet_")):
        await bet.bet_callback(update, context)
        return

    if data.startswith("ttt_"):
        await tictactoe.ttt_callback(update, context)
        return

    if data.startswith("reg_start_"):
        if uid != int(data.split("_")[2]): return await q.answer("Not for you!", show_alert=True)
        if register_user(uid, q.from_user.first_name): await q.edit_message_text("✅ Registered!")
        else: await q.answer("Already registered!")
        return

    if data.startswith("buy_"):
        parts = data.split("_")
        if uid != int(parts[2]): return await q.answer("Not for you!", show_alert=True)
        item = SHOP_ITEMS.get(parts[1])
        if get_balance(uid) < item["price"]: return await q.answer("No Money!", show_alert=True)
        update_balance(uid, -item["price"])
        users_col.update_one({"_id": uid}, {"$push": {"titles": item["name"]}})
        await q.answer(f"Bought {item['name']}!")
        return
    
    if data.startswith("revive_"):
        await pay.revive_callback(update, context)
        return
        
    if data == "giveup_wordgrid":
        await wordgrid.give_up(update, context)
        return
        
    if data.startswith("grid_"):
        await wordgrid.grid_callback(update, context)
        return

    if data == "close_time":
        await livetime.close_time(update, context)
        return

# --- MESSAGE HANDLER (UPDATED FOR COMPLETE SILENCE) ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    user = update.effective_user
    chat = update.effective_chat
    
    # 0. DM SPAM PROTECTION
    if chat.type == "private":
        spam_status = dmspam.check_spam(user.id)
        if spam_status == "BLOCKED": return 
        elif spam_status == "NEW_BLOCK":
            await update.message.reply_text("🚫 **Spam mat kar bhai!**\n5 minute ke liye block kiya ja raha hai.")
            return 

    # 1. ENFORCEMENT
    if chat.type in ["group", "supergroup"] and not user.is_bot:
        if is_user_banned(chat.id, user.id) or is_user_muted(chat.id, user.id):
            try: await update.message.delete()
            except: pass
            return

    # 2. GLOBAL ANTI-SPAM
    if not user.is_bot:
        status = check_spam(user.id)
        if status == "BLOCKED":
            await update.message.reply_text(f"🚫 **Spam Detected!**\n{user.first_name}, blocked for 8 mins.")
            return

    # 3. STATS
    update_username(user.id, user.first_name)
    if chat.type in ["group", "supergroup"] and not user.is_bot:
        update_chat_stats(chat.id, user.id, user.first_name)
        update_group_activity(chat.id, chat.title)

    # 4. ADMIN & GAMES
    if await admin.handle_admin_input(update, context): return
    await wordseek.handle_word_guess(update, context)
    await wordgrid.handle_word_guess(update, context)

    # 🛑 SETTINGS CHECK (DATABASE SE)
    settings = get_group_settings(chat.id)
    chat_enabled = settings["chat_mode"]
    sticker_enabled = settings["sticker_mode"]

    # 5. STICKER REPLY
    if update.message.sticker:
        # Agar Sticker Mode OFF hai, toh ignore karo
        if not sticker_enabled:
            return

        if chat.type == "private" or (update.message.reply_to_message and update.message.reply_to_message.from_user.id == context.bot.id) or random.random() < 0.2:
            sticker_id = await get_mimi_sticker(context.bot)
            if sticker_id: await update.message.reply_sticker(sticker_id)
        return

    # 6. TEXT & VOICE AI
    text = update.message.text
    if not text: return

    # 🔥 COMPLETE SILENCE LOGIC
    # Agar Private Chat nahi hai aur Chat Mode OFF hai -> RETURN KAR DO (Bilkul Chup)
    if chat.type != "private" and not chat_enabled:
        return 

    # Normal AI Logic
    should_reply = False
    if chat.type == "private": should_reply = True
    elif any(trigger in text.lower() for trigger in ["aniya", context.bot.username.lower()]): should_reply = True
    elif update.message.reply_to_message and update.message.reply_to_message.from_user.id == context.bot.id: should_reply = True

    if should_reply:
        voice_triggers = ["voice", "note", "moh", "audio", "gn", "gm", "rec","kaho"]
        wants_voice = any(v in text.lower() for v in voice_triggers)

        await context.bot.send_chat_action(chat_id=chat.id, action="typing")
        
        # 🔥 AI Response + Reaction (Async)
        ai_reply = await get_yuki_response(user.id, text, user.first_name, update.message)

        if wants_voice:
            await context.bot.send_chat_action(chat_id=chat.id, action="record_voice")
            audio_path = await generate_voice(ai_reply)
            
            if audio_path:
                try:
                    with open(audio_path, 'rb') as voice_file:
                        await update.message.reply_voice(voice=voice_file)
                    os.remove(audio_path)
                    return
                except: await update.message.reply_text(ai_reply)
            else: await update.message.reply_text(ai_reply)
        else:
            await update.message.reply_text(ai_reply)

# --- MAIN ENGINE ---
def main():
    keep_alive()
    app = Application.builder().token(TELEGRAM_TOKEN).post_init(on_startup).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start.start))
    app.add_handler(CommandHandler("admin", admin.admin_panel))
    app.add_handler(CommandHandler("info", info.user_info))
    app.add_handler(CommandHandler("love", info.love_calculator))
    app.add_handler(CommandHandler("stupid", info.stupid_meter))
    app.add_handler(CommandHandler("couple", couple.couple_check))
    app.add_handler(CommandHandler("bal", check_balance))
    app.add_handler(CommandHandler("redeem", redeem_code))
    app.add_handler(CommandHandler("shop", shop_menu))
    app.add_handler(CommandHandler("top", leaderboard.user_leaderboard))
    app.add_handler(CommandHandler("ranking", group.ranking))
    app.add_handler(CommandHandler("stats", logger.stats_bot))
    app.add_handler(CommandHandler("ping", logger.ping_bot))
    app.add_handler(CommandHandler("bet", bet.bet_menu))
    app.add_handler(CommandHandler("new", wordseek.start_wordseek))
    app.add_handler(CommandHandler("wordgrid", wordgrid.start_wordgrid))
    app.add_handler(CommandHandler("zero", tictactoe.start_ttt))
    app.add_handler(CommandHandler("market", group.market_info))
    app.add_handler(CommandHandler("invest", group.invest))
    app.add_handler(CommandHandler("sell", group.sell_shares))
    app.add_handler(CommandHandler("topinvest", group.top_investors))
    app.add_handler(CommandHandler("bank", bank.bank_info))
    app.add_handler(CommandHandler("deposit", bank.deposit))
    app.add_handler(CommandHandler("withdraw", bank.withdraw))
    app.add_handler(CommandHandler("loan", bank.take_loan))
    app.add_handler(CommandHandler("payloan", bank.repay_loan))
    app.add_handler(CommandHandler("pay", pay.pay_user))
    app.add_handler(CommandHandler("rob", pay.rob_user))
    app.add_handler(CommandHandler("kill", pay.kill_user))
    app.add_handler(CommandHandler("protect", pay.protect_user))
    app.add_handler(CommandHandler("alive", pay.check_status))
    app.add_handler(CommandHandler("time", livetime.start_live_time))
    app.add_handler(MessageHandler(filters.Regex(r'^[\./]time'), livetime.start_live_time))

    # ✅ REGISTER NEW COMMANDS
    app.add_handler(CommandHandler(["gchat", "Gchat"], toggle_gchat))
    app.add_handler(CommandHandler(["gsticker", "Gsticker"], toggle_gsticker))

    app.add_handler(CallbackQueryHandler(callback_handler))
    
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, events.welcome_user))
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, events.track_leave))
    app.add_handler(MessageHandler(filters.StatusUpdate.VIDEO_CHAT_STARTED, events.vc_handler))
    app.add_handler(MessageHandler(filters.StatusUpdate.VIDEO_CHAT_ENDED, events.vc_handler))
    app.add_handler(MessageHandler(filters.StatusUpdate.VIDEO_CHAT_PARTICIPANTS_INVITED, events.vc_handler))
    
    app.add_handler(MessageHandler(filters.Regex(r'(?i)^[\./]crank'), chatstat.show_leaderboard))
    
    # 🔥 Plugins LOAD (Music vagera)
    load_plugins(app)

    # Note: 'handle_message' catches ALL text, so it must be last
    app.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), handle_message))
    
    print(f"🚀 {BOT_NAME} STARTED SUCCESSFULLY!")
    app.run_polling()

if __name__ == "__main__":
    main()
                                               
