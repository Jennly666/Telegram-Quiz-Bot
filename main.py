import asyncio
from aiogram import Bot, Dispatcher
from database import create_table
from handlers import register_handlers

API_TOKEN = 'BOT_TOKEN'

async def main():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()
    await create_table()
    register_handlers(dp)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
