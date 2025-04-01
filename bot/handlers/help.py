from aiogram import types
from aiogram.filters import Command
from keyboards.reply import get_main_menu

async def help_command(message: types.Message):
    """Обработчик команды /help"""
    help_text = (
        "¡Soy un bot-abogado! Te ayudaré a responder preguntas sobre leyes.\n\n"
        "Cómo usar:\n"
        "- Presiona *Preguntar* y haz tu pregunta.\n"
        "- Presiona *HELP* o escribe /help para ver este mensaje.\n"
        "¡Simplemente escribe preguntas y encontraré respuestas cuando haya leyes!"
    )
    await message.reply(help_text, parse_mode="Markdown", reply_markup=get_main_menu())

def register_handlers(dp):
    """Регистрация обработчиков команды help"""
    dp.message.register(help_command, Command("help"))
    dp.message.register(help_command, lambda message: message.text == "HELP")