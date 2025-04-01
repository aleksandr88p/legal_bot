from aiogram import types
from aiogram.filters import Command
from keyboards.main_menu import get_main_menu

async def start_command(message: types.Message):
    await message.reply(
        "Hola! Soy legal bot. Pregunta me algo sobre el lei",
        reply_markup=get_main_menu()
    )

async def ask_button(message: types.Message):
    await message.reply("Pregunta me algo sobre el lei")

def register_handlers(dp):
    dp.message.register(start_command, Command("start"))
    dp.message.register(ask_button, lambda message: message.text == "Preguntar")