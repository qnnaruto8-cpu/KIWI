import random
import asyncio
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, Application, CommandHandler, CallbackQueryHandler
from telegram.error import BadRequest, Forbidden, TelegramError

# Database imports (agar aapke pass database.py hai)
from database import users_col, get_balance

# Global variables
active_tag_sessions = {}  # Format: {chat_id: {"stop": False, "tagged": 0}}

# EMOJI and MESSAGES (same as before)
EMOJI = [
    "🦋🦋🦋🦋🦋", "🧚🌸🧋🍬🫖", "🥀🌷🌹🌺💐", "🌸🌿💮🌱🌵",
    "❤️💚💙💜🖤", "💓💕💞💗💖", "🌸💐🌺🌹🦋", "🍔🦪🍛🍲🥗",
    "🍎🍓🍒🍑🌶️", "🧋🥤🧋🥛🍷", "🍬🍭🧁🎂🍡", "🍨🧉🍺☕🍻",
    "🥪🥧🍦🍥🍚", "🫖☕🍹🍷🥛", "☕🧃🍩🍦🍙", "🍁🌾💮🍂🌿",
    "🌨️🌥️⛈️🌩️🌧️", "🌷🏵️🌸🌺💐", "💮🌼🌻🍀🍁", "🧟🦸🦹🧙👸",
    "🧅🍠🥕🌽🥦", "🐷🐹🐭🐨🐻‍❄️", "🦋🐇🐀🐈🐈‍⬛", "🌼🌳🌲🌴🌵",
    "🥩🍋🍐🍈🍇", "🍴🍽️🔪🍶🥃", "🕌🏰🏩⛩️🏩", "🎉🎊🎈🎂🎀",
    "🪴🌵🌴🌳🌲", "🎄🎋🎍🎑🎎", "🦅🦜🕊️🦤🦢", "🦤🦩🦚🦃🦆",
    "🐬🦭🦈🐋🐳", "🐔🐟🐠🐡🦐", "🦩🦀🦑🐙🦪", "🐦🦂🕷️🕸️🐚",
    "🥪🍰🥧🍨🍨", " 🥬🍉🧁🧇",
]

