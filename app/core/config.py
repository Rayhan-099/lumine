import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Lumine AI Skin Intelligence API"
    HF_TOKEN: str = os.getenv("HF_TOKEN", "")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey_please_change_in_production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 1 week
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./lumine.db"

    class Config:
        env_file = ".env"

settings = Settings()
