import os
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.types import BotCommand
from aiogram.types import FSInputFile

from __init__ import bot, dp, logger
from parser import get_evaluations_screenshot

@dp.message(CommandStart)
async def cmd_start(message: Message):
    await message.answer("Я бот на aiogram 3.20")

@dp.message(Command("get_evaluations"))
async def cmd_get_evaluations(message: Message):
    await message.answer("Вот ваши оценки:")

async def main():
    await bot.set_my_commands([
        BotCommand(command="/start", description="Запуск бота"),
        BotCommand(command="/get_evaluations", description="Получение оценок"),
    ])
    logger.info("🚩 Starting bot")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        import asyncio
        asyncio.run(main())
    except KeyboardInterrupt: 
        logger.info("🏁 Stopped bot")
        