TAGMES = [
    "**➠ ɢᴏᴏᴅ ɴɪɢʜᴛ 🌚**",
    "**➠ ᴄʜᴜᴘ ᴄʜᴀᴘ sᴏ ᴊᴀ 🙊**",
    "**➠ ᴘʜᴏɴᴇ ʀᴀᴋʜ ᴋᴀʀ sᴏ ᴊᴀ, ɴᴀʜɪ ᴛᴏ ʙʜᴏᴏᴛ ᴀᴀ ᴊᴀʏᴇɢᴀ..👻**",
    "**➠ ᴀᴡᴇᴇ ʙᴀʙᴜ sᴏɴᴀ ᴅɪɴ ᴍᴇɪɴ ᴋᴀʀ ʟᴇɴᴀ ᴀʙʜɪ sᴏ ᴊᴀᴏ..?? 🥲**",
    "**➠ ᴍᴜᴍᴍʏ ᴅᴇᴋʜᴏ ʏᴇ ᴀᴘɴᴇ ɢғ sᴇ ʙᴀᴀᴛ ᴋʀ ʀʜᴀ ʜ ʀᴀᴊᴀɪ ᴍᴇ ɢʜᴜs ᴋᴀʀ, sᴏ ɴᴀʜɪ ʀᴀʜᴀ 😜**",
    "**➠ ᴘᴀᴘᴀ ʏᴇ ᴅᴇᴋʜᴏ ᴀᴘɴᴇ ʙᴇᴛᴇ ᴋᴏ ʀᴀᴀᴛ ʙʜᴀʀ ᴘʜᴏɴᴇ ᴄʜᴀʟᴀ ʀʜᴀ ʜᴀɪ 🤭**",
    "**➠ ᴊᴀɴᴜ ᴀᴀᴊ ʀᴀᴀᴛ ᴋᴀ sᴄᴇɴᴇ ʙɴᴀ ʟᴇ..?? 🌠**",
    "**➠ ɢɴ sᴅ ᴛᴄ.. 🙂**",
    "**➠ ɢᴏᴏᴅ ɴɪɢʜᴛ sᴡᴇᴇᴛ ᴅʀᴇᴀᴍ ᴛᴀᴋᴇ ᴄᴀʀᴇ..?? ✨**",
    "**➠ ʀᴀᴀᴛ ʙʜᴜᴛ ʜᴏ ɢʏɪ ʜᴀɪ sᴏ ᴊᴀᴏ, ɢɴ..?? 🌌**",
    "**➠ ᴍᴜᴍᴍʏ ᴅᴇᴋʜᴏ 11 ʙᴀᴊɴᴇ ᴡᴀʟᴇ ʜᴀɪ ʏᴇ ᴀʙʜɪ ᴛᴀᴋ ᴘʜᴏɴᴇ ᴄʜᴀʟᴀ ʀʜᴀ ɴᴀʜɪ sᴏ ɴᴀʜɪ ʀᴀʜᴀ 🕦**",
    "**➠ ᴋᴀʟ sᴜʙʜᴀ sᴄʜᴏᴏʟ ɴᴀʜɪ ᴊᴀɴᴀ ᴋʏᴀ, ᴊᴏ ᴀʙʜɪ ᴛᴀᴋ ᴊᴀɢ ʀʜᴇ ʜᴏ 🏫**",
    "**➠ ʙᴀʙᴜ, ɢᴏᴏᴅ ɴɪɢʜᴛ sᴅ ᴛᴄ..?? 😊**",
    "**➠ ᴀᴀᴊ ʙʜᴜᴛ ᴛʜᴀɴᴅ ʜᴀɪ, ᴀᴀʀᴀᴍ sᴇ ᴊᴀʟᴅɪ sᴏ ᴊᴀᴛɪ ʜᴏᴏɴ 🌼**",
    "**➠ ᴊᴀɴᴇᴍᴀɴ, ɢᴏᴏᴅ ɴɪɢʜᴛ 🌷**",
    "**➠ ᴍᴇ ᴊᴀ ʀᴀʜɪ sᴏɴᴇ, ɢɴ sᴅ ᴛᴄ 🏵️**",
    "**➠ ʜᴇʟʟᴏ ᴊɪ ɴᴀᴍᴀsᴛᴇ, ɢᴏᴏᴅ ɴɪɢʜᴛ 🍃**",
    "**➠ ʜᴇʏ, ʙᴀʙʏ ᴋᴋʀʜ..? sᴏɴᴀ ɴᴀʜɪ ʜᴀɪ ᴋʏᴀ ☃️**",
    "**➠ ɢᴏᴏᴅ ɴɪɢʜᴛ ᴊɪ, ʙʜᴜᴛ ʀᴀᴀᴛ ʜᴏ ɢʏɪ..? ⛄**",
    "**➠ ᴍᴇ ᴊᴀ ʀᴀʜɪ ʀᴏɴᴇ, ɪ ᴍᴇᴀɴ sᴏɴᴇ ɢᴏᴏᴅ ɴɪɢʜᴛ ᴊɪ 😁**",
    "**➠ ᴍᴀᴄʜʜᴀʟɪ ᴋᴏ ᴋᴇʜᴛᴇ ʜᴀɪ ғɪsʜ, ɢᴏᴏᴅ ɴɪɢʜᴛ ᴅᴇᴀʀ ᴍᴀᴛ ᴋʀɴᴀ ᴍɪss, ᴊᴀ ʀʜɪ sᴏɴᴇ 🌄**",
    "**➠ ɢᴏᴏᴅ ɴɪɢʜᴛ ʙʀɪɢʜᴛғᴜʟʟ ɴɪɢʜᴛ 🤭**",
    "**➠ ᴛʜᴇ ɴɪɢʜᴛ ʜᴀs ғᴀʟʟᴇɴ, ᴛʜᴇ ᴅᴀʏ ɪs ᴅᴏɴᴇ,, ᴛʜᴇ ᴍᴏᴏɴ ʜᴀs ᴛᴀᴋᴇɴ ᴛʜᴇ ᴘʟᴀᴄᴇ ᴏғ ᴛʜᴇ sᴜɴ... 😊**",
    "**➠ ᴍᴀʏ ᴀʟʟ ʏᴏᴜʀ ᴅʀᴇᴀᴍs ᴄᴏᴍᴇ ᴛʀᴜᴇ ❤️**",
    "**➠ ɢᴏᴏᴅ ɴɪɢʜᴛ sᴘʀɪɴᴋʟᴇs sᴡᴇᴇᴛ ᴅʀᴇᴀᴍ 💚**",
    "**➠ ɢᴏᴏᴅ ɴɪɢʜᴛ, ɴɪɴᴅ ᴀᴀ ʀʜɪ ʜᴀɪ 🥱**",
    "**➠ ᴅᴇᴀʀ ғʀɪᴇɴᴅ ɢᴏᴏᴅ ɴɪɢʜᴛ 💤**",
    "**➠ ʙᴀʙʏ ᴀᴀᴊ ʀᴀᴀᴛ ᴋᴀ sᴄᴇɴᴇ ʙɴᴀ ʟᴇ 🥰**",
    "**➠ ɪᴛɴɪ ʀᴀᴀᴛ ᴍᴇ ᴊᴀɢ ᴋᴀʀ ᴋʏᴀ ᴋᴀʀ ʀʜᴇ ʜᴏ sᴏɴᴀ ɴᴀʜɪ ʜᴀɪ ᴋʏᴀ 😜**",
    "**➠ ᴄʟᴏsᴇ ʏᴏᴜʀ ᴇʏᴇs sɴᴜɢɢʟᴇ ᴜᴘ ᴛɪɢʜᴛ,, ᴀɴᴅ ʀᴇᴍᴇᴍʙᴇʀ ᴛʜᴀᴛ ᴀɴɢᴇʟs, ᴡɪʟʟ ᴡᴀᴛᴄʜ ᴏᴠᴇʀ ʏᴏᴜ ᴛᴏɴɪɢʜᴛ... 💫**",
]

