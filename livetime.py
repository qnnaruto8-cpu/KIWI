import asyncio
import pytz
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, JobQueue

# --- LIVE TIME MODULE ---

# Store active time messages
active_time_messages = {}

# Timezone mapping for common Indian cities
TIMEZONES = {
    "delhi": "Asia/Kolkata",
    "mumbai": "Asia/Kolkata", 
    "kolkata": "Asia/Kolkata",
    "chennai": "Asia/Kolkata",
    "bangalore": "Asia/Kolkata",
    "hyderabad": "Asia/Kolkata",
    "ahmedabad": "Asia/Kolkata",
    "pune": "Asia/Kolkata",
    "jaipur": "Asia/Kolkata",
    "lucknow": "Asia/Kolkata",
    "kanpur": "Asia/Kolkata",
    "nagpur": "Asia/Kolkata",
    "indore": "Asia/Kolkata",
    "thane": "Asia/Kolkata",
    "bhopal": "Asia/Kolkata",
    "visakhapatnam": "Asia/Kolkata",
    "patna": "Asia/Kolkata",
    "vadodara": "Asia/Kolkata",
    "ghaziabad": "Asia/Kolkata",
    "ludhiana": "Asia/Kolkata",
    "agra": "Asia/Kolkata",
    "nashik": "Asia/Kolkata",
    "faridabad": "Asia/Kolkata",
    "meerut": "Asia/Kolkata",
    "rajkot": "Asia/Kolkata",
    "kalyan": "Asia/Kolkata",
    "varanasi": "Asia/Kolkata",
    "srinagar": "Asia/Kolkata",
    "aurangabad": "Asia/Kolkata",
    "dhanbad": "Asia/Kolkata",
    "amritsar": "Asia/Kolkata",
    "navi mumbai": "Asia/Kolkata",
    "allahabad": "Asia/Kolkata",
    "ranchi": "Asia/Kolkata",
    "howrah": "Asia/Kolkata",
    "coimbatore": "Asia/Kolkata",
    "jabalpur": "Asia/Kolkata",
    "gwalior": "Asia/Kolkata",
    "vijayawada": "Asia/Kolkata",
    "jodhpur": "Asia/Kolkata",
    "madurai": "Asia/Kolkata",
    "raipur": "Asia/Kolkata",
    "kota": "Asia/Kolkata",
    "guwahati": "Asia/Kolkata",
    "chandigarh": "Asia/Kolkata",
    "solapur": "Asia/Kolkata",
    "hubli": "Asia/Kolkata",
    "bareilly": "Asia/Kolkata",
    "moradabad": "Asia/Kolkata",
    "mysore": "Asia/Kolkata",
    "gurgaon": "Asia/Kolkata",
    "aligarh": "Asia/Kolkata",
    "jalandhar": "Asia/Kolkata",
    "tiruchirappalli": "Asia/Kolkata",
    "bhubaneswar": "Asia/Kolkata",
    "salem": "Asia/Kolkata",
    "mira-bhayandar": "Asia/Kolkata",
    "warangal": "Asia/Kolkata",
    "thiruvananthapuram": "Asia/Kolkata",
    "guntur": "Asia/Kolkata",
    "bhiwandi": "Asia/Kolkata",
    "saharanpur": "Asia/Kolkata",
    "gorakhpur": "Asia/Kolkata",
    "bikaner": "Asia/Kolkata",
    "amravati": "Asia/Kolkata",
    "noida": "Asia/Kolkata",
    "jamshedpur": "Asia/Kolkata",
    "bhilai": "Asia/Kolkata",
    "cuttack": "Asia/Kolkata",
    "firozabad": "Asia/Kolkata",
    "kochi": "Asia/Kolkata",
    "nellore": "Asia/Kolkata",
    "bhavnagar": "Asia/Kolkata",
    "dehradun": "Asia/Kolkata",
    "durgapur": "Asia/Kolkata",
    "asansol": "Asia/Kolkata",
    "rourkela": "Asia/Kolkata",
    "nanded": "Asia/Kolkata",
    "kolhapur": "Asia/Kolkata",
    "ajmer": "Asia/Kolkata",
    "akola": "Asia/Kolkata",
    "gulbarga": "Asia/Kolkata",
    "jamnagar": "Asia/Kolkata",
    "ujjain": "Asia/Kolkata",
    "loni": "Asia/Kolkata",
    "siliguri": "Asia/Kolkata",
    "jhansi": "Asia/Kolkata",
    "ulhasnagar": "Asia/Kolkata",
    "jammu": "Asia/Kolkata",
    "sangli-miraj": "Asia/Kolkata",
    "mangalore": "Asia/Kolkata",
    "erode": "Asia/Kolkata",
    "belgaum": "Asia/Kolkata",
    "ambattur": "Asia/Kolkata",
    "tirunelveli": "Asia/Kolkata",
    "malegaon": "Asia/Kolkata",
    "gaya": "Asia/Kolkata",
    "jalandhar cantonment": "Asia/Kolkata",
    "udaipur": "Asia/Kolkata",
    "kakinada": "Asia/Kolkata",
    "davanagere": "Asia/Kolkata",
    "kozhikode": "Asia/Kolkata",
    "maheshtala": "Asia/Kolkata",
    "rajpur sonarpur": "Asia/Kolkata",
    "bokaro": "Asia/Kolkata",
    "south dumdum": "Asia/Kolkata",
    "bellary": "Asia/Kolkata",
    "patiala": "Asia/Kolkata",
    "gopalpur": "Asia/Kolkata",
    "agartala": "Asia/Kolkata",
    "bhagalpur": "Asia/Kolkata",
    "muzaffarnagar": "Asia/Kolkata",
    "bhatpara": "Asia/Kolkata",
    "panihati": "Asia/Kolkata",
    "latur": "Asia/Kolkata",
    "dhule": "Asia/Kolkata",
    "rohtak": "Asia/Kolkata",
    "korba": "Asia/Kolkata",
    "bhilwara": "Asia/Kolkata",
    "berhampur": "Asia/Kolkata",
    "muzaffarpur": "Asia/Kolkata",
    "ahmednagar": "Asia/Kolkata",
    "mathura": "Asia/Kolkata",
    "kollam": "Asia/Kolkata",
    "avadi": "Asia/Kolkata",
    "kadapa": "Asia/Kolkata",
    "kamarhati": "Asia/Kolkata",
    "sambalpur": "Asia/Kolkata",
    "bilaspur": "Asia/Kolkata",
    "shahjahanpur": "Asia/Kolkata",
    "satara": "Asia/Kolkata",
    "bijapur": "Asia/Kolkata",
    "rampur": "Asia/Kolkata",
    "shivamogga": "Asia/Kolkata",
    "chandrapur": "Asia/Kolkata",
    "junagadh": "Asia/Kolkata",
    "thrissur": "Asia/Kolkata",
    "alwar": "Asia/Kolkata",
    "bardhaman": "Asia/Kolkata",
    "kulti": "Asia/Kolkata",
    "nizamabad": "Asia/Kolkata",
    "parbhani": "Asia/Kolkata",
    "tumkur": "Asia/Kolkata",
    "khammam": "Asia/Kolkata",
    "ozhukarai": "Asia/Kolkata",
    "bihar sharif": "Asia/Kolkata",
    "panipat": "Asia/Kolkata",
    "darbhanga": "Asia/Kolkata",
    "bally": "Asia/Kolkata",
    "aisen": "Asia/Kolkata",
    "deoli": "Asia/Kolkata",
    "kirari suleman nagar": "Asia/Kolkata",
    "purnia": "Asia/Kolkata",
    "bhandara": "Asia/Kolkata",
    "bhadravati": "Asia/Kolkata",
    "chinsurah": "Asia/Kolkata",
    "gandhinagar": "Asia/Kolkata",
    "bahraich": "Asia/Kolkata",
    "machilipatnam": "Asia/Kolkata",
    "raichur": "Asia/Kolkata",
    "etawah": "Asia/Kolkata",
    "raigarh": "Asia/Kolkata",
    "koraput": "Asia/Kolkata",
    "puducherry": "Asia/Kolkata",
    "gandhidham": "Asia/Kolkata",
    "bharuch": "Asia/Kolkata",
    "pali": "Asia/Kolkata",
    "tatabánya": "Asia/Kolkata",
    "palghar": "Asia/Kolkata",
    "bulandshahr": "Asia/Kolkata",
    "navsari": "Asia/Kolkata",
    "mango": "Asia/Kolkata",
    "bidar": "Asia/Kolkata",
    "thoothukudi": "Asia/Kolkata",
    "deoghar": "Asia/Kolkata",
    "chittoor": "Asia/Kolkata",
    "haridwar": "Asia/Kolkata",
    "saharsa": "Asia/Kolkata",
    "vidisha": "Asia/Kolkata",
    "bettiah": "Asia/Kolkata",
    "pathankot": "Asia/Kolkata",
    "hospet": "Asia/Kolkata",
    "bhusawal": "Asia/Kolkata",
    "fatehpur": "Asia/Kolkata",
    "mandsaur": "Asia/Kolkata",
    "dinapur nizamat": "Asia/Kolkata",
    "sasaram": "Asia/Kolkata",
    "damoh": "Asia/Kolkata",
    "phusro": "Asia/Kolkata",
    "khanna": "Asia/Kolkata",
    "chittaranjan": "Asia/Kolkata",
    "chikmagalur": "Asia/Kolkata",
    "godhra": "Asia/Kolkata",
    "bhadrak": "Asia/Kolkata",
    "siwan": "Asia/Kolkata",
    "hinganghat": "Asia/Kolkata",
    "shillong": "Asia/Kolkata",
    "ranchi cantonment": "Asia/Kolkata",
    "warisaliganj": "Asia/Kolkata",
    "mirzapur": "Asia/Kolkata",
    "tadepalligudem": "Asia/Kolkata",
    "karaikudi": "Asia/Kolkata",
    "kishanganj": "Asia/Kolkata",
    "jetpur navagadh": "Asia/Kolkata",
    "jaunpur": "Asia/Kolkata",
    "madhubani": "Asia/Kolkata",
    "tezpur": "Asia/Kolkata",
    "mcc": "Asia/Kolkata"
}

