import html
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

# Global Dictionary
ttt_games = {}

# Winning Combinations
WIN_COMBOS = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8], # Rows
    [0, 3, 6], [1, 4, 7], [2, 5, 8], # Cols
    [0, 4, 8], [2, 4, 6]             # Diagonals
]

def to_fancy(text):
    mapping = {'A': 'Λ', 'E': 'Є', 'S': 'δ', 'O': 'σ', 'T': 'ᴛ', 'N': 'ɴ', 'M': 'ᴍ', 'U': 'ᴜ', 'R': 'ʀ', 'D': 'ᴅ', 'C': 'ᴄ', 'P': 'ᴘ', 'G': 'ɢ', 'B': 'ʙ', 'L': 'ʟ', 'W': 'ᴡ', 'K': 'ᴋ', 'J': 'ᴊ', 'Y': 'ʏ', 'I': 'ɪ', 'H': 'ʜ'}
    return "".join(mapping.get(c.upper(), c) for c in text)

# --- SMART BOT LOGIC (Minimax-Lite) ---
def get_bot_move(board):
    # 1. Check if Bot can win now
    for combo in WIN_COMBOS:
        line = [board[i] for i in combo]
        if line.count("O") == 2 and line.count(" ") == 1:
            return combo[line.index(" ")]

    # 2. Check if Player is winning, Block them
    for combo in WIN_COMBOS:
        line = [board[i] for i in combo]
        if line.count("X") == 2 and line.count(" ") == 1:
            return combo[line.index(" ")]

    # 3. Take Center if available
    if board[4] == " ": return 4

    # 4. Take random available spot
    available = [i for i, x in enumerate(board) if x == " "]
    return random.choice(available) if available else None

# --- 1. START COMMAND (/zero) ---
async def start_ttt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    msg = f"""
<blockquote><b>🎮 {to_fancy("TIC TAC TOE")}</b></blockquote>
<blockquote><b>👤 ᴘʟᴀʏᴇʀ :</b> {html.escape(user.first_name)}
<b>⚔️ ᴄʜᴏᴏsᴇ ᴍᴏᴅᴇ :</b> 👇</blockquote>
"""
    kb = [
        [InlineKeyboardButton("👥 1 vs 1 (PvP)", callback_data=f"ttt_init_pvp_{user.id}")],
        [InlineKeyboardButton("🤖 Play with Bot", callback_data=f"ttt_init_bot_{user.id}")],
        [InlineKeyboardButton("❌ Close", callback_data="ttt_close")]
    ]
    
    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)

# --- 2. GAME LOGIC ---
def check_winner(board):
    for combo in WIN_COMBOS:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] and board[combo[0]] != " ":
            return board[combo[0]]
    if " " not in board:
        return "Draw"
    return None

def get_board_markup(game_id):
    game = ttt_games[game_id]
    board = game["board"]
    kb = []
    for i in range(0, 9, 3):
        row = []
        for j in range(3):
            idx = i + j
            text = board[idx]
            if text == " ": text = "⬜"
            elif text == "X": text = "❌"
            elif text == "O": text = "⭕"
            row.append(InlineKeyboardButton(text, callback_data=f"ttt_move_{idx}"))
        kb.append(row)
    kb.append([InlineKeyboardButton("❌ End Game", callback_data="ttt_close")])
    return InlineKeyboardMarkup(kb)

