from functools import lru_cache
import os
from pydantic_settings import BaseSettings, SettingsConfigDict


@lru_cache
def get_env_filename():
    runtime_env = os.getenv("ENV")
    return f".env.{runtime_env}" if runtime_env else ".env"


class EnvironmentSettings(BaseSettings):
    # Application settings
    API_VERSION: str
    APP_NAME: str
    APP_DESC: str
    APP_PORT: int
    # Vertex AI settings
    MODEL_NAME: str = "gemini-2.5-pro"
    GOOGLE_CLOUD_PROJECT: str
    GOOGLE_CLOUD_LOCATION: str = "us-east1"
    GOOGLE_APPLICATION_CREDENTIALS: str = "service-account.json"
    # Database settings - PostgreSQL
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    # Cache settings - Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    TTL_SECONDS: int = 3600
    # Debug settings
    MAX_TURNS: int = 20
    LIMIT_MINUTES: int = 10
    MAX_MSG: int = 12
    DEBUG_MODE: bool = False
    COUNTER_TTL_HOURS: int = 1
    APP_RELOAD: bool = False

    model_config = SettingsConfigDict(env_file=get_env_filename(), env_file_encoding="utf-8")


@lru_cache
def get_environment_variables():
    return EnvironmentSettings()

env = get_environment_variables()