# Fancy Text Converter (SAME AS WORDGRID)
def to_fancy(text):
    mapping = {
        'A': 'Λ', 'B': 'ʙ', 'C': 'ᴄ', 'D': 'ᴅ', 'E': 'Є', 
        'F': 'ғ', 'G': 'ɢ', 'H': 'ʜ', 'I': 'ɪ', 'J': 'ᴊ', 
        'K': 'ᴋ', 'L': 'ʟ', 'M': 'ᴍ', 'N': 'ɴ', 'O': 'σ', 
        'P': 'ᴘ', 'Q': 'ǫ', 'R': 'ʀ', 'S': 'δ', 'T': 'ᴛ', 
        'U': 'ᴜ', 'V': 'ᴠ', 'W': 'ᴡ', 'X': 'х', 'Y': 'ʏ', 'Z': 'ᴢ'
    }
    return "".join(mapping.get(c.upper(), c) for c in text)

def get_current_time(city="delhi"):
    """Get current time for a city"""
    city = city.lower()
    timezone_str = TIMEZONES.get(city, "Asia/Kolkata")
    
    try:
        tz = pytz.timezone(timezone_str)
        now = datetime.now(tz)
        
        # Format time with AM/PM
        time_str = now.strftime("%I:%M:%S %p")
        
        # Format date
        date_str = now.strftime("%A, %d %B %Y")
        
        # Get day number
        day_num = now.strftime("%d")
        
        # Get month name
        month_name = now.strftime("%B")
        
        # Get weekday
        weekday = now.strftime("%A")
        
        # Get fancy weekday
        fancy_weekday = to_fancy(weekday.upper())
        
        # Get fancy month
        fancy_month = to_fancy(month_name.upper())
        
        # Get fancy city
        fancy_city = to_fancy(city.upper())
        
        # Get fancy timezone
        fancy_timezone = to_fancy(timezone_str.split('/')[-1].upper())
        
        return {
            'time': time_str,
            'date': date_str,
            'day': day_num,
            'month': month_name,
            'weekday': weekday,
            'timezone': timezone_str,
            'city': city.title(),
            'fancy_city': fancy_city,
            'fancy_timezone': fancy_timezone,
            'fancy_weekday': fancy_weekday,
            'fancy_month': fancy_month
        }
    except:
        # Fallback to UTC
        tz = pytz.timezone("Asia/Kolkata")
        now = datetime.now(tz)
        return {
            'time': now.strftime("%I:%M:%S %p"),
            'date': now.strftime("%A, %d %B %Y"),
            'day': now.strftime("%d"),
            'month': now.strftime("%B"),
            'weekday': now.strftime("%A"),
            'timezone': "Asia/Kolkata",
            'city': "Delhi",
            'fancy_city': "ᴅᴇʟʜɪ",
            'fancy_timezone': "ᴋᴏʟᴋᴀᴛᴀ",
            'fancy_weekday': to_fancy(now.strftime("%A").upper()),
            'fancy_month': to_fancy(now.strftime("%B").upper())
        }

