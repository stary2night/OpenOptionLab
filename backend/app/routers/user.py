"""
User Router
"""
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_

from app.database import get_db
from app.models.user import User, UserFavorite, UserStrategy, UserNotification
from app.models.market import MarketSnapshot
from app.routers.auth import get_current_active_user

router = APIRouter()


# ============== Pydantic Models ==============

class FavoriteCreate(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=20)
    category: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=500)
    alert_enabled: bool = False
    alert_settings: Optional[dict] = None


class FavoriteUpdate(BaseModel):
    notes: Optional[str] = Field(None, max_length=500)
    alert_enabled: Optional[bool] = None
    alert_settings: Optional[dict] = None


class FavoriteResponse(BaseModel):
    id: int
    symbol: str
    category: Optional[str]
    notes: Optional[str]
    alert_enabled: bool
    alert_settings: Optional[dict]
    market_data: Optional[dict] = None  # Joined market snapshot
    created_at: datetime
    
    class Config:
        from_attributes = True


class StrategyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    strategy_type: str = Field(..., min_length=1, max_length=50)
    tags: Optional[list[str]] = None
    strategy_data: dict
    underlying_symbol: Optional[str] = None
    underlying_price: Optional[str] = None
    max_profit: Optional[str] = None
    max_loss: Optional[str] = None
    breakeven_points: Optional[list[float]] = None
    probability_of_profit: Optional[str] = None
    initial_capital: Optional[str] = None
    is_public: bool = False


class StrategyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    tags: Optional[list[str]] = None
    is_public: Optional[bool] = None
    is_active: Optional[bool] = None


class StrategyResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    strategy_type: str
    tags: Optional[list[str]]
    underlying_symbol: Optional[str]
    underlying_price: Optional[str]
    max_profit: Optional[str]
    max_loss: Optional[str]
    breakeven_points: Optional[list[float]]
    probability_of_profit: Optional[str]
    initial_capital: Optional[str]
    current_pnl: Optional[str]
    pnl_percent: Optional[str]
    is_public: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class StrategyDetailResponse(StrategyResponse):
    strategy_data: dict


class NotificationResponse(BaseModel):
    id: int
    type: str
    title: str
    message: str
    data: Optional[dict]
    is_read: bool
    read_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class MarkNotificationsRead(BaseModel):
    notification_ids: List[int]


# ============== Favorites Routes ==============

@router.get("/favorites", response_model=List[FavoriteResponse])
async def get_favorites(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    include_market_data: bool = Query(True, description="Include current market data")
):
    """Get user's favorite symbols with optional market data"""
    result = await db.execute(
        select(UserFavorite)
        .where(UserFavorite.user_id == current_user.id)
        .order_by(desc(UserFavorite.created_at))
    )
    favorites = result.scalars().all()
    
    if not include_market_data:
        return favorites
    
    # Fetch market data for all favorites
    symbols = [f.symbol for f in favorites]
    market_data = {}
    
    if symbols:
        result = await db.execute(
            select(MarketSnapshot).where(MarketSnapshot.symbol.in_(symbols))
        )
        for snapshot in result.scalars().all():
            market_data[snapshot.symbol] = snapshot.to_dict()
    
    # Combine favorites with market data
    response = []
    for favorite in favorites:
        fav_dict = {
            'id': favorite.id,
            'symbol': favorite.symbol,
            'category': favorite.category,
            'notes': favorite.notes,
            'alert_enabled': favorite.alert_enabled,
            'alert_settings': favorite.alert_settings,
            'market_data': market_data.get(favorite.symbol),
            'created_at': favorite.created_at,
        }
        response.append(fav_dict)
    
    return response


