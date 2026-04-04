from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: Optional[str] = None
    SECRET_KEY: str = "test_secret_key"
    BACKEND_URL: str = "http://localhost:8000"

    class Config:
        env_file = ".env"


settings = Settings()
