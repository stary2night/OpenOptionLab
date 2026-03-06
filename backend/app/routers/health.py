"""
Health Check Router
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.database import get_db, get_redis

router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "OpenOptions Lab API",
        "version": "1.0.0"
    }


@router.get("/db")
async def db_health_check(db: AsyncSession = Depends(get_db)):
    """Database health check"""
    try:
        result = await db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "type": "PostgreSQL"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


@router.get("/cache")
async def cache_health_check():
    """Redis cache health check"""
    try:
        redis = get_redis()
        await redis.ping()
        info = await redis.info()
        return {
            "status": "healthy",
            "cache": "connected",
            "type": "Redis",
            "version": info.get("redis_version", "unknown")
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "cache": "disconnected",
            "error": str(e)
        }


@router.get("/full")
async def full_health_check(db: AsyncSession = Depends(get_db)):
    """Full system health check"""
    results = {
        "service": "OpenOptions Lab API",
        "version": "1.0.0",
        "checks": {}
    }
    
    # Check database
    try:
        await db.execute(text("SELECT 1"))
        results["checks"]["database"] = {"status": "healthy"}
    except Exception as e:
        results["checks"]["database"] = {"status": "unhealthy", "error": str(e)}
    
    # Check cache
    try:
        redis = get_redis()
        await redis.ping()
        results["checks"]["cache"] = {"status": "healthy"}
    except Exception as e:
        results["checks"]["cache"] = {"status": "unhealthy", "error": str(e)}
    
    # Overall status
    all_healthy = all(check.get("status") == "healthy" for check in results["checks"].values())
    results["status"] = "healthy" if all_healthy else "degraded"
    
    return results
