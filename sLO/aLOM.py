import logging
import random
import asyncio
from typing import Dict, Optional, List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

# ========= CONFIG =========
TOKEN = "7780908362:AAFdmlpAYvir1RzCz2TGJBOJeqlClfzC5hI"
MIN_PLAYERS = 3 
NIGHT_DURATION = 45
DAY_DURATION = 60
# ==========================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

games: Dict[int, dict] = {}
user_settings: Dict[int, str] = {}

LANGUAGES = {
    'uz': {
        'START_MESSAGE': "Salom! Mafia o‘yini. Tilni tanlang (yoki /help):",
        'LANGUAGE_SELECTED': "✅ Til *O‘zbek* tiliga o‘rnatildi.",
        'CREATE_INSTRUCTION': "Iltimos o‘yin kodi kiriting: `/create 1234`",
        'GAME_EXISTS': "Bu chatda o‘yin allaqachon mavjud.",
        'GAME_CREATED':
            """🆕 O‘yin yaratildi!
👑 Host: **{host_name}**
🔢 O‘yin kodi: **{code}**
O‘yinchilar `/join {code}` orqali qo‘shilishi mumkin.
Minimal o‘yinchi: **{min_players}**

⚠️ **MUHIM:** Har bir o‘yinchi rollarni olish va harakat qilishi uchun bot bilan PM orqali yozishni boshlashi kerak.

Host: O‘yinni boshlash uchun `/startgame` buyrug‘ini yuboring!""",
        'JOIN_INSTRUCTION': "Iltimos o‘yin kodini kiriting: `/join 1234`",
        'GAME_NOT_FOUND': "O‘yin topilmadi. Avval /create qilin.",
        'INVALID_CODE': "❌ Noto‘g‘ri kod.",
        'ALREADY_IN_GAME': "Siz allaqachon o‘yin ichidasiz.",
        'GAME_STARTED': "O‘yin boshlangan.",
        'PLAYER_JOINED': """✅ **{user_name}** o‘yinga qo‘shildi!
Jami o‘yinchi: **{player_count}**

⚠️ PM orqali botga /start yuborganingizga ishonch hosil qiling!""",
        'NO_ACTIVE_GAME': "Bu chatda faol o‘yin yo‘q.",
        'HOST_ONLY': "❌ Faqat host bu buyruqni bera oladi.",
        'GAME_CANCELED': "🛑 O‘yin host tomonidan bekor qilindi.",
        'NOT_IN_GAME': "O‘yinda emassiz.",
        'CANT_LEAVE': "O‘yin boshlanganidan keyin chiqib bo‘lmaydi.",
        'PLAYER_LEFT': "**{user_name}** o‘yindan chiqdi.",

        'STATUS_TITLE':
            "🟦 O‘yin holati: **{phase}**\n🔢 O‘yin kodi: **{code}**\n👥 O‘yinchilar: **{player_count}**",

        'STATUS_PLAYER_LINE': "- {player_name} {icon}{role_info}\n",

        'ROLE_MAP': {
            "mafia": "Mafiya 🔪",
            "doctor": "Doktor 💉",
            "detective": "Detektiv 🕵️",
            "town": "Tinch aholi 🏘️"
        },

        'ROLE_DESCRIPTIONS': {
            "mafia": "Siz har kecha tinch aholidan birini o'ldirasiz.",
            "doctor": "Siz har kecha bir o‘yinchini qutqarishingiz mumkin.",
            "detective": "Har kecha bir o‘yinchini tekshirishingiz mumkin.",
            "town": "Sizning vazifangiz mafiyani topish."
        },

        'MIN_PLAYERS_ERR': "Kam o‘yinchi: **{min_players}** ta kerak.",
        'GAME_ALREADY_STARTED': "O‘yin allaqachon boshlangan.",

        'GAME_STARTED_PM':
            """🎉 **O‘yin boshlandi!**
Sizning rolingiz: **{role_name}**
Vazifa: {description}{extra_info}""",

        'OTHER_MAFIA': "\n\nBoshqa Mafiya: **{mafia_members}**",
        'ALONE_MAFIA': "\n\nSiz yolg‘iz Mafiyasiz.",

        'GAME_STARTED_CHAT': "O‘yin boshlandi! Tun boshlandi.",

        'NIGHT_START': "🌙 **Tun boshlandi!** ({duration} soniya)",
        'NIGHT_END': "⏰ Tun tugadi. Natijalar...",

        'ACTION_MAFIA': "🔪 Kimni o‘ldirmoqchisiz?",
        'ACTION_DOCTOR': "💉 Kimni qutqarmoqchisiz?",
        'ACTION_DETECTIVE': "🕵️ Kimni tekshirmoqchisiz?",
        'ACTION_TOWN': "Siz tinch aholisiz. Harakatingiz yo‘q.",

        'NIGHT_ACTION_TITLE': "🌙 **Tun harakati** ({role_name}):\n{action_text}",

        'DETECTIVE_RESULT_MAFIA': "{target_name} — **Mafiya**.",
        'DETECTIVE_RESULT_TOWN': "{target_name} — **Tinch aholi**.",

        'KILLED_ANNOUNCEMENT': "🚨 Tunda o‘ldirilgan: **{killed_name}** ({role_name})",
        'NO_KILL_ANNOUNCEMENT': "🕊️ Hech kim o‘lmagan.",

        'DAY_START': "☀️ **Kun boshlandi!** ({duration} soniya)",

        'VOTE_RECEIVED': "Siz **{target_name}** ga ovoz berdingiz.",
        'VOTE_RESULT_EJECTED':
            "🗳️ **{ejected_name}** chiqarildi. (Roli: {role_name})",
        'VOTE_RESULT_TIE': "⚖️ Ovozlar teng.",
        'VOTE_RESULT_NONE': "Hech kimga ovoz berilmadi.",

        'WINNER_TOWN': "TINCH AHOLI",
        'WINNER_MAFIA': "MAFIYA",

        'GAME_ENDED_TITLE': "🏆 **G‘olib:** {winner}!",
        'GAME_ENDED_SUMMARY': "**Rollar:**\n{roles_summary}",

        'ACTION_ACCEPTED': "Tanlov qabul qilindi.",
        'NO_ACTIVE_NIGHT': "Tun faol emas.",
        'DEAD_PLAYER_ACTION': "Siz o‘lgansiz.",
        'INVALID_TARGET': "Noto‘g‘ri nishon.",

        'ACTION_MAFIA_CONFIRM': "**{target_name}** ni o‘ldirishingiz belgilandi.",
        'ACTION_DOCTOR_CONFIRM': "**{target_name}** ni qutqarishingiz belgilandi.",
        'ACTION_DETECTIVE_CONFIRM': "**{target_name}** ni tekshirasiz.",

        'INVALID_ACTION': "Noto‘g‘ri harakat.",
        'ROLE_UNDEF': "Tugallanmagan",
        'ROLE_UNKNOWN': "Noma'lum"
    },

    'en': {
        "START_MESSAGE": "Hello! Mafia Game. Choose your language:",
        "LANGUAGE_SELECTED": "Language set to English.",
        "CREATE_INSTRUCTION": "Please enter a game code: `/create 1234`",
        "GAME_EXISTS": "A game already exists in this chat.",
        "GAME_CREATED":
            """🆕 Game created!
👑 Host: **{host_name}**
🔢 Game code: **{code}**
Players can join via `/join {code}`
Minimum players: **{min_players}**

⚠️ IMPORTANT: Every player must start PM with the bot (`/start`) to receive role and night actions.

Host: Start game with `/startgame`""",
        
    }
}
# === YORDAMCHI FUNKSIYALAR ===

