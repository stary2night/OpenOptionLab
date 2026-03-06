"""
Celery Tasks for Market Data Collection
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any

from celery import shared_task
from celery.utils.log import get_task_logger

from app.database import async_session
from app.services.data_collector import DataCollector
from app.utils.cache import Cache

logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def collect_market_snapshot(self, symbols: List[str] = None):
    """
    Collect market snapshot data for specified symbols
    
    Args:
        symbols: List of symbols to collect (default: major ETFs)
    """
    if symbols is None:
        symbols = ["510050", "510300", "159919", "588000"]  # Major ETFs
    
    logger.info(f"Collecting market snapshot for {len(symbols)} symbols")
    
    try:
        # Run async code in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(_collect_snapshot_async(symbols))
        loop.close()
        
        logger.info(f"Successfully collected snapshot for {len(result)} symbols")
        return {"status": "success", "count": len(result), "symbols": symbols}
        
    except Exception as exc:
        logger.error(f"Failed to collect market snapshot: {exc}")
        raise self.retry(exc=exc)


async def _collect_snapshot_async(symbols: List[str]) -> List[Dict[str, Any]]:
    """Async helper for collecting snapshot"""
    async with async_session() as db:
        collector = DataCollector(db)
        results = []
        
        for symbol in symbols:
            try:
                data = await collector.collect_option_snapshot(symbol)
                if data:
                    results.append(data)
            except Exception as e:
                logger.warning(f"Failed to collect {symbol}: {e}")
        
        return results


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def collect_option_chain(self, underlying_symbol: str):
    """
    Collect option chain data for an underlying symbol
    
    Args:
        underlying_symbol: Underlying symbol (e.g., "510050")
    """
    logger.info(f"Collecting option chain for {underlying_symbol}")
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(_collect_option_chain_async(underlying_symbol))
        loop.close()
        
        logger.info(f"Successfully collected option chain for {underlying_symbol}")
        return {"status": "success", "symbol": underlying_symbol, "count": len(result)}
        
    except Exception as exc:
        logger.error(f"Failed to collect option chain: {exc}")
        raise self.retry(exc=exc)


async def _collect_option_chain_async(underlying_symbol: str) -> List[Dict[str, Any]]:
    """Async helper for collecting option chain"""
    async with async_session() as db:
        collector = DataCollector(db)
        return await collector.collect_option_chain(underlying_symbol)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def detect_unusual_flows(self, lookback_minutes: int = 5):
    """
    Detect unusual option flows
    
    Args:
        lookback_minutes: Time window to look back for detection
    """
    logger.info(f"Detecting unusual flows (last {lookback_minutes} minutes)")
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(_detect_flows_async(lookback_minutes))
        loop.close()
        
        logger.info(f"Detected {len(result)} unusual flows")
        return {"status": "success", "count": len(result), "flows": result}
        
    except Exception as exc:
        logger.error(f"Failed to detect unusual flows: {exc}")
        raise self.retry(exc=exc)


async def _detect_flows_async(lookback_minutes: int) -> List[Dict[str, Any]]:
    """Async helper for detecting unusual flows"""
    async with async_session() as db:
        collector = DataCollector(db)
        return await collector.detect_unusual_flows(lookback_minutes)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def update_iv_rank(self, days: int = 252):
    """
    Update IV Rank and IV Percentile for all symbols
    
    Args:
        days: Lookback period in trading days (default: 1 year)
    """
    logger.info(f"Updating IV Rank (lookback: {days} days)")
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(_update_iv_rank_async(days))
        loop.close()
        
        logger.info(f"Successfully updated IV Rank for {len(result)} symbols")
        return {"status": "success", "count": len(result)}
        
    except Exception as exc:
        logger.error(f"Failed to update IV Rank: {exc}")
        raise self.retry(exc=exc)


async def _update_iv_rank_async(days: int) -> List[str]:
    """Async helper for updating IV Rank"""
    async with async_session() as db:
        collector = DataCollector(db)
        
        # Get all symbols with options
        from sqlalchemy import select
        from app.models.market import OptionContract
        
        result = await db.execute(
            select(OptionContract.underlying_symbol).distinct()
        )
        symbols = [row[0] for row in result.fetchall()]
        
        updated = []
        for symbol in symbols:
            try:
                await collector.calculate_iv_rank(symbol, days)
                updated.append(symbol)
            except Exception as e:
                logger.warning(f"Failed to update IV Rank for {symbol}: {e}")
        
        return updated


@shared_task
def cleanup_old_data(retention_days: int = 90):
    """
    Clean up old market data to save storage
    
    Args:
        retention_days: Number of days to retain data
    """
    logger.info(f"Cleaning up data older than {retention_days} days")
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(_cleanup_data_async(retention_days))
        loop.close()
        
        logger.info(f"Cleanup completed: {result}")
        return result
        
    except Exception as exc:
        logger.error(f"Failed to cleanup data: {exc}")
        return {"status": "error", "error": str(exc)}


async def _cleanup_data_async(retention_days: int) -> Dict[str, Any]:
    """Async helper for data cleanup"""
    from sqlalchemy import text
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    
    async with async_session() as db:
        # Clean up old quotes (TimescaleDB has efficient deletion)
        tables = ["market_quotes", "option_quotes", "unusual_flows"]
        
        deleted_counts = {}
        for table in tables:
            result = await db.execute(
                text(f"""
                    SELECT hypertable_size('{table}') as size
                """)
            )
            
            # For TimescaleDB, use drop_chunks for efficient cleanup
            await db.execute(
                text(f"""
                    SELECT drop_chunks('{table}', older_than => '{cutoff_date}'::timestamp)
                """)
            )
            
            deleted_counts[table] = "chunks dropped"
        
        await db.commit()
        
        return {
            "status": "success",
            "cutoff_date": cutoff_date.isoformat(),
            "deleted": deleted_counts
        }


@shared_task
def send_market_alert():
    """
    Send market alerts to users based on their alert settings
    """
    logger.info("Processing market alerts")
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(_send_alerts_async())
        loop.close()
        
        logger.info(f"Sent {result['sent']} alerts")
        return result
        
    except Exception as exc:
        logger.error(f"Failed to send alerts: {exc}")
        return {"status": "error", "error": str(exc)}


async def _send_alerts_async() -> Dict[str, Any]:
    """Async helper for sending alerts"""
    async with async_session() as db:
        from sqlalchemy import select, and_
        from app.models.user import UserFavorite, UserNotification
        from app.services.market_data import MarketDataService
        
        market_service = MarketDataService(db)
        
        # Get all favorites with alerts enabled
        result = await db.execute(
            select(UserFavorite).where(
                and_(
                    UserFavorite.alert_enabled == True,
                    UserFavorite.alert_settings.isnot(None)
                )
            )
        )
        favorites = result.scalars().all()
        
        sent_count = 0
        for fav in favorites:
            try:
                # Get current price
                snapshot = await market_service.get_symbol_detail(fav.symbol)
                if not snapshot:
                    continue
                
                current_price = snapshot.get("price", 0)
                alert_settings = fav.alert_settings or {}
                
                # Check price conditions
                price_above = alert_settings.get("price_above")
                price_below = alert_settings.get("price_below")
                
                should_alert = False
                alert_message = ""
                
                if price_above and current_price >= price_above:
                    should_alert = True
                    alert_message = f"{fav.symbol} 价格已上涨至 {current_price}，超过设定值 {price_above}"
                
                if price_below and current_price <= price_below:
                    should_alert = True
                    alert_message = f"{fav.symbol} 价格已下跌至 {current_price}，低于设定值 {price_below}"
                
                if should_alert:
                    # Create notification
                    notification = UserNotification(
                        user_id=fav.user_id,
                        type="price_alert",
                        title=f"价格提醒: {fav.symbol}",
                        message=alert_message,
                        data={
                            "symbol": fav.symbol,
                            "current_price": current_price,
                            "alert_settings": alert_settings
                        }
                    )
                    db.add(notification)
                    sent_count += 1
                    
                    # TODO: Send email/push notification
                    
            except Exception as e:
                logger.warning(f"Failed to process alert for {fav.symbol}: {e}")
        
        await db.commit()
        
        return {"status": "success", "sent": sent_count}
