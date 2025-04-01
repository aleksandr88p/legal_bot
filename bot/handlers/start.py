from aiogram import types
from aiogram.filters import Command
from keyboards.reply import get_main_menu

async def start_command(message: types.Message):
    """Обработчик команды /start"""
    welcome_text = (
        "¡Hola! Soy un bot legal especializado en leyes españolas. "
        "Estoy aquí para ayudarte con tus preguntas sobre la legislación.\n\n"
        "Usa el botón *Preguntar* para hacer tu consulta."
    )
    await message.reply(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=get_main_menu()
    )

def register_handlers(dp):
    """Регистрация обработчиков команды start"""
    dp.message.register(start_command, Command("start"))