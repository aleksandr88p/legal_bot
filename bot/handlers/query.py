from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from states import QueryState
from config import Config
from keyboards.reply import get_main_menu

async def handle_query_command(message: types.Message, state: FSMContext):
    """
    Обработчик команды запроса.
    Запрашивает у пользователя вопрос о законе.
    """
    await message.reply(
        "Por favor, escribe tu pregunta sobre la ley:",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(QueryState.waiting_for_query)

async def handle_query_text(message: types.Message, state: FSMContext):
    """
    Обработчик текста запроса.
    Сейчас работает как эхо-бот, в будущем здесь будет интеграция с API.
    
    TODO: 
    1. Добавить обращение к API для получения ответа на вопрос
    2. Обработать возможные ошибки API
    3. Форматировать ответ от API для пользователя
    """
    user_question = message.text
    
    if Config.is_api_enabled():
        # TODO: В будущем здесь будет интеграция с API
        response = "Esta función estará disponible pronto cuando se integre la API"
    else:
        response = (
            "Tu pregunta ha sido recibida:\n\n"
            f"❓ {user_question}\n\n"
            "🤖 En el futuro, proporcionaré respuestas basadas en la legislación española."
        )
    
    await message.reply(response, reply_markup=get_main_menu())
    await state.clear()

def register_handlers(dp):
    """Регистрация обработчиков запросов"""
    dp.message.register(handle_query_command, Command("query"))
    dp.message.register(handle_query_command, lambda message: message.text == "Preguntar")
    dp.message.register(handle_query_text, QueryState.waiting_for_query) 