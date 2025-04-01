from aiogram.fsm.state import State, StatesGroup

class QueryState(StatesGroup):
    """Состояния для обработки запросов пользователя"""
    waiting_for_query = State()
    processing_query = State()

class TextState(StatesGroup):
    """Состояния для обработки текстовых сообщений"""
    waiting_for_text = State()
    processing_text = State() 