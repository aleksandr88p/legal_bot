from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu() -> ReplyKeyboardMarkup:
    """Основное меню бота"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Preguntar"), KeyboardButton(text="HELP")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard 