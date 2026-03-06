"""
Database Configuration and Connection Management
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
import redis.asyncio as aioredis  # 使用 redis 替代 aioredis
from typing import AsyncGenerator, Optional

from app.config import get_settings

settings = get_settings()

# SQLAlchemy Base Model
Base = declarative_base()

# Create async engine for PostgreSQL
engine = create_async_engine(
    settings.database_url,
    echo=settings.DEBUG,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# Redis client instance
redis_client = None


async def init_redis():
    """Initialize Redis connection"""
    global redis_client
    redis_client = aioredis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )
    return redis_client


async def close_redis():
    """Close Redis connection"""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None


def get_redis():
    """Get Redis client instance"""
    if redis_client is None:
        raise RuntimeError("Redis not initialized. Call init_redis() first.")
    return redis_client


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    # Initialize Redis
    try:
        await init_redis()
    except Exception as e:
        print(f"Redis initialization failed: {e}")
        # Continue without Redis


async def close_db():
    """Close database connections"""
    await engine.dispose()
    try:
        await close_redis()
    except Exception as e:
        print(f"Redis close failed: {e}")


# Cache helper functions
async def cache_get(key: str) -> Optional[str]:
    """Get value from cache"""
    global redis_client
    if redis_client:
        return await redis_client.get(key)
    return None


async def cache_set(key: str, value: str, expire: int = 300):
    """Set value in cache with expiration (seconds)"""
    global redis_client
    if redis_client:
        await redis_client.setex(key, expire, value)


