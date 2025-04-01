from dataclasses import dataclass
from os import getenv
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    # Основные настройки бота
    BOT_TOKEN: str = getenv("BOT_TOKEN")
    ADMIN_ID: int = int(getenv("ADMIN_ID", 0))
    
    # Настройки API
    USE_API: bool = getenv("USE_API", "False").lower() == "true"
    API_URL: str = getenv("API_URL", "http://localhost:8000")
    
    # Режим разработки/продакшн
    DEBUG: bool = getenv("DEBUG", "True").lower() == "true"

    @classmethod
    def is_api_enabled(cls) -> bool:
        """Проверка, включено ли использование API"""
        return cls.USE_API and cls.API_URL 