# --- 3. CALLBACK HANDLER ---
async def ttt_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data
    user = q.from_user
    msg_id = q.message.message_id
    
    # A. CLOSE
    if data == "ttt_close":
        if msg_id in ttt_games: del ttt_games[msg_id]
        await q.message.delete()
        return

    # B. INITIALIZE GAME
    if data.startswith("ttt_init_"):
        parts = data.split("_")
        mode = parts[2] # 'pvp' or 'bot'
        p1_id = int(parts[3])
        
        game_data = {
            "board": [" "] * 9,
            "turn": "X",
            "p1": p1_id,
            "p2": None, 
            "p1_name": user.first_name,
            "p2_name": "Waiting...",
            "mode": mode
        }

        # If Bot Mode, setup Bot immediately
        if mode == "bot":
            game_data["p2"] = 0 # 0 ID for Bot
            game_data["p2_name"] = "Mimi Bot"

        ttt_games[msg_id] = game_data
        
        status_text = f"❌ <b>Turn:</b> {html.escape(user.first_name)}"
        
        await q.edit_message_text(
            f"<blockquote><b>🎮 {to_fancy('GAME STARTED')} ({mode.upper()})</b></blockquote>\n<blockquote>{status_text}</blockquote>",
            reply_markup=get_board_markup(msg_id),
            parse_mode=ParseMode.HTML
        )
        return

    # C. PLAYER MOVE
    if data.startswith("ttt_move_"):
        if msg_id not in ttt_games:
            await q.answer("❌ Game Expired!", show_alert=True)
            try: await q.message.delete()
            except: pass
            return
            
        game = ttt_games[msg_id]
        idx = int(data.split("_")[2])
        
        # --- PvP LOGIC: ASSIGN P2 ---
        if game["mode"] == "pvp":
            if game["p2"] is None:
                # 🔥 FIX: Prevent Self Play
                if user.id == game["p1"]:
                    await q.answer("⚠️ You cannot play against yourself! Wait for a friend.", show_alert=True)
                    return
                game["p2"] = user.id
                game["p2_name"] = user.first_name
        
        # --- CHECK TURN ---
        is_p1 = (user.id == game["p1"])
        is_p2 = (user.id == game["p2"])
        
        # Player Validation
        if game["turn"] == "X" and not is_p1:
            await q.answer("❌ Not your turn! (Waiting for X)", show_alert=True)
            return
        if game["turn"] == "O":
            if game["mode"] == "bot":
                 await q.answer("❌ Wait for Bot to move!", show_alert=True)
                 return
            if not is_p2:
                await q.answer("❌ Not your turn! (Waiting for O)", show_alert=True)
                return
        
        # Check Cell Empty
        if game["board"][idx] != " ":
            await q.answer("⚠️ Already taken!", show_alert=True)
            return
            
        # --- EXECUTE MOVE (PLAYER) ---
        game["board"][idx] = game["turn"]
        
        # CHECK WIN AFTER PLAYER MOVE
        winner = check_winner(game["board"])
        if winner:
            await end_game(q, game, winner, msg_id)
            return

        # SWITCH TURN
        game["turn"] = "O" if game["turn"] == "X" else "X"
        
        # --- IF BOT MODE: BOT MAKES MOVE ---
        if game["mode"] == "bot" and game["turn"] == "O":
            # 1. Show Player Move first (Visual update)
            await q.edit_message_text(
                f"<blockquote><b>🎮 {to_fancy('GAME ON')}</b></blockquote>\n<blockquote>🤖 <b>Turn:</b> Mimi Bot is thinking...</blockquote>",
                reply_markup=get_board_markup(msg_id),
                parse_mode=ParseMode.HTML
            )
            
            # 2. Calculate Bot Move
            # asyncio.sleep(0.5) # Optional delay for realism
            bot_idx = get_bot_move(game["board"])
            
            if bot_idx is not None:
                game["board"][bot_idx] = "O"
                
                # Check Win after Bot Move
                winner = check_winner(game["board"])
                if winner:
                    await end_game(q, game, winner, msg_id)
                    return
                
                # Switch back to Player
                game["turn"] = "X"
        
        # UPDATE UI FOR NEXT TURN
        next_player = game["p1_name"] if game["turn"] == "X" else game["p2_name"]
        
        await q.edit_message_text(
            f"<blockquote><b>🎮 {to_fancy('GAME ON')}</b></blockquote>\n<blockquote>{( '❌' if game['turn']=='X' else '⭕' )} <b>Turn:</b> {html.escape(next_player)}</blockquote>",
            reply_markup=get_board_markup(msg_id),
            parse_mode=ParseMode.HTML
        )

# --- HELPER: END GAME ---
async def end_game(q, game, winner, msg_id):
    if winner == "Draw":
        txt = f"<blockquote><b>🤝 {to_fancy('GAME DRAW')}!</b></blockquote>\n<blockquote>Nobody won this round.</blockquote>"
    else:
        w_name = game["p1_name"] if winner == "X" else game["p2_name"]
        txt = f"<blockquote><b>👑 {to_fancy('WINNER')} : {html.escape(w_name)}</b></blockquote>\n<blockquote>🎉 Congratulations!</blockquote>"
    
    if msg_id in ttt_games: del ttt_games[msg_id]
    await q.edit_message_text(txt, parse_mode=ParseMode.HTML)
