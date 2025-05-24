import os
from dotenv import load_dotenv
from pathlib import Path
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from functools import lru_cache


load_dotenv()


class Settings(BaseSettings):
    """
    Класс настроек.
    """
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding='utf-8')
    DB_USER: str = Field(default="admin")
    DB_PASSWORD: str = os.getenv('DB_PASSWORD', 'postgres')
    DB_NAME: str = Field(default="postgres")
    DB_HOST: str = Field(default="postgres")
    DB_PORT: int = Field(default=5432)
    FOLDER_LOG: Path = Field(default="logs/")
    POSTGRES_ECHO: bool = Field(default=False)
    WEATHER_API_URL: str = Field(default="https://api.open-meteo.com/v1/forecast")
    GEOCODE_URL: str = Field(default="https://nominatim.openstreetmap.org/search")
    DB_URI: str | None = Field(default=None)

    @classmethod
    def get_path(cls, path: Path) -> Path:
        file_path = Path(__file__).parent / path
        file_path.mkdir(exist_ok=True, parents=True)
        abs_path = file_path.absolute()
        return abs_path

    @model_validator(mode='after')
    def change_path(self):
        """
        Метод класса для корректировки путей.
        :return:
        """
        self.DB_URI = f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        self.FOLDER_LOG = self.get_path(self.FOLDER_LOG)

        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings: Settings = get_settings()