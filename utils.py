from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


def generate_options_keyboard(answer_options, correct_option):
    builder = InlineKeyboardBuilder()

    for option in answer_options:
        if option == correct_option:
            callback_data = "right_answer"
        else:
            callback_data = f"wrong_answer:{option}"
        builder.add(types.InlineKeyboardButton(text=option, callback_data=callback_data))

    builder.adjust(1)
    return builder.as_markup()
