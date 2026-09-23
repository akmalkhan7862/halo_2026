import os
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"
    )

    PROJECT_NAME: str = "Resume Intelligence & Mock Interview Platform"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./resume_platform.db"

    # Security
    SECRET_KEY: str = "supersecret_default_key_change_in_production_32chars!"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    ALGORITHM: str = "HS256"

    # LLM Settings
    LLM_PROVIDER: str = "openai"  # openai, groq, ollama, mock
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://api.openai.com/v1"
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 2048
    LLM_TIMEOUT_SECONDS: int = 30
    LLM_MAX_RETRIES: int = 3

    # Scoring Weights (Must sum to 1.0)
    WEIGHT_SKILL_MATCH: float = 0.35
    WEIGHT_EXPERIENCE: float = 0.20
    WEIGHT_PROJECT: float = 0.20
    WEIGHT_KEYWORD: float = 0.15
    WEIGHT_SENIORITY: float = 0.10

    # Uploads
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "docx"]

    # Taxonomy
    DEFAULT_TAXONOMY_SOURCES: List[str] = ["esco", "onet", "custom"]
    FUZZY_MATCH_THRESHOLD: float = 0.80

    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    PROMPTS_DIR: str = os.path.join(BASE_DIR, "prompts")
    CONFIG_DIR: str = os.path.join(BASE_DIR, "config")


settings = Settings()
