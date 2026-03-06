"""
WebSocket Market Data Handler
Real-time market data streaming
"""
import asyncio
import json
from typing import Dict, Set, List
from datetime import datetime
import logging

from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import AsyncSessionLocal, get_redis
from app.models.market import MarketSnapshot

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket connection manager"""
    
    def __init__(self):
        # Active connections
        self.active_connections: Dict[str, WebSocket] = {}
        # Symbol subscriptions per connection
        self.subscriptions: Dict[str, Set[str]] = {}
        # Global symbol subscriptions (all symbols subscribed by any client)
        self.all_subscribed_symbols: Set[str] = set()
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.subscriptions[client_id] = set()
        logger.info(f"Client {client_id} connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, client_id: str):
        """Remove WebSocket connection"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        
        # Remove subscriptions
        if client_id in self.subscriptions:
            del self.subscriptions[client_id]
        
        # Recalculate all subscribed symbols
        self._recalculate_subscriptions()
        
        logger.info(f"Client {client_id} disconnected. Total: {len(self.active_connections)}")
    
    def subscribe(self, client_id: str, symbols: List[str]):
        """Subscribe client to symbols"""
        if client_id not in self.subscriptions:
            self.subscriptions[client_id] = set()
        
        self.subscriptions[client_id].update(symbols)
        self._recalculate_subscriptions()
        
        logger.debug(f"Client {client_id} subscribed to: {symbols}")
    
    def unsubscribe(self, client_id: str, symbols: List[str]):
        """Unsubscribe client from symbols"""
        if client_id in self.subscriptions:
            self.subscriptions[client_id].difference_update(symbols)
            self._recalculate_subscriptions()
        
        logger.debug(f"Client {client_id} unsubscribed from: {symbols}")
    
    def _recalculate_subscriptions(self):
        """Recalculate all subscribed symbols"""
        self.all_subscribed_symbols = set()
        for symbols in self.subscriptions.values():
            self.all_subscribed_symbols.update(symbols)
    
    async def send_personal_message(self, message: dict, client_id: str):
        """Send message to specific client"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending to {client_id}: {e}")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {e}")
                disconnected.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected:
            self.disconnect(client_id)
    
    async def broadcast_to_subscribers(self, symbol: str, data: dict):
        """Broadcast to clients subscribed to specific symbol"""
        message = {
            "type": "market_update",
            "symbol": symbol,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        disconnected = []
        for client_id, symbols in self.subscriptions.items():
            if symbol in symbols or "*" in symbols:  # * means subscribe to all
                try:
                    await self.active_connections[client_id].send_json(message)
                except Exception as e:
                    logger.error(f"Error sending to {client_id}: {e}")
                    disconnected.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected:
            self.disconnect(client_id)
    
    def get_stats(self) -> dict:
        """Get connection statistics"""
        return {
            "total_connections": len(self.active_connections),
            "total_subscriptions": sum(len(s) for s in self.subscriptions.values()),
            "unique_symbols": len(self.all_subscribed_symbols),
            "symbols": list(self.all_subscribed_symbols)[:20]  # First 20
        }


# Global connection manager
manager = ConnectionManager()


async def handle_market_websocket(websocket: WebSocket, client_id: str):
    """
    Handle WebSocket connection for market data
    
    Message format:
    - Subscribe: {"action": "subscribe", "symbols": ["510300", "510500"]}
    - Unsubscribe: {"action": "unsubscribe", "symbols": ["510300"]}
    - Get snapshot: {"action": "get_snapshot", "symbols": ["510300"]}
    """
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            action = data.get("action")
            symbols = data.get("symbols", [])
            
            if action == "subscribe":
                manager.subscribe(client_id, symbols)
                await manager.send_personal_message({
                    "type": "subscribed",
                    "symbols": list(manager.subscriptions[client_id])
                }, client_id)
            
            elif action == "unsubscribe":
                manager.unsubscribe(client_id, symbols)
                await manager.send_personal_message({
                    "type": "unsubscribed",
                    "symbols": list(manager.subscriptions[client_id])
                }, client_id)
            
            elif action == "get_snapshot":
                # Fetch current snapshot from database
                snapshot_data = await fetch_snapshot_data(symbols)
                await manager.send_personal_message({
                    "type": "snapshot",
                    "data": snapshot_data
                }, client_id)
            
            elif action == "ping":
                await manager.send_personal_message({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                }, client_id)
            
            elif action == "get_stats":
                stats = manager.get_stats()
                await manager.send_personal_message({
                    "type": "stats",
                    "data": stats
                }, client_id)
            
            else:
                await manager.send_personal_message({
                    "type": "error",
                    "message": f"Unknown action: {action}"
                }, client_id)
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
        manager.disconnect(client_id)


async def fetch_snapshot_data(symbols: List[str]) -> List[dict]:
    """Fetch snapshot data from database"""
    async with AsyncSessionLocal() as db:
        if symbols and symbols != ["*"]:
            result = await db.execute(
                select(MarketSnapshot).where(MarketSnapshot.symbol.in_(symbols))
            )
        else:
            result = await db.execute(select(MarketSnapshot))
        
        snapshots = result.scalars().all()
        return [s.to_dict() for s in snapshots]


class MarketDataBroadcaster:
    """
    Broadcast market data updates to subscribed clients
    Runs as a background task
    """
    
    def __init__(self):
        self.is_running = False
        self.last_broadcast = {}
    
    async def broadcast_loop(self, interval: float = 1.0):
        """
        Continuously broadcast market data updates
        
        Args:
            interval: Seconds between broadcasts
        """
        self.is_running = True
        logger.info("Starting market data broadcaster")
        
        while self.is_running:
            try:
                if manager.all_subscribed_symbols:
                    await self._broadcast_updates()
            except Exception as e:
                logger.error(f"Broadcast error: {e}")
            
            await asyncio.sleep(interval)
        
        logger.info("Market data broadcaster stopped")
    
    async def _broadcast_updates(self):
        """Broadcast updates for subscribed symbols"""
        symbols = list(manager.all_subscribed_symbols)
        
        if not symbols:
            return
        
        # Fetch latest data from database
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(MarketSnapshot).where(MarketSnapshot.symbol.in_(symbols))
            )
            snapshots = result.scalars().all()
            
            for snapshot in snapshots:
                symbol = snapshot.symbol
                
                # Check if data has changed since last broadcast
                data = snapshot.to_dict()
                data_hash = hash(json.dumps(data, sort_keys=True, default=str))
                
                if self.last_broadcast.get(symbol) != data_hash:
                    await manager.broadcast_to_subscribers(symbol, data)
                    self.last_broadcast[symbol] = data_hash
    
    def stop(self):
        """Stop broadcaster"""
        self.is_running = False


# Global broadcaster instance
broadcaster = MarketDataBroadcaster()


async def start_broadcaster():
    """Start the market data broadcaster"""
    asyncio.create_task(broadcaster.broadcast_loop())


def stop_broadcaster():
    """Stop the market data broadcaster"""
    broadcaster.stop()