VC_TAG = [
    "**➠ ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ, ᴋᴇsᴇ ʜᴏ 🐱**",
    "**➠ ɢᴍ, sᴜʙʜᴀ ʜᴏ ɢʏɪ ᴜᴛʜɴᴀ ɴᴀʜɪ ʜᴀɪ ᴋʏᴀ 🌤️**",
    "**➠ ɢᴍ ʙᴀʙʏ, ᴄʜᴀɪ ᴘɪ ʟᴏ ☕**",
    "**➠ ᴊᴀʟᴅɪ ᴜᴛʜᴏ, sᴄʜᴏᴏʟ ɴᴀʜɪ ᴊᴀɴᴀ ᴋʏᴀ 🏫**",
    "**➠ ɢᴍ, ᴄʜᴜᴘ ᴄʜᴀᴘ ʙɪsᴛᴇʀ sᴇ ᴜᴛʜᴏ ᴠʀɴᴀ ᴘᴀɴɪ ᴅᴀʟ ᴅᴜɴɢɪ 🧊**",
    "**➠ ʙᴀʙʏ ᴜᴛʜᴏ ᴀᴜʀ ᴊᴀʟᴅɪ ғʀᴇsʜ ʜᴏ ᴊᴀᴏ, ɴᴀsᴛᴀ ʀᴇᴀᴅʏ ʜᴀɪ 🫕**",
    "**➠ ᴏғғɪᴄᴇ ɴᴀʜɪ ᴊᴀɴᴀ ᴋʏᴀ ᴊɪ ᴀᴀᴊ, ᴀʙʜɪ ᴛᴀᴋ ᴜᴛʜᴇ ɴᴀʜɪ 🏣**",
    "**➠ ɢᴍ ᴅᴏsᴛ, ᴄᴏғғᴇᴇ/ᴛᴇᴀ ᴋʏᴀ ʟᴏɢᴇ ☕🍵**",
    "**➠ ʙᴀʙʏ 8 ʙᴀᴊɴᴇ ᴡᴀʟᴇ ʜᴀɪ, ᴀᴜʀ ᴛᴜᴍ ᴀʙʜɪ ᴛᴋ ᴜᴛʜᴇ ɴᴀʜɪ 🕖**",
    "**➠ ᴋʜᴜᴍʙʜᴋᴀʀᴀɴ ᴋɪ ᴀᴜʟᴀᴅ ᴜᴛʜ ᴊᴀᴀ... ☃️**",
    "**➠ ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ ʜᴀᴠᴇ ᴀ ɴɪᴄᴇ ᴅᴀʏ... 🌄**",
    "**➠ ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ, ʜᴀᴠᴇ ᴀ ɢᴏᴏᴅ ᴅᴀʏ... 🪴**",
    "**➠ ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ, ʜᴏᴡ ᴀʀᴇ ʏᴏᴜ ʙᴀʙʏ 😇**",
    "**➠ ᴍᴜᴍᴍʏ ᴅᴇᴋʜᴏ ʏᴇ ɴᴀʟᴀʏᴋ ᴀʙʜɪ ᴛᴀᴋ sᴏ ʀʜᴀ ʜᴀɪ... 😵‍💫**",
    "**➠ ʀᴀᴀᴛ ʙʜᴀʀ ʙᴀʙᴜ sᴏɴᴀ ᴋʀ ʀʜᴇ ᴛʜᴇ ᴋʏᴀ, ᴊᴏ ᴀʙʜɪ ᴛᴋ sᴏ ʀʜᴇ ʜᴏ ᴜᴛʜɴᴀ ɴᴀʜɪ ʜᴀɪ ᴋʏᴀ... 😏**",
    "**➠ ʙᴀʙᴜ ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ ᴜᴛʜ ᴊᴀᴏ ᴀᴜʀ ɢʀᴏᴜᴘ ᴍᴇ sᴀʙ ғʀɪᴇɴᴅs ᴋᴏ ɢᴍ ᴡɪsʜ ᴋʀᴏ... 🌟**",
    "**➠ ᴘᴀᴘᴀ ʏᴇ ᴀʙʜɪ ᴛᴀᴋ ᴜᴛʜ ɴᴀʜɪ, sᴄʜᴏᴏʟ ᴋᴀ ᴛɪᴍᴇ ɴɪᴋᴀʟᴛᴀ ᴊᴀ ʀʜᴀ ʜᴀɪ... 🥲**",
    "**➠ ᴊᴀɴᴇᴍᴀɴ ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ, ᴋʏᴀ ᴋʀ ʀʜᴇ ʜᴏ ... 😅**",
    "**➠ ɢᴍ ʙᴇᴀsᴛɪᴇ, ʙʀᴇᴀᴋғᴀsᴛ ʜᴜᴀ ᴋʏᴀ... 🍳**",
]

