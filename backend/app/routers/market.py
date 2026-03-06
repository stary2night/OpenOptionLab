"""
Market Data Router
"""
from typing import Optional, List
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, asc, func

from app.database import get_db, cache_get, cache_set
from app.config import get_settings
from app.models.market import MarketSnapshot, MarketQuote, UnusualFlow

router = APIRouter()
settings = get_settings()


# Pydantic models
class MarketSnapshotResponse(BaseModel):
    id: int
    symbol: str
    name: str
    nameEn: Optional[str]
    exchange: str
    category: Optional[str]
    latestPrice: float
    priceChange: Optional[float]
    priceChangePercent: Optional[float]
    daysToExpiry: Optional[int]
    impliedVol: Optional[float]
    ivChange: Optional[float]
    ivSpeed: Optional[float]
    realizedVol: Optional[float]
    premium: Optional[float]
    skew: Optional[float]
    ivPercentile: Optional[int]
    skewPercentile: Optional[int]
    isMain: bool
    isForeign: bool
    
    class Config:
        from_attributes = True


class MarketHistoryResponse(BaseModel):
    time: datetime
    latestPrice: Optional[float]
    priceChangePercent: Optional[float]
    impliedVol: Optional[float]
    realizedVol: Optional[float]
    volume: Optional[int]


class UnusualFlowResponse(BaseModel):
    id: int
    symbol: str
    optionType: str
    strike: float
    expiryDate: datetime
    volume: int
    openInterest: Optional[int]
    premium: int
    sentiment: str
    tradeTime: datetime
    
    class Config:
        from_attributes = True


class CategoryStats(BaseModel):
    category: str
    count: int
    avgIv: Optional[float]
    topGainer: Optional[str]
    topLoser: Optional[str]


# Helper function to build cache key
def build_cache_key(prefix: str, **params) -> str:
    """Build cache key from parameters"""
    key_parts = [prefix]
    for k, v in sorted(params.items()):
        if v is not None:
            key_parts.append(f"{k}:{v}")
    return ":".join(key_parts)