def create_time_display(city="delhi"):
    """Create beautiful time display with FANCY TEXT"""
    time_data = get_current_time(city)
    
    # Create fancy time display
    time_display = f"""<blockquote><b>🕒 {to_fancy("LIVE TIME")}</b></blockquote>

<blockquote>
<b>📍 {to_fancy("CITY")}:</b> {time_data['fancy_city']}
<b>🌐 {to_fancy("TIMEZONE")}:</b> {time_data['fancy_timezone']}
</blockquote>

<blockquote>
<b>⏰ {to_fancy("TIME")}:</b> <code>{time_data['time']}</code>
</blockquote>

<blockquote>
<b>📅 {to_fancy("DATE")}:</b> {time_data['date']}
<b>📆 {to_fancy("DAY")}:</b> {time_data['day']} | <b>{to_fancy("MONTH")}:</b> {time_data['fancy_month']}
<b>🌞 {to_fancy("WEEKDAY")}:</b> {time_data['fancy_weekday']}
</blockquote>

<blockquote>
<b>🔄 {to_fancy("UPDATES EVERY SECOND")}</b>
<b>📍 {to_fancy("USE")}:</b> <code>/time mumbai</code> {to_fancy("FOR DIFFERENT CITY")}
</blockquote>"""
    
    return time_display

