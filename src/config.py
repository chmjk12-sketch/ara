"""
ARA - Adaptive Reality Agent Configuration
"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "ara"
    APP_PORT: int = 80
    DEBUG: bool = False

    # DeepSeek
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # Control Plane
    CP_API_KEY: str = ""
    CP_BASE_URL: str = "https://administrator.chmjk67.top"
    AGENT_SLUG: str = "ara"
    AGENT_ID: str = ""

    # CORS
    CORS_ORIGINS: str = "*"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
