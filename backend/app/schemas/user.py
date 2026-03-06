"""
User Schemas
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class UserBase(BaseModel):
    """User base schema"""
    username: str
    email: EmailStr


class UserCreate(UserBase):
    """User create schema"""
    password: str = Field(..., min_length=8)
    phone: Optional[str] = None


class UserUpdate(BaseModel):
    """User update schema"""
    phone: Optional[str] = None
    bio: Optional[str] = None


class UserResponse(UserBase):
    """User response schema"""
    id: int
    phone: Optional[str]
    avatar: Optional[str]
    bio: Optional[str]
    is_active: bool
    is_vip: bool
    email_verified: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    """User profile schema"""
    id: int
    username: str
    email: str
    phone: Optional[str]
    avatar: Optional[str]
    bio: Optional[str]
    is_vip: bool
    email_verified: bool
    favorite_count: int
    strategy_count: int
    notification_count: int
    unread_notification_count: int
    created_at: datetime
    last_login: Optional[datetime]


# Favorite schemas
class FavoriteBase(BaseModel):
    """Favorite base schema"""
    symbol: str = Field(..., min_length=1, max_length=20)
    symbol_type: str = Field(default="ETF", pattern=r'^(ETF|INDEX|STOCK|OPTION)$')
    remark: Optional[str] = Field(None, max_length=200)


class FavoriteCreate(FavoriteBase):
    """Favorite create schema"""
    pass


class FavoriteUpdate(BaseModel):
    """Favorite update schema"""
    remark: Optional[str] = Field(None, max_length=200)
    alert_enabled: Optional[bool] = None
    alert_settings: Optional[Dict[str, Any]] = None


class FavoriteResponse(FavoriteBase):
    """Favorite response schema"""
    id: int
    user_id: int
    notes: Optional[str]
    alert_enabled: bool
    alert_settings: Optional[Dict[str, Any]]
    created_at: datetime
    # Optional market data (when include_data=true)
    market_data: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


# Strategy schemas
class StrategyLeg(BaseModel):
    """Strategy leg schema"""
    symbol: str
    side: str = Field(..., pattern=r'^(buy|sell)$')
    quantity: int = Field(..., gt=0)
    option_type: Optional[str] = Field(None, pattern=r'^(call|put)$')
    strike: Optional[float] = None
    expiry: Optional[str] = None


class StrategyBase(BaseModel):
    """Strategy base schema"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    strategy_type: str = Field(default="custom", pattern=r'^(custom|spread|iron_condor|butterfly|calendar|diagonal|straddle|strangle|covered_call|protective_put)$')


class StrategyCreate(StrategyBase):
    """Strategy create schema"""
    legs: List[StrategyLeg] = Field(..., min_length=1)
    parameters: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class StrategyUpdate(BaseModel):
    """Strategy update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    legs: Optional[List[StrategyLeg]] = None
    parameters: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None


class StrategyResponse(StrategyBase):
    """Strategy response schema"""
    id: int
    user_id: int
    legs: List[Dict[str, Any]]
    parameters: Optional[Dict[str, Any]]
    tags: Optional[List[str]]
    underlying_symbol: Optional[str]
    underlying_price: Optional[str]
    probability_of_profit: Optional[str]
    initial_capital: Optional[str]
    current_pnl: Optional[str]
    pnl_percent: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    closed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class StrategyDetailResponse(StrategyResponse):
    """Strategy detail response with analysis"""
    analysis: Optional[Dict[str, Any]] = None
    greeks: Optional[Dict[str, float]] = None
    payoff_data: Optional[List[Dict[str, Any]]] = None


# Notification schemas
class NotificationResponse(BaseModel):
    """Notification response schema"""
    id: int
    user_id: int
    type: str
    title: str
    message: str
    data: Optional[Dict[str, Any]]
    is_read: bool
    read_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Login history schema
class LoginHistoryResponse(BaseModel):
    """Login history response schema"""
    id: int
    ip_address: Optional[str]
    user_agent: Optional[str]
    login_method: Optional[str]
    success: bool
    failure_reason: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