def get_text(user_id: int, key: str) -> str:
    """Foydalanuvchi tiliga mos matn qaytaradi."""
    lang = user_settings.get(user_id, 'uz')
    return LANGUAGES.get(lang, LANGUAGES['uz']).get(key, f"[{key}]")

def get_role_name(user_id: int, role: str) -> str:
    lang = user_settings.get(user_id, 'uz')
    return LANGUAGES[lang]['ROLE_MAP'].get(role, role)

def find_player(game: dict, user_id: int) -> Optional[dict]:
    for p in game['players']:
        if p['id'] == user_id:
            return p
    return None

def alive_players(game: dict) -> List[dict]:
    return [p for p in game['players'] if p['alive']]

def get_role_counts(game: dict) -> Dict[str, int]:
    count_mafia = sum(1 for p in game['players'] if p['alive'] and p['role'] == "mafia")
    count_town = sum(1 for p in game['players'] if p['alive'] and p['role'] != "mafia")
    return {"mafia": count_mafia, "town": count_town}

async def send_to_player(app, user_id: int, text: str, reply_markup=None):
    try:
        await app.bot.send_message(
            chat_id=user_id,
            text=text,
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Error sending PM to {user_id}: {e}")

async def send_role_buttons_for_action(app, game: dict, player: dict, title: str):
    """Tungi harakat tugmalari"""
    targets = []
    for p in alive_players(game):
        if player['role'] == "detective" and p['id'] == player['id']:
            continue
        targets.append([InlineKeyboardButton(p['name'], callback_data=f"act_{p['id']}")])

    if not targets:
        await send_to_player(app, player['id'], title)
        return

    kb = InlineKeyboardMarkup(targets)
    await send_to_player(app, player['id'], title, kb)
# ======== TIL TANLASH CALLBACK ========

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    lang_code = query.data.replace("lang_", "")

    user_settings[user_id] = lang_code
    msg = LANGUAGES[lang_code]['LANGUAGE_SELECTED']

    await query.edit_message_text(msg)


# ======== /start ========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    # Faqat PMda til tanlash bo‘ladi
    if chat.type == "private":
        keyboard = [
            [InlineKeyboardButton("🇺🇿 O‘zbek", callback_data="lang_uz")],
            [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
        ]
        await update.message.reply_text(
            LANGUAGES['uz']['START_MESSAGE'],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text("Bot shaxsiy xabarda (/start) bilan ishlaydi.")


# ======== /create ========

async def create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    if chat_id in games:
        await update.message.reply_text(
            get_text(user.id, 'GAME_EXISTS')
        )
        return

    if len(context.args) != 1:
        await update.message.reply_text(
            get_text(user.id, 'CREATE_INSTRUCTION')
        )
        return

    code = context.args[0]

    games[chat_id] = {
        "code": code,
        "host_id": user.id,
        "players": [{"id": user.id, "name": user.first_name, "alive": True, "role": None}],
        "phase": "lobby",
        "night_actions": {},
        "votes": {},
        "night_task": None,
        "day_task": None,
        "started": False
    }

    await update.message.reply_text(
        get_text(user.id, 'GAME_CREATED').format(
            host_name=user.first_name,
            code=code,
            min_players=MIN_PLAYERS
        )
    )


# ======== /join ========

async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    if chat_id not in games:
        await update.message.reply_text(get_text(user.id, 'GAME_NOT_FOUND'))
        return

    if len(context.args) != 1:
        await update.message.reply_text(get_text(user.id, 'JOIN_INSTRUCTION'))
        return

    code = context.args[0]
    game = games[chat_id]

    if game['code'] != code:
        await update.message.reply_text(get_text(user.id, 'INVALID_CODE'))
        return

    if find_player(game, user.id):
        await update.message.reply_text(get_text(user.id, 'ALREADY_IN_GAME'))
        return

    if game['started']:
        await update.message.reply_text(get_text(user.id, 'GAME_STARTED'))
        return

    game['players'].append({
        "id": user.id,
        "name": user.first_name,
        "alive": True,
        "role": None
    })

    await update.message.reply_text(
        get_text(user.id, 'PLAYER_JOINED').format(
            user_name=user.first_name,
            player_count=len(game['players'])
        )
    )


# ======== /leave ========

async def leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    if chat_id not in games:
        await update.message.reply_text(get_text(user.id, 'NO_ACTIVE_GAME'))
        return

    game = games[chat_id]

    if find_player(game, user.id) is None:
        await update.message.reply_text(get_text(user.id, 'NOT_IN_GAME'))
        return

    if game['started']:
        await update.message.reply_text(get_text(user.id, 'CANT_LEAVE'))
        return

    game['players'] = [p for p in game['players'] if p['id'] != user.id]

    await update.message.reply_text(
        get_text(user.id, 'PLAYER_LEFT').format(user_name=user.first_name)
    )


# ======== /endgame (faqat HOST) ========

async def endgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    if chat_id not in games:
        await update.message.reply_text(get_text(user.id, 'NO_ACTIVE_GAME'))
        return

    game = games[chat_id]

    if user.id != game['host_id']:
        await update.message.reply_text(get_text(user.id, 'HOST_ONLY'))
        return

    del games[chat_id]

    await update.message.reply_text(get_text(user.id, 'GAME_CANCELED'))


# ======== /status ========

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    if chat_id not in games:
        await update.message.reply_text(get_text(user.id, 'NO_ACTIVE_GAME'))
        return

    game = games[chat_id]

    txt = get_text(user.id, 'STATUS_TITLE').format(
        phase=game['phase'],
        code=game['code'],
        player_count=len(game['players'])
    )

    for p in game['players']:
        icon = "🟢" if p['alive'] else "🔴"

        role_key = p['role'] or "ROLE_UNDEF"
        role_name = LANGUAGES[user_settings.get(user.id, 'uz')]['ROLE_MAP'].get(
            p['role'], get_text(user.id, 'ROLE_UNKNOWN')
        )

        if game['phase'] == "lobby":
            role_name = get_text(user.id, 'ROLE_UNDEF')

        txt += get_text(user.id, 'STATUS_PLAYER_LINE').format(
            player_name=p['name'],
            icon=icon,
            role_info=f"({role_name})"
        )

    await update.message.reply_text(txt)


# ======== /help ========

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    await update.message.reply_text(
        "BUYRUQLAR:\n"
        "/create 1234 – o‘yin yaratish\n"
        "/join 1234 – o‘yinga qo‘shilish\n"
        "/startgame – o‘yinni boshlash\n"
        "/status – o‘yin holati\n"
        "/leave – o‘yindan chiqish\n"
        "/endgame – host o‘yinni tugatadi\n"
        "/help – yordam"
    )
# ============================
#   /startgame — O‘YIN BOSHLASH
# ============================

async def startgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    if chat_id not in games:
        await update.message.reply_text(get_text(user.id, 'NO_ACTIVE_GAME'))
        return

    game = games[chat_id]

    if user.id != game['host_id']:
        await update.message.reply_text(get_text(user.id, 'HOST_ONLY'))
        return

    if len(game['players']) < MIN_PLAYERS:
        await update.message.reply_text(
            get_text(user.id, 'MIN_PLAYERS_ERR').format(min_players=MIN_PLAYERS)
        )
        return

    if game['started']:
        await update.message.reply_text(get_text(user.id, 'GAME_ALREADY_STARTED'))
        return

    game['started'] = True

    # === Rollarni tasodifiy taqsimlash ===
    players = game['players']
    roles_pool = ["mafia", "doctor", "detective"] + ["town"] * (len(players) - 3)
    random.shuffle(roles_pool)

    for p, r in zip(players, roles_pool):
        p['role'] = r

    # PMga rollarni yuborish
    app = context.application

    for p in players:
        lang = user_settings.get(p['id'], 'uz')
        role_name = LANGUAGES[lang]['ROLE_MAP'][p['role']]
        desc = LANGUAGES[lang]['ROLE_DESCRIPTIONS'][p['role']]

        extra = ""
        if p['role'] == "mafia":
            mafia_members = [x['name'] for x in players if x['role'] == "mafia" and x['id'] != p['id']]
            if mafia_members:
                extra = LANGUAGES[lang]['OTHER_MAFIA'].format(mafia_members=", ".join(mafia_members))
            else:
                extra = LANGUAGES[lang]['ALONE_MAFIA']

        await send_to_player(
            app,
            p['id'],
            LANGUAGES[lang]['GAME_STARTED_PM'].format(
                role_name=role_name,
                description=desc,
                extra_info=extra
            )
        )

    await update.message.reply_text(get_text(user.id, 'GAME_STARTED_CHAT'))

    # Birinchi tunni boshlaymiz
    await night_phase(chat_id, context)


# ============================
#           TUN BOSHLASH
# ============================

async def night_phase(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    if chat_id not in games:
        return

    game = games[chat_id]
    game['phase'] = "night"
    game['night_actions'] = {}

    app = context.application

    # Guruhga e’lon
    for p in game['players']:
        if p['alive']:
            await app.bot.send_message(
                chat_id=chat_id,
                text=get_text(p['id'], 'NIGHT_START').format(duration=NIGHT_DURATION)
            )

    # Har bir o‘yinchiga harakat tugmalari
    for p in alive_players(game):
        lang = user_settings.get(p['id'], 'uz')
        role = p['role']

        if role == "mafia":
            text = LANGUAGES[lang]['ACTION_MAFIA']
        elif role == "doctor":
            text = LANGUAGES[lang]['ACTION_DOCTOR']
        elif role == "detective":
            text = LANGUAGES[lang]['ACTION_DETECTIVE']
        else:
            text = LANGUAGES[lang]['ACTION_TOWN']
            await send_to_player(app, p['id'], text)
            continue

        title = LANGUAGES[lang]['NIGHT_ACTION_TITLE'].format(
            role_name=LANGUAGES[lang]['ROLE_MAP'][role],
            action_text=text
        )

        await send_role_buttons_for_action(app, game, p, title)

    # Tun davomiyligi
    await asyncio.sleep(NIGHT_DURATION)

    # Tun tugashi
    await finalize_night(chat_id, context)


# ============================
#        TUN NATIJALARI
# ============================

async def finalize_night(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    if chat_id not in games:
        return

    game = games[chat_id]
    app = context.application

    # Guruhga e’lon
    for p in game['players']:
        await app.bot.send_message(
            chat_id=chat_id,
            text=get_text(p['id'], 'NIGHT_END')
        )

    mafia_target = game['night_actions'].get("mafia")
    doctor_save = game['night_actions'].get("doctor")

    killed = None

    if mafia_target and mafia_target != doctor_save:
        player = find_player(game, mafia_target)
        if player:
            player['alive'] = False
            killed = player

    # Natijani e’lon qilish
    for p in game['players']:
        lang = user_settings.get(p['id'], 'uz')

        if killed:
            await app.bot.send_message(
                chat_id=chat_id,
                text=LANGUAGES[lang]['KILLED_ANNOUNCEMENT'].format(
                    killed_name=killed['name'],
                    role_name=LANGUAGES[lang]['ROLE_MAP'][killed['role']]
                )
            )
        else:
            await app.bot.send_message(
                chat_id=chat_id,
                text=LANGUAGES[lang]['NO_KILL_ANNOUNCEMENT']
            )

    # G‘olib bormi?
    if await check_win(chat_id, context):
        return

    # Kunga o‘tish
    await day_phase(chat_id, context)


# ============================
#      KUN BOSHLASH (OVOZ)
# ============================

async def day_phase(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    if chat_id not in games:
        return

    game = games[chat_id]
    game['phase'] = "day"
    game['votes'] = {}

    app = context.application

    # Guruhga e’lon
    for p in alive_players(game):
        await app.bot.send_message(
            chat_id=chat_id,
            text=get_text(p['id'], 'DAY_START').format(duration=DAY_DURATION)
        )

    # Ovoz berish tugmalari
    kb = []
    for p in alive_players(game):
        kb.append([InlineKeyboardButton(p['name'], callback_data=f"vote_{p['id']}")])

    markup = InlineKeyboardMarkup(kb)

    for p in alive_players(game):
        await send_to_player(app, p['id'], "🗳️ Ovoz bering:", markup)

    await asyncio.sleep(DAY_DURATION)

    # Ovozlar natijasi
    await finalize_votes(chat_id, context)


# ============================
#       OVOZ NATIJALARI
# ============================

async def finalize_votes(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    if chat_id not in games:
        return

    game = games[chat_id]
    app = context.application
    votes = game['votes']

    if not votes:
        for p in game['players']:
            await app.bot.send_message(
                chat_id=chat_id,
                text=get_text(p['id'], 'VOTE_RESULT_NONE')
            )
        await night_phase(chat_id, context)
        return

    # Ovozlarni sanash
    counts = {}
    for voter, target in votes.items():
        counts[target] = counts.get(target, 0) + 1

    # Maksimal ovoz
    top = max(counts.values())
    winners = [pid for pid, cnt in counts.items() if cnt == top]

    if len(winners) != 1:
        for p in game['players']:
            await app.bot.send_message(
                chat_id=chat_id,
                text=get_text(p['id'], 'VOTE_RESULT_TIE')
            )
        await night_phase(chat_id, context)
        return

    # Chqarib yuboriladigan o‘yinchi
    out_id = winners[0]
    out_player = find_player(game, out_id)

    if out_player:
        out_player['alive'] = False

        for p in game['players']:
            lang = user_settings.get(p['id'], 'uz')
            await app.bot.send_message(
                chat_id=chat_id,
                text=LANGUAGES[lang]['VOTE_RESULT_EJECTED'].format(
                    ejected_name=out_player['name'],
                    role_name=LANGUAGES[lang]['ROLE_MAP'][out_player['role']]
                )
            )

    # G‘olib bormi?
    if await check_win(chat_id, context):
        return

    await night_phase(chat_id, context)


# ============================
#   TUGMA CALLBACK — HARAQATLAR
# ============================

async def role_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    chat_id = query.message.chat_id

    if chat_id not in games:
        return

    game = games[chat_id]
    player = find_player(game, user.id)

    if not player or not player['alive']:
        await query.edit_message_text(get_text(user.id, 'DEAD_PLAYER_ACTION'))
        return

    if not query.data.startswith("act_"):
        return

    target_id = int(query.data.split("_")[1])
    target = find_player(game, target_id)

    if not target or not target['alive']:
        await query.edit_message_text(get_text(user.id, 'INVALID_TARGET'))
        return

    role = player['role']

    if role == "mafia":
        game['night_actions']['mafia'] = target_id
        await query.edit_message_text(
            get_text(user.id, 'ACTION_MAFIA_CONFIRM').format(target_name=target['name'])
        )

    elif role == "doctor":
        game['night_actions']['doctor'] = target_id
        await query.edit_message_text(
            get_text(user.id, 'ACTION_DOCTOR_CONFIRM').format(target_name=target['name'])
        )

    elif role == "detective":
        game['night_actions']['detective'] = target_id
        lang = user_settings.get(user.id, 'uz')

        if target['role'] == "mafia":
            text = LANGUAGES[lang]['DETECTIVE_RESULT_MAFIA']
        else:
            text = LANGUAGES[lang]['DETECTIVE_RESULT_TOWN']

        text = text.format(target_name=target['name'])

        await query.edit_message_text(text)

    else:
        await query.edit_message_text(get_text(user.id, 'INVALID_ACTION'))
# ============================
#        G‘OLIBNI ANIQLASH
# ============================

async def check_win(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    if chat_id not in games:
        return True

    game = games[chat_id]
    counts = get_role_counts(game)

    mafia = counts['mafia']
    town = counts['town']

    # Agar mafia yo‘q bo‘lsa → Town g‘olib
    if mafia == 0:
        await end_game(chat_id, context, winner="town")
        return True

    # Agar mafia >= town bo‘lib qolsa → Mafia g‘olib
    if mafia >= town:
        await end_game(chat_id, context, winner="mafia")
        return True

    return False


# ============================
#        O‘YINNI YAKUNLASH
# ============================

async def end_game(chat_id: int, context: ContextTypes.DEFAULT_TYPE, winner: str):
    if chat_id not in games:
        return

    game = games[chat_id]
    app = context.application

    # Rollar ro‘yxati
    summary = ""
    for p in game['players']:
        lang = user_settings.get(p['id'], 'uz')
        role_name = LANGUAGES[lang]['ROLE_MAP'][p['role']]
        summary += f"{p['name']} — {role_name}\n"

    for p in game['players']:
        lang = user_settings.get(p['id'], 'uz')

        txt = (
            LANGUAGES[lang]['GAME_ENDED_TITLE'].format(
                winner=LANGUAGES[lang]['WINNER_TOWN'] if winner == "town"
                else LANGUAGES[lang]['WINNER_MAFIA']
            )
            + "\n\n"
            + LANGUAGES[lang]['GAME_ENDED_SUMMARY'].format(
                roles_summary=summary
            )
        )

        await app.bot.send_message(chat_id=chat_id, text=txt)

    # O‘yinni o‘chirib tashlash
    del games[chat_id]


# ============================
#       HANDLERLARNI ULASH
# ============================

def setup_handlers(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))

    app.add_handler(CommandHandler("create", create))
    app.add_handler(CommandHandler("join", join))
    app.add_handler(CommandHandler("leave", leave))
    app.add_handler(CommandHandler("endgame", endgame))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("startgame", startgame))

    app.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(role_callback, pattern="^act_"))
    app.add_handler(CallbackQueryHandler(role_callback, pattern="^vote_"))


# ============================
#         BOTNI ISHGA TUSHIRISH
# ============================

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    setup_handlers(app)

    print("Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()