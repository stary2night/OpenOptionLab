"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "OpenOptions Lab API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server (Railway provides PORT)
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database - Railway provides DATABASE_URL
    DATABASE_URL: Optional[str] = None
    
    # Database - PostgreSQL (fallback for local dev)
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "openoptions"
    POSTGRES_PASSWORD: str = "openoptions123"
    POSTGRES_DB: str = "openoptions"
    
    # Database - TimescaleDB
    TIMESCALE_HOST: str = "localhost"
    TIMESCALE_PORT: int = 5432
    TIMESCALE_USER: str = "openoptions"
    TIMESCALE_PASSWORD: str = "openoptions123"
    TIMESCALE_DB: str = "openoptions"
    
    # Redis - Railway provides REDIS_URL
    REDIS_URL: Optional[str] = None
    
    # Redis (fallback for local dev)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # Celery
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # CORS - Allow Railway frontend and all origins for development
    CORS_ORIGINS: list = ["*"]
    
    # Data Sources
    TUSHARE_TOKEN: Optional[str] = None
    AKSHARE_ENABLE: bool = True
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Cache TTL (seconds)
    CACHE_TTL_MARKET_SNAPSHOT: int = 5
    CACHE_TTL_SYMBOL_DETAIL: int = 10
    CACHE_TTL_USER_DATA: int = 300
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    @property
    def database_url(self) -> str:
        """Async PostgreSQL connection string"""
        # Use Railway's DATABASE_URL if available
        if self.DATABASE_URL:
            # Convert postgresql:// to postgresql+asyncpg://
            url = self.DATABASE_URL
            if url.startswith("postgresql://") and "asyncpg" not in url:
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return url
        
        # Fallback to individual settings
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    @property
    def database_url_sync(self) -> str:
        """Sync PostgreSQL connection string for Alembic"""
        if self.DATABASE_URL:
            # Remove asyncpg if present
            url = self.DATABASE_URL
            if "postgresql+asyncpg://" in url:
                url = url.replace("postgresql+asyncpg://", "postgresql://", 1)
            return url
        
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    @property
    def timescale_url(self) -> str:
        """TimescaleDB connection string (same as PostgreSQL on Railway)"""
        return self.database_url
    
    @property
    def redis_url(self) -> str:
        """Redis connection string"""
        if self.REDIS_URL:
            return self.REDIS_URL
        
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    @property
    def celery_broker_url(self) -> str:
        """Celery broker URL"""
        if self.CELERY_BROKER_URL:
            return self.CELERY_BROKER_URL
        return self.redis_url
    
    @property
    def celery_result_backend(self) -> str:
        """Celery result backend URL"""
        if self.CELERY_RESULT_BACKEND:
            return self.CELERY_RESULT_BACKEND
        return self.redis_url


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
