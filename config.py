from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Клас для завантаження налаштувань з .env файлу.
    """
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    model_config = SettingsConfigDict(env_file=".env")

# Створюємо єдиний екземпляр налаштувань
settings = Settings()
