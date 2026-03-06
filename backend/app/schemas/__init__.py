"""
Pydantic Schemas
"""
from app.schemas.auth import (
    Token,
    TokenPayload,
    LoginRequest,
    RegisterRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordChange,
    ProfileUpdate,
)
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserProfile,
    FavoriteBase,
    FavoriteCreate,
    FavoriteUpdate,
    FavoriteResponse,
    StrategyBase,
    StrategyCreate,
    StrategyUpdate,
    StrategyResponse,
    StrategyDetailResponse,
    NotificationResponse,
)
from app.schemas.market import (
    MarketSnapshot,
    SymbolDetail,
    HistoricalData,
    TopListItem,
    UnusualFlowItem,
)
from app.schemas.strategy import (
    StrategyLeg,
    StrategyAnalysisRequest,
    StrategyAnalysisResponse,
    StrategyTemplate,
)

__all__ = [
    # Auth schemas
    "Token",
    "TokenPayload",
    "LoginRequest",
    "RegisterRequest",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    "PasswordChange",
    "ProfileUpdate",
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserProfile",
    "FavoriteBase",
    "FavoriteCreate",
    "FavoriteUpdate",
    "FavoriteResponse",
    "StrategyBase",
    "StrategyCreate",
    "StrategyUpdate",
    "StrategyResponse",
    "StrategyDetailResponse",
    "NotificationResponse",
    # Market schemas
    "MarketSnapshot",
    "SymbolDetail",
    "HistoricalData",
    "TopListItem",
    "UnusualFlowItem",
    # Strategy schemas
    "StrategyLeg",
    "StrategyAnalysisRequest",
    "StrategyAnalysisResponse",
    "StrategyTemplate",
]
