import asyncio
import logging
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import os
from handlers import start, help

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Регистрируем обработчики
start.register_handlers(dp)
help.register_handlers(dp)

async def main():
    logger.info("=== Legal Bot запущен ===")
    logger.info(f"Имя бота: @{(await bot.get_me()).username}")
    logger.info("Обработчики команд зарегистрированы")
    logger.info("Бот готов к работе!")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
    finally:
        logger.info("=== Legal Bot остановлен ===")

if __name__ == "__main__":
    asyncio.run(main())