@router.post("/favorites", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
async def add_favorite(
    favorite: FavoriteCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a symbol to favorites"""
    symbol = favorite.symbol.upper()
    
    # Check if already exists
    result = await db.execute(
        select(UserFavorite)
        .where(UserFavorite.user_id == current_user.id)
        .where(UserFavorite.symbol == symbol)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{symbol} is already in your favorites"
        )
    
    # Verify symbol exists in market
    result = await db.execute(
        select(MarketSnapshot).where(MarketSnapshot.symbol == symbol)
    )
    market_data = result.scalar_one_or_none()
    
    # Create favorite
    new_favorite = UserFavorite(
        user_id=current_user.id,
        symbol=symbol,
        category=favorite.category or (market_data.category if market_data else None),
        notes=favorite.notes,
        alert_enabled=favorite.alert_enabled,
        alert_settings=favorite.alert_settings
    )
    
    db.add(new_favorite)
    await db.commit()
    await db.refresh(new_favorite)
    
    # Build response with market data
    response = {
        'id': new_favorite.id,
        'symbol': new_favorite.symbol,
        'category': new_favorite.category,
        'notes': new_favorite.notes,
        'alert_enabled': new_favorite.alert_enabled,
        'alert_settings': new_favorite.alert_settings,
        'market_data': market_data.to_dict() if market_data else None,
        'created_at': new_favorite.created_at,
    }
    
    return response


@router.put("/favorites/{favorite_id}", response_model=FavoriteResponse)
async def update_favorite(
    favorite_id: int,
    favorite_update: FavoriteUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a favorite's notes and alert settings"""
    result = await db.execute(
        select(UserFavorite)
        .where(UserFavorite.id == favorite_id)
        .where(UserFavorite.user_id == current_user.id)
    )
    favorite = result.scalar_one_or_none()
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found"
        )
    
    # Update fields
    if favorite_update.notes is not None:
        favorite.notes = favorite_update.notes
    if favorite_update.alert_enabled is not None:
        favorite.alert_enabled = favorite_update.alert_enabled
    if favorite_update.alert_settings is not None:
        favorite.alert_settings = favorite_update.alert_settings
    
    await db.commit()
    await db.refresh(favorite)
    
    # Get market data
    result = await db.execute(
        select(MarketSnapshot).where(MarketSnapshot.symbol == favorite.symbol)
    )
    market_data = result.scalar_one_or_none()
    
    return {
        'id': favorite.id,
        'symbol': favorite.symbol,
        'category': favorite.category,
        'notes': favorite.notes,
        'alert_enabled': favorite.alert_enabled,
        'alert_settings': favorite.alert_settings,
        'market_data': market_data.to_dict() if market_data else None,
        'created_at': favorite.created_at,
    }


@router.delete("/favorites/{favorite_id}")
async def remove_favorite(
    favorite_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove a symbol from favorites by ID"""
    result = await db.execute(
        select(UserFavorite)
        .where(UserFavorite.id == favorite_id)
        .where(UserFavorite.user_id == current_user.id)
    )
    favorite = result.scalar_one_or_none()
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found"
        )
    
    await db.delete(favorite)
    await db.commit()
    
    return {"message": f"{favorite.symbol} removed from favorites"}


@router.delete("/favorites/by-symbol/{symbol}")
async def remove_favorite_by_symbol(
    symbol: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove a symbol from favorites by symbol name"""
    result = await db.execute(
        select(UserFavorite)
        .where(UserFavorite.user_id == current_user.id)
        .where(UserFavorite.symbol == symbol.upper())
    )
    favorite = result.scalar_one_or_none()
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{symbol} not found in your favorites"
        )
    
    await db.delete(favorite)
    await db.commit()
    
    return {"message": f"{symbol} removed from favorites"}


# ============== Strategy Routes ==============

@router.get("/strategies", response_model=List[StrategyResponse])
async def get_strategies(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    include_inactive: bool = Query(False, description="Include inactive strategies"),
    strategy_type: Optional[str] = Query(None, description="Filter by strategy type")
):
    """Get user's saved strategies"""
    query = select(UserStrategy).where(UserStrategy.user_id == current_user.id)
    
    if not include_inactive:
        query = query.where(UserStrategy.is_active == True)
    
    if strategy_type:
        query = query.where(UserStrategy.strategy_type == strategy_type)
    
    query = query.order_by(desc(UserStrategy.updated_at))
    
    result = await db.execute(query)
    strategies = result.scalars().all()
    return strategies


@router.post("/strategies", response_model=StrategyDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_strategy(
    strategy: StrategyCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new strategy"""
    new_strategy = UserStrategy(
        user_id=current_user.id,
        name=strategy.name,
        description=strategy.description,
        strategy_type=strategy.strategy_type,
        tags=strategy.tags,
        strategy_data=strategy.strategy_data,
        underlying_symbol=strategy.underlying_symbol,
        underlying_price=strategy.underlying_price,
        max_profit=strategy.max_profit,
        max_loss=strategy.max_loss,
        breakeven_points=strategy.breakeven_points,
        probability_of_profit=strategy.probability_of_profit,
        initial_capital=strategy.initial_capital,
        is_public=strategy.is_public
    )
    
    db.add(new_strategy)
    await db.commit()
    await db.refresh(new_strategy)
    
    # Return with strategy_data
    return {
        **new_strategy.to_dict(include_private=True),
        'strategy_data': new_strategy.strategy_data
    }


@router.get("/strategies/{strategy_id}", response_model=StrategyDetailResponse)
async def get_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific strategy with full details"""
    result = await db.execute(
        select(UserStrategy)
        .where(UserStrategy.id == strategy_id)
        .where(UserStrategy.user_id == current_user.id)
    )
    strategy = result.scalar_one_or_none()
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found"
        )
    
    return {
        **strategy.to_dict(include_private=True),
        'strategy_data': strategy.strategy_data
    }


@router.put("/strategies/{strategy_id}", response_model=StrategyDetailResponse)
async def update_strategy(
    strategy_id: int,
    strategy_update: StrategyUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a strategy"""
    result = await db.execute(
        select(UserStrategy)
        .where(UserStrategy.id == strategy_id)
        .where(UserStrategy.user_id == current_user.id)
    )
    strategy = result.scalar_one_or_none()
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found"
        )
    
    # Update fields
    if strategy_update.name is not None:
        strategy.name = strategy_update.name
    if strategy_update.description is not None:
        strategy.description = strategy_update.description
    if strategy_update.tags is not None:
        strategy.tags = strategy_update.tags
    if strategy_update.is_public is not None:
        strategy.is_public = strategy_update.is_public
    if strategy_update.is_active is not None:
        strategy.is_active = strategy_update.is_active
        if not strategy_update.is_active:
            strategy.closed_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(strategy)
    
    return {
        **strategy.to_dict(include_private=True),
        'strategy_data': strategy.strategy_data
    }


@router.delete("/strategies/{strategy_id}")
async def delete_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a strategy permanently"""
    result = await db.execute(
        select(UserStrategy)
        .where(UserStrategy.id == strategy_id)
        .where(UserStrategy.user_id == current_user.id)
    )
    strategy = result.scalar_one_or_none()
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found"
        )
    
    await db.delete(strategy)
    await db.commit()
    
    return {"message": "Strategy deleted successfully"}


@router.post("/strategies/{strategy_id}/close")
async def close_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Close a strategy (mark as inactive)"""
    result = await db.execute(
        select(UserStrategy)
        .where(UserStrategy.id == strategy_id)
        .where(UserStrategy.user_id == current_user.id)
    )
    strategy = result.scalar_one_or_none()
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found"
        )
    
    strategy.is_active = False
    strategy.closed_at = datetime.utcnow()
    await db.commit()
    
    return {"message": "Strategy closed successfully"}


@router.get("/strategies/public", response_model=List[StrategyResponse])
async def get_public_strategies(
    limit: int = Query(20, ge=1, le=100),
    strategy_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get public strategies from all users"""
    query = select(UserStrategy).where(UserStrategy.is_public == True)
    
    if strategy_type:
        query = query.where(UserStrategy.strategy_type == strategy_type)
    
    query = query.order_by(desc(UserStrategy.created_at)).limit(limit)
    
    result = await db.execute(query)
    strategies = result.scalars().all()
    return strategies


# ============== Notification Routes ==============

@router.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=100)
):
    """Get user notifications"""
    query = select(UserNotification).where(UserNotification.user_id == current_user.id)
    
    if unread_only:
        query = query.where(UserNotification.is_read == False)
    
    query = query.order_by(desc(UserNotification.created_at)).limit(limit)
    
    result = await db.execute(query)
    notifications = result.scalars().all()
    return notifications


