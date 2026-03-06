"""
WebSocket Router
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
import uuid
import logging

from app.websocket.market_ws import handle_market_websocket, manager, start_broadcaster

logger = logging.getLogger(__name__)
router = APIRouter()

# Track if broadcaster has been started
_broadcaster_started = False


@router.websocket("/market")
async def market_websocket(
    websocket: WebSocket,
    client_id: str = Query(None)
):
    """
    WebSocket endpoint for real-time market data
    
    Query Parameters:
    - client_id: Optional client identifier (auto-generated if not provided)
    
    Message Protocol:
    - Subscribe: {"action": "subscribe", "symbols": ["510300", "510500"]}
    - Unsubscribe: {"action": "unsubscribe", "symbols": ["510300"]}
    - Get snapshot: {"action": "get_snapshot", "symbols": ["510300"]}
    - Ping: {"action": "ping"}
    - Get stats: {"action": "get_stats"}
    
    Response Types:
    - market_update: {"type": "market_update", "symbol": "510300", "data": {...}, "timestamp": "..."}
    - subscribed: {"type": "subscribed", "symbols": [...]}
    - snapshot: {"type": "snapshot", "data": [...]}
    - pong: {"type": "pong", "timestamp": "..."}
    - stats: {"type": "stats", "data": {...}}
    """
    global _broadcaster_started
    
    # Generate client_id if not provided
    if not client_id:
        client_id = str(uuid.uuid4())[:8]
    
    # Start broadcaster on first connection
    if not _broadcaster_started:
        await start_broadcaster()
        _broadcaster_started = True
    
    await handle_market_websocket(websocket, client_id)


@router.get("/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics"""
    return manager.get_stats()
