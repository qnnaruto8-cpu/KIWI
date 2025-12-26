from tools.youtube import YouTubeAPI
from tools.stream import play_stream
from tools.thumbnails import get_thumb

# Initialize YouTube
YouTube = YouTubeAPI()

async def process_stream(chat_id, user_name, query):
    """
    Complete Flow: Search -> Download -> Thumbnail -> Stream/Queue
    """
    
    # --- 1. SEARCHING ---
    try:
        # Link hai ya Name? check karke details nikalo
        if "youtube.com" in query or "youtu.be" in query:
             # Agar Link hai
             title = await YouTube.title(query)
             duration = await YouTube.duration(query)
             thumbnail = await YouTube.thumbnail(query)
             if "v=" in query:
                 vidid = query.split("v=")[-1].split("&")[0]
             else:
                 vidid = query.split("/")[-1]
             link = query
        else:
            # Agar Name hai (Search)
            result, vidid = await YouTube.track(query)
            if not result:
                return "❌ Song not found.", None
            title = result["title"]
            duration = result["duration_min"]
            thumbnail = result["thumb"]
            link = result["link"]
            
    except Exception as e:
        return f"❌ Search Error: {e}", None

    # --- 2. THUMBNAIL GENERATION ---
    # Custom Thumbnail banao (Prince/Yukki Style)
    final_thumb = await get_thumb(vidid)
    if not final_thumb:
        final_thumb = thumbnail # Fallback to original if generation fails

    # --- 3. DOWNLOADING ---
    try:
        file_path, direct = await YouTube.download(
            link, 
            mystic=None,
            title=title,
            format_id="bestaudio"
        )
    except Exception as e:
        return f"❌ Download Error: {e}", None

    # --- 4. PLAYING / QUEUING (🔥 FIXED HERE) ---
    # ✅ FIX: Ab hum link aur final_thumb bhi pass kar rahe hain
    # play_stream(chat_id, file, title, duration, user, link, thumbnail)
    status, position = await play_stream(
        chat_id, 
        file_path, 
        title, 
        duration, 
        user_name, 
        link,        # ✅ Added Link
        final_thumb  # ✅ Added Thumbnail
    )

    # --- 5. RESULT ---
    response = {
        "title": title,
        "duration": duration,
        "thumbnail": final_thumb, # Generated Path
        "user": user_name,
        "link": link,
        "vidid": vidid,
        "status": status,    # True (Playing) / False (Queued)
        "position": position # Queue Number
    }
    
    return None, response
    