async def update_live_time(context: ContextTypes.DEFAULT_TYPE):
    """Update live time message"""
    chat_id = context.job.chat_id
    
    if chat_id in active_time_messages:
        try:
            msg_info = active_time_messages[chat_id]
            message_id = msg_info['message_id']
            city = msg_info['city']
            
            time_display = create_time_display(city)
            kb = [[InlineKeyboardButton("❌ Close", callback_data="close_time")]]
            
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=time_display,
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            print(f"❌ LIVE TIME: Error updating time: {e}")
            if chat_id in active_time_messages:
                del active_time_messages[chat_id]

async def start_live_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start live time display"""
    chat_id = update.effective_chat.id
    
    print(f"LIVE TIME: Command received in chat {chat_id}")
    
    # Check for city argument
    city = "delhi"
    if context.args:
        city_arg = context.args[0].lower()
        if city_arg in TIMEZONES:
            city = city_arg
        else:
            # Try to find closest match
            for key in TIMEZONES:
                if city_arg in key or key in city_arg:
                    city = key
                    break
    
    print(f"LIVE TIME: Creating display for city {city}")
    
    # Create initial time display
    time_display = create_time_display(city)
    kb = [[InlineKeyboardButton("❌ Close", callback_data="close_time")]]
    
    # Send time message
    try:
        msg = await update.message.reply_text(
            text=time_display,
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode=ParseMode.HTML
        )
        print(f"✅ LIVE TIME: Message sent with ID {msg.message_id}")
    except Exception as e:
        print(f"❌ LIVE TIME: Error sending message: {e}")
        return
    
    # Store message info
    active_time_messages[chat_id] = {
        'message_id': msg.message_id,
        'city': city,
        'pinned': False
    }
    
    # Try to pin the message
    try:
        await msg.pin(disable_notification=True)
        active_time_messages[chat_id]['pinned'] = True
        print(f"✅ LIVE TIME: Message pinned")
    except Exception as e:
        print(f"⚠️ LIVE TIME: Could not pin message: {e}")
    
    # Schedule live updates every second
    if context.job_queue:
        # First remove any existing job for this chat
        current_jobs = context.job_queue.get_jobs_by_name(f"livetime_{chat_id}")
        for job in current_jobs:
            job.schedule_removal()
            print(f"🔄 LIVE TIME: Removed existing job")
        
        # Schedule new job
        job = context.job_queue.run_repeating(
            callback=update_live_time,
            interval=1,  # Update every second
            first=0,     # Start immediately
            chat_id=chat_id,
            name=f"livetime_{chat_id}"
        )
        active_time_messages[chat_id]['job'] = job
        print(f"✅ LIVE TIME: Started live updates for chat {chat_id}, city: {city}")
    else:
        print(f"❌ LIVE TIME: No job_queue available!")

async def close_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Close live time display - FIXED"""
    query = update.callback_query
    
    # Answer the callback FIRST
    await query.answer("⏰ Time display closed!")
    
    chat_id = query.message.chat_id
    
    print(f"CLOSE TIME: Close button clicked in chat {chat_id}")
    
    if chat_id in active_time_messages:
        # Get message info
        msg_info = active_time_messages[chat_id]
        
        # Cancel update job
        if 'job' in msg_info:
            try:
                msg_info['job'].schedule_removal()
                print(f"✅ CLOSE TIME: Stopped updates for chat {chat_id}")
            except Exception as e:
                print(f"⚠️ CLOSE TIME: Error removing job: {e}")
        
        # Unpin message if pinned
        if msg_info.get('pinned'):
            try:
                await context.bot.unpin_chat_message(
                    chat_id=chat_id,
                    message_id=msg_info['message_id']
                )
                print(f"✅ CLOSE TIME: Message unpinned")
            except Exception as e:
                print(f"⚠️ CLOSE TIME: Error unpinning: {e}")
        
        # Delete the time message
        try:
            await query.message.delete()
            print(f"✅ CLOSE TIME: Message deleted")
        except Exception as e:
            print(f"⚠️ CLOSE TIME: Error deleting message: {e}")
            # If can't delete, edit it to show it's closed
            try:
                await query.message.edit_text(
                    text="⏰ <b>Time display closed</b>",
                    parse_mode=ParseMode.HTML
                )
            except:
                pass
        
        # Remove from storage
        del active_time_messages[chat_id]
        print(f"✅ CLOSE TIME: Cleaned up for chat {chat_id}")
    else:
        await query.answer("⚠️ No active time display found.", show_alert=True)

async def time_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle time callback queries"""
    query = update.callback_query
    data = query.data
    
    print(f"TIME CALLBACK: Received callback data: {data}")
    
    if data == "close_time":
        await close_time(update, context)

# Cleanup function
def cleanup_time_messages():
    """Clean up old time messages"""
    # This can be called periodically to clean up stale entries
    # For now, we rely on callback to clean up
    pass

# Export functions
__all__ = [
    'start_live_time',
    'time_callback',
    'close_time',
    'cleanup_time_messages'
]