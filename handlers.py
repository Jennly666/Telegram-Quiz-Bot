from aiogram import types, Dispatcher, F
from aiogram.filters import Command
from database import (
    get_quiz_index,
    update_quiz_index,
    get_correct_answers,
    increment_correct_answers,
    save_quiz_result,
    get_all_results,
)
from quiz_data import quiz_data
from utils import generate_options_keyboard
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

async def start_command(message: types.Message):
    # Создаем кнопки
    button_quiz = KeyboardButton(text="Начать игру")
    button_stats = KeyboardButton(text="Статистика игроков")

    # Создаем клавиатуру
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [button_quiz],  # Кнопка в первой строке
            [button_stats],  # Кнопка во второй строке
        ],
        resize_keyboard=True  # Клавиатура адаптируется под экран
    )

    await message.answer(
        "Привет! Добро пожаловать в квиз-бот! Выберите действие:", 
        reply_markup=keyboard
    )


async def start_quiz(message: types.Message):
    user_id = message.from_user.id
    await update_quiz_index(user_id, 0)  # Сбрасываем индекс вопросов
    await increment_correct_answers(user_id, reset=True)  # Сбрасываем счетчик правильных ответов
    await send_question(message, user_id)


async def send_question(message, user_id):
    question_index = await get_quiz_index(user_id)
    if question_index < len(quiz_data):
        question = quiz_data[question_index]
        keyboard = generate_options_keyboard(
            question["options"], question["options"][question["correct_option"]]
        )
        await message.answer(
            f"Вопрос {question_index + 1}/{len(quiz_data)}:\n{question['question']}",
            reply_markup=keyboard,
        )
    else:
        await send_final_results(message, user_id)


async def right_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    question_index = await get_quiz_index(user_id)
    question = quiz_data[question_index]

    # Увеличиваем счетчик правильных ответов
    await increment_correct_answers(user_id)

    # Удаляем клавиатуру
    await callback.message.edit_reply_markup()

    # Отправляем сообщение с ответом
    await callback.message.answer(
        f"Вы выбрали: {question['options'][question['correct_option']]}\n✅ Правильно!"
    )

    # Переходим к следующему вопросу
    await next_question(callback)


async def wrong_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    question_index = await get_quiz_index(user_id)
    question = quiz_data[question_index]

    # Удаляем клавиатуру
    await callback.message.edit_reply_markup()

    # Определяем текст неправильного ответа
    selected_option = callback.data.split(":")[1]
    correct_option = question["options"][question["correct_option"]]

    # Отправляем сообщение с ответом
    await callback.message.answer(
        f"Вы выбрали: {selected_option}\n❌ Неправильно.\nПравильный ответ: {correct_option}"
    )

    # Переходим к следующему вопросу
    await next_question(callback)


async def next_question(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    question_index = await get_quiz_index(user_id)
    await update_quiz_index(user_id, question_index + 1)

    # Отправляем следующий вопрос
    await send_question(callback.message, user_id)


async def send_final_results(message: types.Message, user_id):
    correct_answers = await get_correct_answers(user_id)
    total_questions = len(quiz_data)

    # Проверяем, чтобы правильных ответов не было больше, чем вопросов
    correct_answers = min(correct_answers, total_questions)

    # Сохраняем результат в базе данных
    await save_quiz_result(user_id, correct_answers)

    await message.answer(
        f"🎉 Квиз завершен! Вы ответили правильно на {correct_answers} из {total_questions} вопросов."
    )


async def all_stats_handler(message: types.Message):
    results = await get_all_results()  # Получаем список всех результатов
    if not results:
        await message.answer("📊 Еще никто не прошел квиз. Будьте первым!")
    else:
        leaderboard = "📊 Последние результаты игроков:\n\n"
        for idx, (user_id, correct_answers) in enumerate(results, start=1):
            leaderboard += f"{idx}. Игрок {user_id}: {correct_answers} правильных ответов\n"
        await message.answer(leaderboard)



def register_handlers(dp: Dispatcher):
    dp.message.register(start_command, Command("start"))
    dp.message.register(start_quiz, F.text == "Начать игру")
    dp.message.register(all_stats_handler, F.text == "Статистика игроков")
    dp.callback_query.register(right_answer, F.data == "right_answer")
    dp.callback_query.register(wrong_answer, F.data.startswith("wrong_answer"))
