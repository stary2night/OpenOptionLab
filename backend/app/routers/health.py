"""
Health Check Router
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, func
from decimal import Decimal

from app.database import get_db, get_redis
from app.models.market import MarketSnapshot

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

@router.get("/seed")
@router.post("/seed")
async def seed_database(db: AsyncSession = Depends(get_db)):
    """
    Insert seed data for testing
    Only inserts if market_snapshots table is empty
    """
    try:
        # Check if data already exists
        result = await db.execute(select(func.count()).select_from(MarketSnapshot))
        count = result.scalar()
        
        if count > 0:
            return {
                "status": "skipped",
                "message": f"Database already has {count} market snapshots",
                "existing_records": count
            }
        
        # Insert seed data
        seed_data = [
            MarketSnapshot(
                symbol='510300', name='沪深300ETF', name_en='CSI 300 ETF',
                exchange='SSE', category='index',
                latest_price=Decimal('4.1234'),
                price_change=Decimal('0.0234'),
                price_change_percent=Decimal('0.57'),
                implied_vol=Decimal('18.5'),
                iv_change=Decimal('0.5'),
                iv_speed=Decimal('0.02'),
                realized_vol=Decimal('16.2'),
                premium=Decimal('3.2'),
                skew=Decimal('-0.15'),
                iv_percentile=65,
                skew_percentile=40,
                is_main=True, is_foreign=False
            ),
            MarketSnapshot(
                symbol='510500', name='中证500ETF', name_en='CSI 500 ETF',
                exchange='SSE', category='index',
                latest_price=Decimal('6.2345'),
                price_change=Decimal('-0.0156'),
                price_change_percent=Decimal('-0.25'),
                implied_vol=Decimal('22.3'),
                iv_change=Decimal('-0.3'),
                iv_speed=Decimal('0.01'),
                realized_vol=Decimal('20.1'),
                premium=Decimal('4.5'),
                skew=Decimal('-0.08'),
                iv_percentile=45,
                skew_percentile=55,
                is_main=True, is_foreign=False
            ),
            MarketSnapshot(
                symbol='159915', name='创业板ETF', name_en='ChiNext ETF',
                exchange='SZSE', category='index',
                latest_price=Decimal('2.3456'),
                price_change=Decimal('0.0456'),
                price_change_percent=Decimal('1.98'),
                implied_vol=Decimal('25.8'),
                iv_change=Decimal('1.2'),
                iv_speed=Decimal('0.05'),
                realized_vol=Decimal('23.5'),
                premium=Decimal('5.8'),
                skew=Decimal('-0.22'),
                iv_percentile=78,
                skew_percentile=35,
                is_main=True, is_foreign=False
            ),
            MarketSnapshot(
                symbol='588000', name='科创50ETF', name_en='STAR 50 ETF',
                exchange='SSE', category='index',
                latest_price=Decimal('1.1234'),
                price_change=Decimal('0.0123'),
                price_change_percent=Decimal('1.11'),
                implied_vol=Decimal('28.5'),
                iv_change=Decimal('0.8'),
                iv_speed=Decimal('0.03'),
                realized_vol=Decimal('26.2'),
                premium=Decimal('6.5'),
                skew=Decimal('-0.28'),
                iv_percentile=82,
                skew_percentile=30,
                is_main=True, is_foreign=False
            ),
            MarketSnapshot(
                symbol='AU', name='沪金', name_en='Shanghai Gold',
                exchange='SHFE', category='metal',
                latest_price=Decimal('480.50'),
                price_change=Decimal('2.30'),
                price_change_percent=Decimal('0.48'),
                implied_vol=Decimal('15.2'),
                iv_change=Decimal('-0.2'),
                iv_speed=Decimal('0.01'),
                realized_vol=Decimal('14.8'),
                premium=Decimal('2.1'),
                skew=Decimal('0.05'),
                iv_percentile=35,
                skew_percentile=60,
                is_main=True, is_foreign=False
            ),
            MarketSnapshot(
                symbol='SC', name='原油', name_en='Crude Oil',
                exchange='INE', category='energy',
                latest_price=Decimal('560.80'),
                price_change=Decimal('-3.20'),
                price_change_percent=Decimal('-0.57'),
                implied_vol=Decimal('32.5'),
                iv_change=Decimal('1.5'),
                iv_speed=Decimal('0.05'),
                realized_vol=Decimal('30.2'),
                premium=Decimal('8.5'),
                skew=Decimal('-0.35'),
                iv_percentile=55,
                skew_percentile=25,
                is_main=True, is_foreign=False
            ),
        ]
        
        db.add_all(seed_data)
        await db.commit()
        
        return {
            "status": "success",
            "message": "Seed data inserted successfully",
            "records_inserted": len(seed_data),
            "symbols": [s.symbol for s in seed_data]
        }
        
    except Exception as e:
        await db.rollback()
        return {
            "status": "error",
            "message": str(e)
        }
