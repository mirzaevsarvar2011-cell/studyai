import os
import json
import asyncio
import re
import html
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Актуальные стабильные и превью-модели для надежного фолбэка
MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
]

LANG_MAP = {"uz": "Uzbek", "ru": "Russian", "en": "English"}

FORMAT_INSTRUCTION = (
    "Форматируй ответ аккуратно для Telegram. "
    "Строго запрещено использовать символы #, ##, ###, --- и LaTeX-формулы со знаками $ или $$. "
    "Для формул и степеней используй обычные символы Unicode (например: x², x³, √, ×, ÷, ≤, ≥, ≠, π). "
    "Выделяй заголовки и важные термины жирным шрифтом."
)


def clean_for_telegram(text: str) -> str:
    text = html.escape(text)
    # Убираем LaTeX ($ и $$), оставляя сами формулы
    text = re.sub(r"\$\$(.*?)\$\$", r"\1", text, flags=re.DOTALL)
    text = re.sub(r"\$([^$\n]+?)\$", r"\1", text)
    # Превращаем заголовки ### в жирный текст
    text = re.sub(r"^#{1,6}\s*(.+)$", r"<b>\1</b>", text, flags=re.MULTILINE)
    # Убираем разделители --- и ***
    text = re.sub(r"^\s*[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)
    # Превращаем **жирный** и `код` в HTML-теги Telegram
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`([^`\n]+?)`", r"<code>\1</code>", text)
    # Заменяем списки * и - на аккуратные точки •
    text = re.sub(r"^\s*[\*\-]\s+", "• ", text, flags=re.MULTILINE)
    # Превращаем одиночный *курсив* в <i>курсив</i>
    text = re.sub(r"\*([^*\n]+?)\*", r"<i>\1</i>", text)
    # Убираем лишние пустые строки
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


async def _ask_gemini(contents, use_telegram_format: bool = True) -> str:
    last_err = None
    config = (
        types.GenerateContentConfig(system_instruction=FORMAT_INSTRUCTION)
        if use_telegram_format
        else None
    )

    for model_name in MODELS:
        for attempt in range(2):
            try:
                response = await client.aio.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=config,
                )
                raw_text = response.text or ""
                return clean_for_telegram(raw_text) if use_telegram_format else raw_text
            except Exception as e:
                last_err = e
                err_str = str(e)
                if "404" in err_str or "NOT_FOUND" in err_str:
                    break  # Модель не найдена — сразу идем к следующей
                if "503" in err_str or "UNAVAILABLE" in err_str or "429" in err_str:
                    await asyncio.sleep(1.5 * (attempt + 1))
                    continue  # Пробуем еще раз, потом переходим к следующей модели
                break

    raise RuntimeError(f"Все модели Gemini недоступны. Последняя ошибка: {last_err}")


async def check_homework(subject: str, lang: str, text: str = None, image_bytes: bytes = None) -> str:
    target_lang = LANG_MAP.get(lang, "Russian")
    prompt = (
        f"You are an expert tutor in {subject}. Answer strictly in {target_lang}.\n"
        "Check the student's homework/classwork, explain step-by-step, and show the final answer clearly.\n\n"
        f"Student task: {text or 'See attached image.'}"
    )
    contents = [prompt]
    if image_bytes:
        contents.append(types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"))

    try:
        return await _ask_gemini(contents, use_telegram_format=True)
    except Exception as e:
        return f"⚠️ Серверы Gemini временно перегружены, попробуйте через минуту.\n<code>{html.escape(str(e))}</code>"


async def generate_exam(subject: str, lang: str, count: int = 5) -> list[dict]:
    target_lang = LANG_MAP.get(lang, "Russian")
    prompt = (
        f"Generate {count} multiple-choice exam questions on {subject} in {target_lang}. "
        "Return ONLY valid JSON list without markdown: "
        '[{"question": "...", "options": ["A) ...", "B) ...", "C) ...", "D) ..."], "correct_index": 0, "explanation": "..."}]'
    )
    try:
        # Выключаем HTML-экранирование, чтобы не сломать JSON
        raw = await _ask_gemini([prompt], use_telegram_format=False)
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(cleaned)
    except Exception:
        return []