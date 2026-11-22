import aiosqlite

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
