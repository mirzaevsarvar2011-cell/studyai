import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import database as db
from locales import TEXTS, SUBJECTS
import gemini_service as ai

load_dotenv()
bot = Bot(
    token=os.getenv("BOT_TOKEN"),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
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
        await call.message.edit_text(f"📌 <b>{subject}</b>\n\n{TEXTS[lang]['hw_prompt']}")
    else:
        t = TEXTS[lang]
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t["weekly"], callback_data="examtype_weekly")],
            [InlineKeyboardButton(text=t["monthly"], callback_data="examtype_monthly")]
        ])
        await call.message.edit_text(f"📌 <b>{subject}</b>\n\n{t['exam_type']}", reply_markup=kb)


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
    if not questions:
        await call.message.edit_text("⚠️ Не удалось сгенерировать вопросы (сервер ИИ временно недоступен). Попробуйте позже.")
        return

    await state.set_state(StudyState.taking_exam)
    await state.update_data(questions=questions, q_idx=0, score=0, exam_type=exam_type)
    await send_exam_question(call.message, lang, questions, 0)


async def send_exam_question(msg: Message, lang: str, questions: list, idx: int):
    q_data = questions[idx]
    opts = q_data["options"]
    q_text = q_data.get("question") or q_data.get("q", "")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=opt, callback_data=f"ans_{i}")] for i, opt in enumerate(opts)
    ])
    text = TEXTS[lang]["exam_q"].format(curr=idx + 1, total=len(questions), q=q_text)
    await msg.edit_text(text, reply_markup=kb)


@dp.callback_query(StudyState.taking_exam, F.data.startswith("ans_"))
async def answer_exam_cb(call: CallbackQuery, state: FSMContext):
    chosen = int(call.data.split("_")[1])
    data = await state.get_data()
    questions = data["questions"]
    idx = data["q_idx"]
    score = data["score"]

    correct_idx = questions[idx].get("correct_index", questions[idx].get("answer", -1))
    if chosen == correct_idx:
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