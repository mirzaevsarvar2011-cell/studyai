import os
import json
from io import BytesIO
from PIL import Image
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-3.8-flash"

LANG_MAP = {"uz": "Uzbek", "ru": "Russian", "en": "English"}

async def check_homework(subject: str, lang: str, text: str = "", image_bytes: bytes = None) -> str:
    target_lang = LANG_MAP.get(lang, "Russian")
    prompt = f"""You are an expert tutor in {subject}. Respond strictly in {target_lang}.
The student sent homework or classwork.
1. Explain the topic/problem clearly step-by-step.
2. If the student included their own attempt/answer, check it and point out any mistakes.
3. Show the clear final answer at the end.
Keep formatting clean using plain text and bullet points (avoid complex markdown tables).
Student input: {text}"""

    contents = [prompt]
    if image_bytes:
        img = Image.open(BytesIO(image_bytes))
        contents.append(img)

    response = await client.aio.models.generate_content(model=MODEL, contents=contents)
    return response.text

async def generate_exam(subject: str, lang: str, count: int) -> list[dict]:
    target_lang = LANG_MAP.get(lang, "Russian")
    prompt = f"""Create a {count}-question multiple-choice exam on {subject} in {target_lang}.
Return ONLY a valid JSON array of objects, with no extra text or code fences.
Format:
[
  {{"q": "Question text", "options": ["A) ...", "B) ...", "C) ...", "D) ..."], "answer": 0}}
]
Where "answer" is the 0-based index (0, 1, 2, or 3) of the correct option."""

    response = await client.aio.models.generate_content(model=MODEL, contents=prompt)
    raw = response.text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(raw)
