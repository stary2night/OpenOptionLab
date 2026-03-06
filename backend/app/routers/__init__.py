"""
API Routers
"""
from fastapi import APIRouter

from app.routers import auth, market, user, strategy, health, websocket

# Main API router
api_router = APIRouter(prefix="/api/v1")

# Include all sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(market.router, prefix="/market", tags=["Market Data"])
api_router.include_router(user.router, prefix="/user", tags=["User"])
api_router.include_router(strategy.router, prefix="/strategy", tags=["Strategy"])
api_router.include_router(health.router, prefix="/health", tags=["Health"])

# WebSocket router (no prefix, direct mount)
ws_router = APIRouter()
ws_router.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])

__all__ = ["api_router", "ws_router"]
