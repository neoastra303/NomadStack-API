from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "NomadStack API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/nomadstack"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # External APIs
    WEATHER_API_KEY: str = ""
    EXCHANGE_RATE_API_KEY: str = ""
    OPEN_TRIP_MAP_KEY: str = ""

    # Security
    SECRET_KEY: str = "supersecretkey"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
