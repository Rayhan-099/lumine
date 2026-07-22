import os
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Lumine AI Skin Intelligence API"
    HF_TOKEN: str = os.getenv("HF_TOKEN", "")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 1 week
    
    # CORS Origins. Accept a string (comma separated) or list.
    CORS_ORIGINS: Union[str, List[str]] = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")

    @property
    def cors_origins_list(self) -> List[str]:
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        return self.CORS_ORIGINS

    @field_validator("SECRET_KEY", mode="after")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if not v or v.strip() == "":
            raise ValueError("SECRET_KEY environment variable is missing or empty! Must be configured.")
        
        insecure_placeholders = [
            "supersecretkey_please_change_in_production",
            "changeme",
            "development_secret",
            "supersecretkey"
        ]
        if v in insecure_placeholders:
            raise ValueError("SECRET_KEY is set to a known insecure placeholder! Must be configured with a secure key in production.")
            
        if len(v) < 32:
            raise ValueError("SECRET_KEY is too short! It must be at least 32 characters long for secure JWT signing.")
            
        return v

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
