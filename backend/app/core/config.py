import os
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_PATH = os.path.join(BASE_DIR, ".env")

class Settings(BaseSettings):
    PROJECT_NAME: str = "Caterpillar Smart Rental Tracking System"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = "caterpillar_smart_rental_secret_key_2026"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file=ENV_PATH if os.path.exists(ENV_PATH) else ".env", 
        env_file_encoding="utf-8", 
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
