from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./dev.db")
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    AI_REVIEW_ENABLED: bool = os.getenv("AI_REVIEW_ENABLED", "true").lower() == "true"

settings = Settings()