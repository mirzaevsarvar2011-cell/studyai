import os

files = {
    "requirements.txt": """aiogram==3.13.1
google-genai==0.8.0
aiosqlite==0.20.0
apscheduler==3.10.4
python-dotenv==1.0.1
pillow==11.0.0
""",
    ".env": """BOT_TOKEN=ВСТАВЬ_СЮДА_ТОКЕН_ОТ_BOTFATHER
GEMINI_API_KEY=ВСТАВЬ_СЮДА_КЛЮЧ_ОТ_GOOGLE_AI_STUDIO
""",
    "locales.py": """TEXTS = {
    "uz": {
        "choose_lang": "Tilni tanlang / Выберите язык / Choose language:",
        "menu": "Asosiy menyu. Kerakli bo'limni tanlang:",
        "btn_hw": "📚 Uy ishi / Sinf ishi",
        "btn_exam": "📝 Haftalik / Oylik imtihon",
        "btn_timetable": "⏰ Jadval va Eslatmalar",
        "btn_progress": "📊 Mening natijalarim",
        "btn_lang": "🌐 Tilni o'zgartirish",
        "choose_cat": "Yo'nalishni tanlang:",
        "cat_science": "🔬 Science (Aniq va tabiiy fanlar)",
        "cat_economy": "💼 Economy (Iqtisodiyot va huquq)",
        "choose_subj": "Fanni tanlang:",
        "hw_prompt": "Uy ishi yoki sinf ishi matnini yuboring (yoki masalaning rasmini yuklang). Men uni tushuntiraman, tekshiraman va javobini ko'rsataman:",
        "thinking": "⏳ Gemini tahlil qilmoqda...",
        "exam_type": "Imtihon turini tanlang:",
        "weekly": "📅 Haftalik imtihon (5 ta savol)",
        "monthly": "🗓 Oylik imtihon (10 ta savol)",
        "exam_q": "Savol {curr}/{total}:\\n\\n{q}",
        "exam_done": "✅ Imtihon tugadi! Natija: {score}/{total}\\n\\n{feedback}",
        "tt_info": "⏰ Hozirgi eslatma vaqti: {time}\\nYangi vaqt o'rnatish uchun HH:MM formatida yozing (masalan: 18:30) yoki o'chirish uchun 'off' deb yozing:",
        "tt_saved": "✅ Eslatma har kuni soat {time} ga o'rnatildi!",
        "tt_off": "🔕 Eslatmalar o'chirildi.",
        "notif_msg": "🔔 Dars vaqti bo'ldi! Bugungi uy ishlarini tekshirish yoki haftalik imtihon topshirishni unutmang.",
        "progress_msg": "📊 **Sizning statistikangiz:**\\n\\n✅ Tekshirilgan vazifalar: {hw}\\n📝 Topshirilgan imtihonlar: {exams}\\n⭐ O'rtacha ball: {avg}%",
        "back": "🔙 Orqaga"
    },
    "ru": {
        "choose_lang": "Tilni tanlang / Выберите язык / Choose language:",
        "menu": "Главное меню. Выберите нужный раздел:",
        "btn_hw": "📚 Домашка / Классная работа",
        "btn_exam": "📝 Недельный / Месячный экзамен",
        "btn_timetable": "⏰ Расписание и Уведомления",
        "btn_progress": "📊 Мой прогресс",
        "btn_lang": "🌐 Сменить язык",
        "choose_cat": "Выберите категорию:",
        "cat_science": "🔬 Science (Наука и IT)",
        "cat_economy": "💼 Economy (Экономика и Право)",
        "choose_subj": "Выберите предмет:",
        "hw_prompt": "Отправьте текст задания или фото тетради/учебника. Я объясню решение, проверю твой вариант и покажу правильный ответ:",
        "thinking": "⏳ Gemini проверяет и готовит разбор...",
        "exam_type": "Выберите формат экзамена:",
        "weekly": "📅 Недельный экзамен (5 вопросов)",
        "monthly": "🗓 Месячный экзамен (10 вопросов)",
        "exam_q": "Вопрос {curr}/{total}:\\n\\n{q}",
        "exam_done": "✅ Экзамен завершён! Результат: {score}/{total}\\n\\n{feedback}",
        "tt_info": "⏰ Текущее время уведомлений: {time}\\nЧтобы задать новое время, напишите его в формате ЧЧ:ММ (например: 18:30) или напишите 'off' для отключения:",
        "tt_saved": "✅ Уведомление установлено каждый день на {time}!",
        "tt_off": "🔕 Уведомления отключены.",
        "notif_msg": "🔔 Время учёбы! Самое время разобрать домашку или сдать недельный тест.",
        "progress_msg": "📊 **Твой прогресс:**\\n\\n✅ Разобрано заданий: {hw}\\n📝 Сдано экзаменов: {exams}\\n⭐ Средний балл: {avg}%",
        "back": "🔙 Назад"
    },
    "en": {
        "choose_lang": "Tilni tanlang / Выберите язык / Choose language:",
        "menu": "Main Menu. Choose an option:",
        "btn_hw": "📚 Homework / Classwork",
        "btn_exam": "📝 Weekly / Monthly Exam",
        "btn_timetable": "⏰ Timetable & Notifications",
        "btn_progress": "📊 My Progress",
        "btn_lang": "🌐 Change Language",
        "choose_cat": "Choose a category:",
        "cat_science": "🔬 Science",
        "cat_economy": "💼 Economy",
        "choose_subj": "Choose a subject:",
        "hw_prompt": "Send your homework/classwork text (or upload a photo). I will explain it, check your work, and show the answer:",
        "thinking": "⏳ Gemini is analyzing...",
        "exam_type": "Choose exam type:",
        "weekly": "📅 Weekly Exam (5 questions)",
        "monthly": "🗓 Monthly Exam (10 questions)",
        "exam_q": "Question {curr}/{total}:\\n\\n{q}",
        "exam_done": "✅ Exam completed! Score: {score}/{total}\\n\\n{feedback}",
        "tt_info": "⏰ Current reminder time: {time}\\nSend a new time in HH:MM format (e.g. 18:30) or type 'off' to disable:",
        "tt_saved": "✅ Daily reminder set for {time}!",
        "tt_off": "🔕 Notifications disabled.",
        "notif_msg": "🔔 Study time! Don't forget to review your classwork or take your weekly exam.",
        "progress_msg": "📊 **Your Progress:**\\n\\n✅ Homeworks checked: {hw}\\n📝 Exams taken: {exams}\\n⭐ Average score: {avg}%",
        "back": "🔙 Back"
    }
}

SUBJECTS = {
    "science": {
        "uz": ["Kimyo", "Biologiya", "Matematika", "IT", "Fizika", "Robototexnika"],
        "ru": ["Химия", "Биология", "Математика", "IT", "Физика", "Робототехника"],
        "en": ["Chemistry", "Biology", "Math", "IT", "Physics", "Robotics"]
    },
    "economy": {
        "uz": ["Tarix", "Iqtisodiyot", "Huquq", "Moliya", "Biznes", "Davlat huquqi va Konstitutsiya"],
        "ru": ["История", "Экономика", "Право", "Финансы", "Бизнес", "Гос. право и Конституция"],
        "en": ["History", "Economy", "Law", "Finance", "Business", "Gov Law & Constitution"]
    }
}
""",
    "database.py": """import aiosqlite

DB_NAME = "study_bot.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                lang TEXT DEFAULT 'ru',
                hw_count INTEGER DEFAULT 0,
                reminder_time TEXT DEFAULT NULL
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS exams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                subject TEXT,
                exam_type TEXT,
                score INTEGER,
                total INTEGER
            )
        ''')
        await db.commit()

async def set_user_lang(user_id: int, lang: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT INTO users (user_id, lang) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET lang=excluded.lang
        ''', (user_id, lang))
        await db.commit()

async def get_user_lang(user_id: int) -> str:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT lang FROM users WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 'ru'

async def increment_hw(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE users SET hw_count = hw_count + 1 WHERE user_id = ?', (user_id,))
        await db.commit()

async def save_exam(user_id: int, subject: str, exam_type: str, score: int, total: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            'INSERT INTO exams (user_id, subject, exam_type, score, total) VALUES (?, ?, ?, ?, ?)',
            (user_id, subject, exam_type, score, total)
        )
        await db.commit()

async def get_progress(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT hw_count FROM users WHERE user_id = ?', (user_id,)) as c:
            row = await c.fetchone()
            hw = row[0] if row else 0
        async with db.execute('SELECT score, total FROM exams WHERE user_id = ?', (user_id,)) as c:
            rows = await c.fetchall()
            exams = len(rows)
            avg = round(sum((r[0] / r[1]) * 100 for r in rows) / exams, 1) if exams > 0 else 0
            return hw, exams, avg

async def set_reminder(user_id: int, time_str: str | None):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE users SET reminder_time = ? WHERE user_id = ?', (time_str, user_id))
        await db.commit()

async def get_reminder(user_id: int) -> str:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT reminder_time FROM users WHERE user_id = ?', (user_id,)) as c:
            row = await c.fetchone()
            return row[0] if row and row[0] else "OFF"

async def get_users_by_time(time_str: str):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT user_id, lang FROM users WHERE reminder_time = ?', (time_str,)) as c:
            return await c.fetchall()
""",
    "gemini_service.py": """import os
import json
from io import BytesIO
from PIL import Image
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-2.5-flash"

LANG_MAP = {"uz": "Uzbek", "ru": "Russian", "en": "English"}

async def check_homework(subject: str, lang: str, text: str = "", image_bytes: bytes = None) -> str:
    target_lang = LANG_MAP.get(lang, "Russian")
    prompt = f\"\"\"You are an expert tutor in {subject}. Respond strictly in {target_lang}.
The student sent homework or classwork.
1. Explain the topic/problem clearly step-by-step.
2. If the student included their own attempt/answer, check it and point out any mistakes.
3. Show the clear final answer at the end.
Keep formatting clean using plain text and bullet points (avoid complex markdown tables).
Student input: {text}\"\"\"

    contents = [prompt]
    if image_bytes:
        img = Image.open(BytesIO(image_bytes))
        contents.append(img)

    response = await client.aio.models.generate_content(model=MODEL, contents=contents)
    return response.text

async def generate_exam(subject: str, lang: str, count: int) -> list[dict]:
    target_lang = LANG_MAP.get(lang, "Russian")
    prompt = f\"\"\"Create a {count}-question multiple-choice exam on {subject} in {target_lang}.
Return ONLY a valid JSON array of objects, with no extra text or code fences.
Format:
[
  {{"q": "Question text", "options": ["A) ...", "B) ...", "C) ...", "D) ..."], "answer": 0}}
]
Where "answer" is the 0-based index (0, 1, 2, or 3) of the correct option.\"\"\"

    response = await client.aio.models.generate_content(model=MODEL, contents=prompt)
    raw = response.text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(raw)
""",
    "bot.py": """import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import database as db
from locales import TEXTS, SUBJECTS
import gemini_service as ai

load_dotenv()
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

class StudyState(StatesGroup):
    choosing_subject = State()
    waiting_hw = State()
    taking_exam = State()
    setting_time = State()

def main_menu_kb(lang: str) -> ReplyKeyboardMarkup:
    t = TEXTS[lang]
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t["btn_hw"]), KeyboardButton(text=t["btn_exam"])],
            [KeyboardButton(text=t["btn_timetable"]), KeyboardButton(text=t["btn_progress"])],
            [KeyboardButton(text=t["btn_lang"])]
        ],
        resize_keyboard=True
    )

def lang_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang_uz"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
        ]
    ])

def category_kb(lang: str, mode: str) -> InlineKeyboardMarkup:
    t = TEXTS[lang]
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t["cat_science"], callback_data=f"cat_{mode}_science")],
        [InlineKeyboardButton(text=t["cat_economy"], callback_data=f"cat_{mode}_economy")]
    ])

def subjects_kb(lang: str, mode: str, cat: str) -> InlineKeyboardMarkup:
    subs = SUBJECTS[cat][lang]
    rows = [[InlineKeyboardButton(text=s, callback_data=f"subj_{mode}_{cat}_{i}")] for i, s in enumerate(subs)]
    return InlineKeyboardMarkup(inline_keyboard=rows)

@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(TEXTS["ru"]["choose_lang"], reply_markup=lang_kb())

@dp.callback_query(F.data.startswith("lang_"))
async def set_lang_cb(call: CallbackQuery):
    lang = call.data.split("_")[1]
    await db.set_user_lang(call.from_user.id, lang)
    await call.message.delete()
    await call.message.answer(TEXTS[lang]["menu"], reply_markup=main_menu_kb(lang))

@dp.message(F.text.in_([TEXTS["uz"]["btn_lang"], TEXTS["ru"]["btn_lang"], TEXTS["en"]["btn_lang"]]))
async def change_lang_btn(message: Message):
    await message.answer(TEXTS["ru"]["choose_lang"], reply_markup=lang_kb())

# --- HOMEWORK & CLASSWORK ---
@dp.message(F.text.in_([TEXTS["uz"]["btn_hw"], TEXTS["ru"]["btn_hw"], TEXTS["en"]["btn_hw"]]))
async def hw_start(message: Message, state: FSMContext):
    await state.clear()
    lang = await db.get_user_lang(message.from_user.id)
    await message.answer(TEXTS[lang]["choose_cat"], reply_markup=category_kb(lang, "hw"))

# --- EXAMS ---
@dp.message(F.text.in_([TEXTS["uz"]["btn_exam"], TEXTS["ru"]["btn_exam"], TEXTS["en"]["btn_exam"]]))
async def exam_start(message: Message, state: FSMContext):
    await state.clear()
    lang = await db.get_user_lang(message.from_user.id)
    await message.answer(TEXTS[lang]["choose_cat"], reply_markup=category_kb(lang, "exam"))

@dp.callback_query(F.data.startswith("cat_"))
async def choose_category_cb(call: CallbackQuery):
    _, mode, cat = call.data.split("_")
    lang = await db.get_user_lang(call.from_user.id)
    await call.message.edit_text(TEXTS[lang]["choose_subj"], reply_markup=subjects_kb(lang, mode, cat))

@dp.callback_query(F.data.startswith("subj_"))
async def choose_subject_cb(call: CallbackQuery, state: FSMContext):
    _, mode, cat, idx = call.data.split("_")
    lang = await db.get_user_lang(call.from_user.id)
    subject = SUBJECTS[cat][lang][int(idx)]
    await state.update_data(subject=subject)

    if mode == "hw":
        await state.set_state(StudyState.waiting_hw)
        await call.message.edit_text(f"📌 **{subject}**\\n\\n{TEXTS[lang]['hw_prompt']}")
    else:
        t = TEXTS[lang]
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t["weekly"], callback_data="examtype_weekly")],
            [InlineKeyboardButton(text=t["monthly"], callback_data="examtype_monthly")]
        ])
        await call.message.edit_text(f"📌 **{subject}**\\n\\n{t['exam_type']}", reply_markup=kb)

@dp.message(StudyState.waiting_hw)
async def process_homework(message: Message, state: FSMContext):
    lang = await db.get_user_lang(message.from_user.id)
    data = await state.get_data()
    subject = data.get("subject", "General")
    wait_msg = await message.answer(TEXTS[lang]["thinking"])

    img_bytes = None
    if message.photo:
        file = await bot.get_file(message.photo[-1].file_id)
        buf = await bot.download_file(file.file_path)
        img_bytes = buf.read()

    text = message.caption or message.text or ""
    result = await ai.check_homework(subject, lang, text=text, image_bytes=img_bytes)
    await db.increment_hw(message.from_user.id)
    await wait_msg.delete()
    await message.answer(result)

@dp.callback_query(F.data.startswith("examtype_"))
async def start_exam_cb(call: CallbackQuery, state: FSMContext):
    exam_type = call.data.split("_")[1]
    count = 5 if exam_type == "weekly" else 10
    lang = await db.get_user_lang(call.from_user.id)
    data = await state.get_data()
    subject = data.get("subject", "General")

    await call.message.edit_text(TEXTS[lang]["thinking"])
    questions = await ai.generate_exam(subject, lang, count)
    await state.set_state(StudyState.taking_exam)
    await state.update_data(questions=questions, q_idx=0, score=0, exam_type=exam_type)
    await send_exam_question(call.message, lang, questions, 0)

async def send_exam_question(msg: Message, lang: str, questions: list, idx: int):
    q_data = questions[idx]
    opts = q_data["options"]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=opt, callback_data=f"ans_{i}")] for i, opt in enumerate(opts)
    ])
    text = TEXTS[lang]["exam_q"].format(curr=idx + 1, total=len(questions), q=q_data["q"])
    await msg.edit_text(text, reply_markup=kb)

@dp.callback_query(StudyState.taking_exam, F.data.startswith("ans_"))
async def answer_exam_cb(call: CallbackQuery, state: FSMContext):
    chosen = int(call.data.split("_")[1])
    data = await state.get_data()
    questions = data["questions"]
    idx = data["q_idx"]
    score = data["score"]

    if chosen == questions[idx]["answer"]:
        score += 1

    next_idx = idx + 1
    lang = await db.get_user_lang(call.from_user.id)

    if next_idx < len(questions):
        await state.update_data(q_idx=next_idx, score=score)
        await send_exam_question(call.message, lang, questions, next_idx)
    else:
        total = len(questions)
        await db.save_exam(call.from_user.id, data["subject"], data["exam_type"], score, total)
        await state.clear()
        summary = TEXTS[lang]["exam_done"].format(score=score, total=total, feedback=f"Subject: {data['subject']}")
        await call.message.edit_text(summary)

# --- TIMETABLE & PROGRESS ---
@dp.message(F.text.in_([TEXTS["uz"]["btn_timetable"], TEXTS["ru"]["btn_timetable"], TEXTS["en"]["btn_timetable"]]))
async def timetable_btn(message: Message, state: FSMContext):
    lang = await db.get_user_lang(message.from_user.id)
    curr = await db.get_reminder(message.from_user.id)
    await state.set_state(StudyState.setting_time)
    await message.answer(TEXTS[lang]["tt_info"].format(time=curr))

@dp.message(StudyState.setting_time)
async def save_timetable(message: Message, state: FSMContext):
    lang = await db.get_user_lang(message.from_user.id)
    val = message.text.strip().lower()
    if val == "off":
        await db.set_reminder(message.from_user.id, None)
        await state.clear()
        await message.answer(TEXTS[lang]["tt_off"], reply_markup=main_menu_kb(lang))
        return
    try:
        datetime.strptime(val, "%H:%M")
        await db.set_reminder(message.from_user.id, val)
        await state.clear()
        await message.answer(TEXTS[lang]["tt_saved"].format(time=val), reply_markup=main_menu_kb(lang))
    except ValueError:
        await message.answer("❌ Format: HH:MM (e.g. 18:30)")

@dp.message(F.text.in_([TEXTS["uz"]["btn_progress"], TEXTS["ru"]["btn_progress"], TEXTS["en"]["btn_progress"]]))
async def progress_btn(message: Message):
    lang = await db.get_user_lang(message.from_user.id)
    hw, exams, avg = await db.get_progress(message.from_user.id)
    await message.answer(TEXTS[lang]["progress_msg"].format(hw=hw, exams=exams, avg=avg))

async def check_notifications():
    now_str = datetime.now().strftime("%H:%M")
    users = await db.get_users_by_time(now_str)
    for user_id, lang in users:
        try:
            await bot.send_message(user_id, TEXTS[lang]["notif_msg"])
        except Exception:
            pass

async def main():
    await db.init_db()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_notifications, "cron", second=0)
    scheduler.start()
    print("Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
"""
}

for filename, content in files.items():
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

print("✅ Все файлы проекта успешно созданы!")