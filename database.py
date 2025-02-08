import aiosqlite

DB_NAME = "quiz_bot.db"

async def create_table():
    async with aiosqlite.connect(DB_NAME) as db:
        # Создаем таблицу с дополнительным полем correct_answers
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS quiz_state (
                user_id INTEGER PRIMARY KEY,
                question_index INTEGER,
                correct_answers INTEGER DEFAULT 0
            )
            """
        )
        await db.commit()

async def get_quiz_index(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            'SELECT question_index FROM quiz_state WHERE user_id = ?', 
            (user_id,)
        ) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0

async def update_quiz_index(user_id, index):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT OR REPLACE INTO quiz_state (user_id, question_index, correct_answers)
            VALUES (?, ?, (SELECT correct_answers FROM quiz_state WHERE user_id = ?))
        ''', (user_id, index, user_id))
        await db.commit()

async def get_correct_answers(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            'SELECT correct_answers FROM quiz_state WHERE user_id = ?', 
            (user_id,)
        ) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0

async def increment_correct_answers(user_id, reset=False):
    async with aiosqlite.connect(DB_NAME) as db:
        if reset:
            # Сбросить счетчик правильных ответов
            await db.execute(
                "UPDATE quiz_state SET correct_answers = 0 WHERE user_id = ?",
                (user_id,),
            )
        else:
            # Увеличить счетчик правильных ответов
            await db.execute(
                "UPDATE quiz_state SET correct_answers = correct_answers + 1 WHERE user_id = ?",
                (user_id,),
            )
        await db.commit()

async def save_quiz_result(user_id, correct_answers):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            INSERT OR REPLACE INTO quiz_state (user_id, question_index, correct_answers)
            VALUES (?, 0, ?)
            """,
            (user_id, correct_answers),
        )
        await db.commit()

async def get_all_results():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            "SELECT user_id, correct_answers FROM quiz_state ORDER BY correct_answers DESC"
        ) as cursor:
            results = await cursor.fetchall()
            return results