# Routes
@router.get("/snapshot", response_model=List[MarketSnapshotResponse])
async def get_market_snapshot(
    category: Optional[str] = Query(None, description="Filter by category (index, metal, energy, agri, black, chemical, new)"),
    exchange: Optional[str] = Query(None, description="Filter by exchange"),
    sort_by: str = Query("priceChangePercent", description="Sort field"),
    order: str = Query("desc", description="Sort order (asc or desc)"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    Get market snapshot with filtering and sorting
    
    Returns current market data for all symbols with optional filtering.
    """
    # Try cache first
    cache_key = build_cache_key(
        "market:snapshot",
        category=category,
        exchange=exchange,
        sort_by=sort_by,
        order=order,
        limit=limit,
        offset=offset
    )
    
    cached = await cache_get(cache_key)
    if cached:
        import json
        return json.loads(cached)
    
    # Build query
    query = select(MarketSnapshot)
    
    # Apply filters
    if category:
        query = query.where(MarketSnapshot.category == category)
    if exchange:
        query = query.where(MarketSnapshot.exchange == exchange)
    
    # Apply sorting
    sort_column = getattr(MarketSnapshot, sort_by, MarketSnapshot.price_change_percent)
    if order.lower() == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))
    
    # Apply pagination
    query = query.offset(offset).limit(limit)
    
    # Execute query
    result = await db.execute(query)
    snapshots = result.scalars().all()
    
    # Convert to response model
    response = [snapshot.to_dict() for snapshot in snapshots]
    
    # Cache result
    import json
    await cache_set(cache_key, json.dumps(response), settings.CACHE_TTL_MARKET_SNAPSHOT)
    
    return response


@router.get("/snapshot/{symbol}", response_model=MarketSnapshotResponse)
async def get_symbol_detail(
    symbol: str,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed info for a specific symbol"""
    # Try cache
    cache_key = f"market:symbol:{symbol}"
    cached = await cache_get(cache_key)
    if cached:
        import json
        return json.loads(cached)
    
    result = await db.execute(
        select(MarketSnapshot).where(MarketSnapshot.symbol == symbol.upper())
    )
    snapshot = result.scalar_one_or_none()
    
    if not snapshot:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
    
    response = snapshot.to_dict()
    
    # Cache result
    import json
    await cache_set(cache_key, json.dumps(response), settings.CACHE_TTL_SYMBOL_DETAIL)
    
    return response


@router.get("/{symbol}/history", response_model=List[MarketHistoryResponse])
async def get_symbol_history(
    symbol: str,
    start_date: Optional[datetime] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="End date (ISO format)"),
    interval: str = Query("1d", description="Interval: 1m, 5m, 15m, 1h, 1d"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get historical market data for a symbol
    
    Returns historical OHLCV and volatility data.
    """
    # Set default date range
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        if interval == "1m":
            start_date = end_date - timedelta(hours=24)
        elif interval in ["5m", "15m"]:
            start_date = end_date - timedelta(days=7)
        elif interval == "1h":
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=365)
    
    # Query historical data
    query = select(MarketQuote).where(
        MarketQuote.symbol == symbol.upper(),
        MarketQuote.time >= start_date,
        MarketQuote.time <= end_date
    ).order_by(asc(MarketQuote.time))
    
    result = await db.execute(query)
    quotes = result.scalars().all()
    
    return [
        {
            "time": quote.time,
            "latestPrice": float(quote.latest_price) if quote.latest_price else None,
            "priceChangePercent": float(quote.price_change_percent) if quote.price_change_percent else None,
            "impliedVol": float(quote.implied_vol) if quote.implied_vol else None,
            "realizedVol": float(quote.realized_vol) if quote.realized_vol else None,
            "volume": quote.volume
        }
        for quote in quotes
    ]


@router.get("/top/iv-rise", response_model=List[MarketSnapshotResponse])
async def get_top_iv_rise(
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """Get symbols with highest IV increase"""
    result = await db.execute(
        select(MarketSnapshot)
        .where(MarketSnapshot.iv_change != None)
        .order_by(desc(MarketSnapshot.iv_change))
        .limit(limit)
    )
    snapshots = result.scalars().all()
    return [snapshot.to_dict() for snapshot in snapshots]


@router.get("/top/iv-fall", response_model=List[MarketSnapshotResponse])
async def get_top_iv_fall(
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """Get symbols with highest IV decrease"""
    result = await db.execute(
        select(MarketSnapshot)
        .where(MarketSnapshot.iv_change != None)
        .order_by(asc(MarketSnapshot.iv_change))
        .limit(limit)
    )
    snapshots = result.scalars().all()
    return [snapshot.to_dict() for snapshot in snapshots]


@router.get("/top/premium-high", response_model=List[MarketSnapshotResponse])
async def get_top_premium_high(
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """Get symbols with highest IV-RV premium"""
    result = await db.execute(
        select(MarketSnapshot)
        .where(MarketSnapshot.premium != None)
        .order_by(desc(MarketSnapshot.premium))
        .limit(limit)
    )
    snapshots = result.scalars().all()
    return [snapshot.to_dict() for snapshot in snapshots]


@router.get("/top/premium-low", response_model=List[MarketSnapshotResponse])
async def get_top_premium_low(
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """Get symbols with lowest IV-RV premium (discount)"""
    result = await db.execute(
        select(MarketSnapshot)
        .where(MarketSnapshot.premium != None)
        .order_by(asc(MarketSnapshot.premium))
        .limit(limit)
    )
    snapshots = result.scalars().all()
    return [snapshot.to_dict() for snapshot in snapshots]


@router.get("/top/gainers", response_model=List[MarketSnapshotResponse])
async def get_top_gainers(
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """Get top gaining symbols by price change"""
    result = await db.execute(
        select(MarketSnapshot)
        .where(MarketSnapshot.price_change_percent > 0)
        .order_by(desc(MarketSnapshot.price_change_percent))
        .limit(limit)
    )
    snapshots = result.scalars().all()
    return [snapshot.to_dict() for snapshot in snapshots]


@router.get("/top/losers", response_model=List[MarketSnapshotResponse])
async def get_top_losers(
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """Get top losing symbols by price change"""
    result = await db.execute(
        select(MarketSnapshot)
        .where(MarketSnapshot.price_change_percent < 0)
        .order_by(asc(MarketSnapshot.price_change_percent))
        .limit(limit)
    )
    snapshots = result.scalars().all()
    return [snapshot.to_dict() for snapshot in snapshots]


@router.get("/unusual-flows", response_model=List[UnusualFlowResponse])
async def get_unusual_flows(
    symbol: Optional[str] = Query(None),
    option_type: Optional[str] = Query(None, description="call or put"),
    sentiment: Optional[str] = Query(None, description="bullish, bearish, or neutral"),
    min_premium: Optional[int] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get unusual options flow data"""
    query = select(UnusualFlow)
    
    if symbol:
        query = query.where(UnusualFlow.symbol == symbol.upper())
    if option_type:
        query = query.where(UnusualFlow.option_type == option_type.lower())
    if sentiment:
        query = query.where(UnusualFlow.sentiment == sentiment.lower())
    if min_premium:
        query = query.where(UnusualFlow.premium >= min_premium)
    
    query = query.order_by(desc(UnusualFlow.trade_time)).limit(limit)
    
    result = await db.execute(query)
    flows = result.scalars().all()
    
    return [flow.to_dict() for flow in flows]


@router.get("/categories", response_model=List[CategoryStats])
async def get_category_stats(db: AsyncSession = Depends(get_db)):
    """Get statistics for each category"""
    from app.data.marketData import categories
    
    stats = []
    for cat in categories:
        if cat['id'] == 'all':
            continue
        
        # Count symbols in category
        count_result = await db.execute(
            select(func.count()).where(MarketSnapshot.category == cat['id'])
        )
        count = count_result.scalar()
        
        # Get avg IV
        avg_iv_result = await db.execute(
            select(func.avg(MarketSnapshot.implied_vol))
            .where(MarketSnapshot.category == cat['id'])
        )
        avg_iv = avg_iv_result.scalar()
        
        stats.append({
            "category": cat['name'],
            "count": count,
            "avgIv": float(avg_iv) if avg_iv else None,
            "topGainer": None,
            "topLoser": None
        })
    
    return stats
