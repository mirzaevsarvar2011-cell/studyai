import os
import json
import asyncio
import re
import html
from dotenv import load_dotenv
from google import genai
from google.genai import types
from openai import AsyncOpenAI

load_dotenv()

# Клиент Gemini (оставляем для фото и резерва)
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Клиент DeepSeek (использует стандартный формат OpenAI)
deepseek_key = os.getenv("DEEPSEEK_API_KEY") or "missing_key"
deepseek_client = AsyncOpenAI(
    api_key=deepseek_key,
    base_url="https://api.deepseek.com",
)

GEMINI_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3-flash",
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
    text = re.sub(r"\$\$(.*?)\$\$", r"\1", text, flags=re.DOTALL)
    text = re.sub(r"\$([^$\n]+?)\$", r"\1", text)
    text = re.sub(r"^#{1,6}\s*(.+)$", r"<b>\1</b>", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`([^`\n]+?)`", r"<code>\1</code>", text)
    text = re.sub(r"^\s*[\*\-]\s+", "• ", text, flags=re.MULTILINE)
    text = re.sub(r"\*([^*\n]+?)\*", r"<i>\1</i>", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


async def _ask_deepseek(prompt: str, use_telegram_format: bool = True) -> str:
    messages = []
    if use_telegram_format:
        messages.append({"role": "system", "content": FORMAT_INSTRUCTION})
    messages.append({"role": "user", "content": prompt})

    response = await deepseek_client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
    )
    raw_text = response.choices[0].message.content or ""
    return clean_for_telegram(raw_text) if use_telegram_format else raw_text


async def _ask_gemini(contents, use_telegram_format: bool = True) -> str:
    last_err = None
    config = (
        types.GenerateContentConfig(system_instruction=FORMAT_INSTRUCTION)
        if use_telegram_format
        else None
    )

    for model_name in GEMINI_MODELS:
        for attempt in range(2):
            try:
                response = await gemini_client.aio.models.generate_content(
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
                    break
                if "503" in err_str or "UNAVAILABLE" in err_str or "429" in err_str:
                    await asyncio.sleep(1.5 * (attempt + 1))
                    continue
                break

    raise RuntimeError(f"Gemini error: {last_err}")


async def check_homework(subject: str, lang: str, text: str = None, image_bytes: bytes = None) -> str:
    target_lang = LANG_MAP.get(lang, "Russian")
    prompt = (
        f"You are an expert tutor in {subject}. Answer strictly in {target_lang}.\n"
        "Check the student's homework/classwork, explain step-by-step, and show the final answer clearly.\n\n"
        f"Student task: {text or 'See attached image.'}"
    )

    if image_bytes:
        contents = [
            prompt,
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
        ]
        try:
            return await _ask_gemini(contents, use_telegram_format=True)
        except Exception as e:
            return f"⚠️ Ошибка при обработке фото в Gemini.\n<code>{html.escape(str(e))}</code>"

    try:
        return await _ask_deepseek(prompt, use_telegram_format=True)
    except Exception as ds_err:
        print(f"[DeepSeek Error]: {ds_err}")
        try:
            return await _ask_gemini([prompt], use_telegram_format=True)
        except Exception as gm_err:
            print(f"[Gemini Error]: {gm_err}")
            return (
                "⚠️ Серверы ИИ временно недоступны, попробуйте позже.\n"
                f"<code>DeepSeek: {html.escape(str(ds_err))}</code>\n"
                f"<code>{html.escape(str(gm_err))}</code>"
            )


async def generate_exam(subject: str, lang: str, count: int = 5) -> list[dict]:
    target_lang = LANG_MAP.get(lang, "Russian")
    prompt = (
        f"Generate {count} multiple-choice exam questions on {subject} in {target_lang}. "
        "Return ONLY valid JSON list without markdown: "
        '[{"question": "...", "options": ["A) ...", "B) ...", "C) ...", "D) ..."], "correct_index": 0, "explanation": "..."}]'
    )
    try:
        raw = await _ask_deepseek(prompt, use_telegram_format=False)
    except Exception as ds_err:
        print(f"[DeepSeek Exam Error]: {ds_err}")
        try:
            raw = await _ask_gemini([prompt], use_telegram_format=False)
        except Exception as gm_err:
            print(f"[Gemini Exam Error]: {gm_err}")
            return []

    cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        return json.loads(cleaned)
    except Exception as parse_err:
        print(f"[JSON Parse Error]: {parse_err} | Raw: {raw}")
        return []