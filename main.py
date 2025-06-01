import os
import asyncio

from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.types import BotCommand
from aiogram.types import FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove

from __init__ import bot, dp, logger
from parser import get_evaluations_screenshot


class AuthStates(StatesGroup):
    waiting_for_login = State()
    waiting_for_password = State()


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Привет! Я бот для получения оценок из e-learning.bmstu.ru. "
                         "Чтобы получить оценки, используй команду /get_evaluations")


@dp.message(Command("get_evaluations"))
async def cmd_get_evaluations(message: Message, state: FSMContext):
    await message.answer(
        "🔐 Для получения оценок введите ваш логин от e-learning.bmstu.ru:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AuthStates.waiting_for_login)


@dp.message(AuthStates.waiting_for_login)
async def process_login(message: Message, state: FSMContext):
    login = message.text.strip()
    await state.update_data(login=login)

    await message.answer(
        "🔑 Теперь введите ваш пароль:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AuthStates.waiting_for_password)


@dp.message(AuthStates.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    password = message.text.strip()
    user_data = await state.get_data()
    login = user_data.get("login")

    await state.clear()

    wait_msg = await message.answer("⌛ Получаю оценки...")

    try:
        screenshot_path = await asyncio.to_thread(
            get_evaluations_screenshot, login, password
        )

        await bot.delete_message(chat_id=message.chat.id, message_id=wait_msg.message_id)

        if screenshot_path:
            photo = FSInputFile(screenshot_path)
            await message.answer_photo(
                photo=photo,
                caption="📊 Вот ваши оценки:\n\nP.S. Ну ебать ты плохо учишь 🤡"
            )
            os.remove(screenshot_path)
        else:
            await message.answer("❌ Не удалось получить оценки. Проверьте правильность логина и пароля.")

    except Exception as e:
        logger.error(f"Ошибка при обработке запроса: {str(e)}")
        await message.answer("⚠️ Произошла ошибка при получении оценок. Попробуйте позже.")


async def main():
    await bot.set_my_commands([
        BotCommand(command="/start", description="Запуск бота"),
        BotCommand(command="/get_evaluations", description="Получение оценок"),
    ])
    logger.info("🚩 Starting bot")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🏁 Stopped bot")
