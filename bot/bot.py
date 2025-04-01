import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import Config
from handlers import start, help, query
from aiogram.utils.chat_action import ChatActionMiddleware

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=Config.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

async def on_startup(bot: Bot):
    """Действия при запуске бота"""
    if Config.ADMIN_ID:
        await bot.send_message(Config.ADMIN_ID, "¡Bot iniciado!")
    logger.info("=== Bot iniciado ===")
    logger.info(f"Nombre del bot: @{(await bot.get_me()).username}")

async def on_shutdown(bot: Bot):
    """Действия при остановке бота"""
    if Config.ADMIN_ID:
        await bot.send_message(Config.ADMIN_ID, "Bot detenido!")
    logger.info("=== Bot detenido ===")

async def main():
    # Подключение middleware
    dp.message.middleware(ChatActionMiddleware())
    
    # Регистрация обработчиков
    start.register_handlers(dp)
    help.register_handlers(dp)
    query.register_handlers(dp)
    
    # Регистрация действий при запуске и остановке
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Запуск бота
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())