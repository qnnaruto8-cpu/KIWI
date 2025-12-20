import time

# Settings
SPAM_THRESHOLD = 5       # Max messages allowed
TIME_WINDOW = 5          # ...in seconds
BLOCK_DURATION = 480     # 8 Minutes (in seconds)

# Memory Storage
user_spam_history = {}   # {user_id: [time1, time2...]}
blocked_users = {}       # {user_id: unblock_time}

def check_spam(user_id):
    """
    Returns True if user is ALLOWED.
    Returns False if user is BLOCKED (Spamming).
    """
    current_time = time.time()

    # 1. Check if already blocked
    if user_id in blocked_users:
        if current_time < blocked_users[user_id]:
            return False # Still Blocked
        else:
            del blocked_users[user_id] # Unblock time over

    # 2. Add current msg timestamp
    if user_id not in user_spam_history:
        user_spam_history[user_id] = []
    
    user_spam_history[user_id].append(current_time)

    # 3. Clean old timestamps (Keep only recent ones within window)
    user_spam_history[user_id] = [t for t in user_spam_history[user_id] if current_time - t <= TIME_WINDOW]

    # 4. Check Count
    if len(user_spam_history[user_id]) > SPAM_THRESHOLD:
        # Block User
        blocked_users[user_id] = current_time + BLOCK_DURATION
        # History clear kar do taaki unblock hone ke baad turant wapis block na ho
        user_spam_history[user_id] = []
        return "BLOCKED" # Special signal to send warning

    return True # Allowed