@router.post("/notifications/mark-read")
async def mark_notifications_read(
    data: MarkNotificationsRead,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark notifications as read"""
    result = await db.execute(
        select(UserNotification)
        .where(UserNotification.user_id == current_user.id)
        .where(UserNotification.id.in_(data.notification_ids))
    )
    notifications = result.scalars().all()
    
    for notification in notifications:
        notification.is_read = True
        notification.read_at = datetime.utcnow()
    
    await db.commit()
    
    return {"message": f"Marked {len(notifications)} notifications as read"}


@router.post("/notifications/mark-all-read")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark all notifications as read"""
    result = await db.execute(
        select(UserNotification)
        .where(UserNotification.user_id == current_user.id)
        .where(UserNotification.is_read == False)
    )
    notifications = result.scalars().all()
    
    for notification in notifications:
        notification.is_read = True
        notification.read_at = datetime.utcnow()
    
    await db.commit()
    
    return {"message": f"Marked {len(notifications)} notifications as read"}


@router.delete("/notifications/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a notification"""
    result = await db.execute(
        select(UserNotification)
        .where(UserNotification.id == notification_id)
        .where(UserNotification.user_id == current_user.id)
    )
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    await db.delete(notification)
    await db.commit()
    
    return {"message": "Notification deleted"}


@router.get("/notifications/unread-count")
async def get_unread_notification_count(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get count of unread notifications"""
    from sqlalchemy import func
    
    result = await db.execute(
        select(func.count())
        .where(UserNotification.user_id == current_user.id)
        .where(UserNotification.is_read == False)
    )
    count = result.scalar()
    
    return {"unread_count": count}