# ==================== HELPER FUNCTIONS ====================
async def is_admin(chat_id: int, user_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Check if user is admin in group"""
    try:
        chat_member = await context.bot.get_chat_member(chat_id, user_id)
        return chat_member.status in ['creator', 'administrator']
    except Exception as e:
        print(f"Admin check error: {e}")
        return False

async def get_chat_members_fixed(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Fixed function to get chat members"""
    members = []
    try:
        # Try to get approximate member count first
        chat = await context.bot.get_chat(chat_id)
        print(f"📊 Chat: {chat.title}, Members: {chat.get('member_count', 'Unknown')}")
        
        # Get administrators first
        admins = await context.bot.get_chat_administrators(chat_id)
        for admin in admins:
            if not admin.user.is_bot:
                members.append(admin.user)
        
        print(f"✅ Found {len(admins)} admins")
        
        # Try alternative method for regular members
        # Get recent message senders
        try:
            messages = await context.bot.get_chat_history(chat_id, limit=50)
            for msg in messages:
                if hasattr(msg, 'from_user') and msg.from_user:
                    if not msg.from_user.is_bot and msg.from_user.id not in [m.id for m in members]:
                        members.append(msg.from_user)
        except:
            pass
        
        print(f"📋 Total members collected: {len(members)}")
        
    except Exception as e:
        print(f"Error getting members: {e}")
    
    return members

async def tag_user(context: ContextTypes.DEFAULT_TYPE, chat_id: int, user_id: int, user_name: str, tag_type: str, custom_text: str = ""):
    """Tag a single user"""
    try:
        if tag_type == "gn":
            message = f"[{user_name}](tg://user?id={user_id}) {random.choice(TAGMES)}"
        elif tag_type == "gm":
            message = f"[{user_name}](tg://user?id={user_id}) {random.choice(VC_TAG)}"
        else:  # custom
            message = f"[{user_name}](tg://user?id={user_id}) {custom_text}"
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        return True
    except Forbidden:
        print(f"❌ Can't send message to {user_name} (blocked)")
        return False
    except BadRequest as e:
        print(f"❌ Bad request for {user_name}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error tagging {user_name}: {e}")
        return False

# ==================== SIMPLE TAG FUNCTION (WORKING VERSION) ====================
async def simple_tag_members(context: ContextTypes.DEFAULT_TYPE, chat_id: int, tag_text: str, tag_type: str):
    """Simple working version for tagging"""
    try:
        # First test if bot can send messages
        test_msg = await context.bot.send_message(
            chat_id, 
            "🎯 Starting tagging process...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Get chat administrators first
        admins = []
        try:
            admins = await context.bot.get_chat_administrators(chat_id)
            print(f"👑 Found {len(admins)} admins")
        except Exception as e:
            print(f"Error getting admins: {e}")
        
        tagged_count = 0
        failed_count = 0
        
        # Tag all admins
        if admins:
            await context.bot.send_message(chat_id, f"👑 Tagging {len(admins)} admins...")
            
            for admin in admins:
                if chat_id in active_tag_sessions and active_tag_sessions[chat_id].get("stop"):
                    break
                    
                if not admin.user.is_bot:
                    success = await tag_user(
                        context, chat_id, admin.user.id, 
                        admin.user.first_name, tag_type, tag_text
                    )
                    
                    if success:
                        tagged_count += 1
                        # Update session
                        if chat_id in active_tag_sessions:
                            active_tag_sessions[chat_id]["tagged"] = tagged_count
                    else:
                        failed_count += 1
                    
                    # Delay
                    await asyncio.sleep(random.uniform(2, 3))
        
        # Tag recent active users
        await context.bot.send_message(chat_id, "👥 Tagging recent active users...")
        
        # Create a list of known users (you can add more manually if needed)
        known_users = [
            # Add some test user mentions if needed
        ]
        
        # If we have message history, tag recent senders
        try:
            messages = []
            async for msg in context.bot.get_chat_history(chat_id, limit=30):
                messages.append(msg)
            
            for msg in messages:
                if chat_id in active_tag_sessions and active_tag_sessions[chat_id].get("stop"):
                    break
                    
                if hasattr(msg, 'from_user') and msg.from_user and not msg.from_user.is_bot:
                    # Check if already tagged
                    user_already_tagged = False
                    for admin in admins:
                        if admin.user.id == msg.from_user.id:
                            user_already_tagged = True
                            break
                    
                    if not user_already_tagged:
                        success = await tag_user(
                            context, chat_id, msg.from_user.id,
                            msg.from_user.first_name, tag_type, tag_text
                        )
                        
                        if success:
                            tagged_count += 1
                            if chat_id in active_tag_sessions:
                                active_tag_sessions[chat_id]["tagged"] = tagged_count
                        else:
                            failed_count += 1
                        
                        await asyncio.sleep(random.uniform(2, 3))
                        
                        # Stop after 20 users to avoid flooding
                        if tagged_count >= 20:
                            break
        except Exception as e:
            print(f"Error getting chat history: {e}")
        
        # Completion message
        if chat_id in active_tag_sessions and active_tag_sessions[chat_id].get("stop"):
            await context.bot.send_message(
                chat_id,
                f"🛑 Tagging stopped!\n✅ Tagged {tagged_count} users\n❌ Failed: {failed_count}"
            )
        else:
            completion_msg = f"""
✅ **Tagging Complete!**
━━━━━━━━━━━━━━
📊 **Statistics:**
• Successfully Tagged: {tagged_count}
• Failed: {failed_count}
• Total Attempted: {tagged_count + failed_count}
━━━━━━━━━━━━━━
🎯 Tagged recent active users and admins!
            """
            await context.bot.send_message(chat_id, completion_msg, parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        print(f"Tagging error: {e}")
        await context.bot.send_message(chat_id, f"❌ Error during tagging: {str(e)[:100]}")
    finally:
        # Clean up session
        if chat_id in active_tag_sessions:
            del active_tag_sessions[chat_id]

# ==================== COMMAND HANDLERS ====================
async def tag_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /tagall command"""
    user = update.effective_user
    chat = update.effective_chat
    
    if chat.type == 'private':
        await update.message.reply_text("❌ This command only works in groups!")
        return
    
    # Check if already running
    if chat.id in active_tag_sessions:
        await update.message.reply_text("⚠️ Tagging is already running! Use /tagstop to stop.")
        return
    
    # Check admin
    if not await is_admin(chat.id, user.id, context):
        await update.message.reply_text("❌ You need to be an admin to use this command!")
        return
    
    # Get tag text
    tag_text = ""
    if update.message.reply_to_message:
        tag_text = update.message.reply_to_message.text or update.message.reply_to_message.caption or ""
    elif context.args:
        tag_text = " ".join(context.args)
    
    if not tag_text:
        await update.message.reply_text(
            "📝 Please provide text or reply to a message!\n"
            "Example: `/tagall Good Morning` or reply to a message with `/tagall`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Start tagging session
    active_tag_sessions[chat.id] = {"stop": False, "tagged": 0}
    
    # Run tagging in background
    asyncio.create_task(
        simple_tag_members(context, chat.id, tag_text, "custom")
    )
    
    await update.message.reply_text(
        f"🎯 **Started Custom Tagging!**\n\n"
        f"📝 Message: `{tag_text[:50]}...`\n"
        f"⏳ Tagging admins and recent active users...\n"
        f"🛑 Use `/tagstop` to cancel.",
        parse_mode=ParseMode.MARKDOWN
    )

async def tag_all_gm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /gmtag command (Good Morning tag)"""
    user = update.effective_user
    chat = update.effective_chat
    
    if chat.type == 'private':
        await update.message.reply_text("❌ This command only works in groups!")
        return
    
    # Check if already running
    if chat.id in active_tag_sessions:
        await update.message.reply_text("⚠️ Tagging is already running! Use /tagstop to stop.")
        return
    
    # Check admin
    if not await is_admin(chat.id, user.id, context):
        await update.message.reply_text("❌ You need to be an admin to use this command!")
        return
    
    # Start tagging session
    active_tag_sessions[chat.id] = {"stop": False, "tagged": 0}
    
    # Run tagging in background
    asyncio.create_task(
        simple_tag_members(context, chat.id, "", "gm")
    )
    
    await update.message.reply_text(
        "🌅 **Started Good Morning Tagging!**\n\n"
        "⏳ Tagging admins and recent active users...\n"
        "🛑 Use `/tagstop` to cancel.",
        parse_mode=ParseMode.MARKDOWN
    )

async def tag_all_gn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /gntag command (Good Night tag)"""
    user = update.effective_user
    chat = update.effective_chat
    
    if chat.type == 'private':
        await update.message.reply_text("❌ This command only works in groups!")
        return
    
    # Check if already running
    if chat.id in active_tag_sessions:
        await update.message.reply_text("⚠️ Tagging is already running! Use /tagstop to stop.")
        return
    
    # Check admin
    if not await is_admin(chat.id, user.id, context):
        await update.message.reply_text("❌ You need to be an admin to use this command!")
        return
    
    # Start tagging session
    active_tag_sessions[chat.id] = {"stop": False, "tagged": 0}
    
    # Run tagging in background
    asyncio.create_task(
        simple_tag_members(context, chat.id, "", "gn")
    )
    
    await update.message.reply_text(
        "🌙 **Started Good Night Tagging!**\n\n"
        "⏳ Tagging admins and recent active users...\n"
        "🛑 Use `/tagstop` to cancel.",
        parse_mode=ParseMode.MARKDOWN
    )

async def tag_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop tagging process"""
    user = update.effective_user
    chat = update.effective_chat
    
    if chat.id not in active_tag_sessions:
        await update.message.reply_text("ℹ️ No tagging process is currently running.")
        return
    
    # Check admin
    if not await is_admin(chat.id, user.id, context):
        await update.message.reply_text("❌ You need to be an admin to stop tagging!")
        return
    
    # Mark for stopping
    active_tag_sessions[chat.id]["stop"] = True
    await update.message.reply_text("🛑 Stopping tagging process... Please wait.")

async def tag_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check tagging status"""
    chat = update.effective_chat
    
    if chat.id in active_tag_sessions:
        tagged = active_tag_sessions[chat.id].get("tagged", 0)
        await update.message.reply_text(f"🔄 Tagging is running...\n✅ Tagged: {tagged} users")
    else:
        await update.message.reply_text("ℹ️ No active tagging session.")

async def tag_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test tag command - tags 3 users only"""
    user = update.effective_user
    chat = update.effective_chat
    
    if chat.type == 'private':
        await update.message.reply_text("❌ This command only works in groups!")
        return
    
    # Check admin
    if not await is_admin(chat.id, user.id, context):
        await update.message.reply_text("❌ You need to be an admin to use this command!")
        return
    
    await update.message.reply_text("🧪 Testing tag function...")
    
    try:
        # Get chat admins
        admins = await context.bot.get_chat_administrators(chat.id)
        
        # Tag first 3 admins (excluding bots)
        tagged = 0
        for admin in admins[:3]:
            if not admin.user.is_bot:
                message = f"[{admin.user.first_name}](tg://user?id={admin.user.id}) Test tag from bot! 🎯"
                await context.bot.send_message(
                    chat_id=chat.id,
                    text=message,
                    parse_mode=ParseMode.MARKDOWN
                )
                tagged += 1
                await asyncio.sleep(1)
        
        await update.message.reply_text(f"✅ Successfully tagged {tagged} users!")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Test failed: {str(e)}")

async def manual_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manual tag specific users"""
    user = update.effective_user
    chat = update.effective_chat
    
    if chat.type == 'private':
        await update.message.reply_text("❌ This command only works in groups!")
        return
    
    # Check admin
    if not await is_admin(chat.id, user.id, context):
        await update.message.reply_text("❌ You need to be an admin to use this command!")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: `/manual_tag @username1 @username2`")
        return
    
    await update.message.reply_text("🔸 Starting manual tagging...")
    
    tagged = 0
    for arg in context.args:
        if arg.startswith('@'):
            username = arg[1:]
            try:
                message = f"Hello {arg}! 👋"
                await context.bot.send_message(
                    chat_id=chat.id,
                    text=message,
                    parse_mode=ParseMode.MARKDOWN
                )
                tagged += 1
                await asyncio.sleep(2)
            except Exception as e:
                print(f"Failed to tag {arg}: {e}")
    
    await update.message.reply_text(f"✅ Manually tagged {tagged} users!")

# ==================== REGISTER HANDLERS ====================
def register_handlers(app: Application):
    """Register all handlers for this plugin"""
    app.add_handler(CommandHandler("tagall", tag_all))
    app.add_handler(CommandHandler("gmtag", tag_all_gm))
    app.add_handler(CommandHandler("gntag", tag_all_gn))
    app.add_handler(CommandHandler("tagstop", tag_stop))
    app.add_handler(CommandHandler("tagstatus", tag_status))
    app.add_handler(CommandHandler("tagtest", tag_test))
    app.add_handler(CommandHandler("manual_tag", manual_tag))
    app.add_handler(CommandHandler(["tagcancel", "cancletag"], tag_stop))
    app.add_handler(CommandHandler("taghelp", tag_help))
    
    print("✅ Tagger Plugin Loaded Successfully!")

async def tag_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help for tag commands"""
    help_text = """
🎯 **TAGGER PLUGIN COMMANDS:**

**For Admins Only:**
• `/tagall [text]` - Tag with custom text
• `/tagall` (reply to message) - Tag with replied message
• `/gmtag` - Good Morning tag
• `/gntag` - Good Night tag
• `/tagstop` - Stop tagging
• `/tagstatus` - Check status
• `/tagtest` - Test tag (tags 3 users)
• `/manual_tag @user1 @user2` - Manual tag
• `/taghelp` - Show help

**Examples:**
`/tagall Hello everyone!`
`/tagall` (reply to a message)
`/gmtag` - Good Morning to all
`/tagtest` - Test the bot

⚠️ **Note:** Tags recent active users and admins
    """
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

# For direct testing
if __name__ == "__main__":
    print("🧪 Tagger Plugin Ready!")
