"""
Data Collector Service
Collects market data from various sources (akshare, tushare, etc.)
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from decimal import Decimal
import logging

import akshare as ak
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.config import get_settings
from app.database import AsyncSessionLocal
from app.models.market import MarketSnapshot, MarketQuote

logger = logging.getLogger(__name__)
settings = get_settings()


class DataCollector:
    """Market data collector"""
    
    # Symbol mapping for different data sources
    SYMBOL_MAP = {
        # Index ETFs
        "510300": {"name": "沪深300ETF", "exchange": "SSE", "category": "index"},
        "510500": {"name": "中证500ETF", "exchange": "SSE", "category": "index"},
        "159915": {"name": "创业板ETF", "exchange": "SZSE", "category": "index"},
        "588000": {"name": "科创50ETF", "exchange": "SSE", "category": "index"},
        
        # Futures (simplified mapping)
        "IF": {"name": "沪深300期货", "exchange": "CFFEX", "category": "index"},
        "IC": {"name": "中证500期货", "exchange": "CFFEX", "category": "index"},
        "IM": {"name": "中证1000期货", "exchange": "CFFEX", "category": "index"},
        "IH": {"name": "上证50期货", "exchange": "CFFEX", "category": "index"},
        
        # Commodities
        "CU": {"name": "沪铜", "exchange": "SHFE", "category": "metal"},
        "AL": {"name": "沪铝", "exchange": "SHFE", "category": "metal"},
        "ZN": {"name": "沪锌", "exchange": "SHFE", "category": "metal"},
        "NI": {"name": "沪镍", "exchange": "SHFE", "category": "metal"},
        "SN": {"name": "沪锡", "exchange": "SHFE", "category": "metal"},
        "AU": {"name": "沪金", "exchange": "SHFE", "category": "metal"},
        "AG": {"name": "沪银", "exchange": "SHFE", "category": "metal"},
        
        # Energy
        "SC": {"name": "原油", "exchange": "INE", "category": "energy"},
        "FU": {"name": "燃油", "exchange": "SHFE", "category": "energy"},
        "LU": {"name": "低硫燃油", "exchange": "SHFE", "category": "energy"},
        "PG": {"name": "LPG", "exchange": "SHFE", "category": "energy"},
        
        # Agriculture
        "M": {"name": "豆粕", "exchange": "DCE", "category": "agri"},
        "Y": {"name": "豆油", "exchange": "DCE", "category": "agri"},
        "P": {"name": "棕榈油", "exchange": "DCE", "category": "agri"},
        "C": {"name": "玉米", "exchange": "DCE", "category": "agri"},
        "CF": {"name": "棉花", "exchange": "ZCE", "category": "agri"},
        "SR": {"name": "白糖", "exchange": "ZCE", "category": "agri"},
        "LH": {"name": "生猪", "exchange": "DCE", "category": "agri"},
        
        # Black metals
        "RB": {"name": "螺纹钢", "exchange": "SHFE", "category": "black"},
        "HC": {"name": "热卷", "exchange": "SHFE", "category": "black"},
        "I": {"name": "铁矿石", "exchange": "DCE", "category": "black"},
        "JM": {"name": "焦煤", "exchange": "DCE", "category": "black"},
        "J": {"name": "焦炭", "exchange": "DCE", "category": "black"},
        "SM": {"name": "锰硅", "exchange": "ZCE", "category": "black"},
        
        # Chemicals
        "L": {"name": "塑料", "exchange": "DCE", "category": "chemical"},
        "PP": {"name": "聚丙烯", "exchange": "DCE", "category": "chemical"},
        "PVC": {"name": "PVC", "exchange": "DCE", "category": "chemical"},
        "MA": {"name": "甲醇", "exchange": "ZCE", "category": "chemical"},
        "TA": {"name": "PTA", "exchange": "ZCE", "category": "chemical"},
        "EG": {"name": "乙二醇", "exchange": "DCE", "category": "chemical"},
        "EB": {"name": "苯乙烯", "exchange": "DCE", "category": "chemical"},
        
        # New materials
        "LC": {"name": "碳酸锂", "exchange": "GFEX", "category": "new"},
        "SI": {"name": "工业硅", "exchange": "GFEX", "category": "new"},
    }
    
    def __init__(self):
        self.is_running = False
        self.last_update = {}
    
    async def fetch_option_market_data(self) -> List[Dict[str, Any]]:
        """
        Fetch options market data from akshare
        Returns list of market data for all symbols
        """
        try:
            # Get ETF options data
            etf_data = await self._fetch_etf_options_data()
            
            # Get commodity options data
            commodity_data = await self._fetch_commodity_options_data()
            
            # Combine data
            all_data = etf_data + commodity_data
            
            return all_data
            
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            return []
    
    async def _fetch_etf_options_data(self) -> List[Dict[str, Any]]:
        """Fetch ETF options data"""
        data = []
        
        try:
            # 300ETF options
            df_300 = ak.option_cffex_sz50_daily_sina()
            if df_300 is not None and not df_300.empty:
                for _, row in df_300.iterrows():
                    symbol = str(row.get('symbol', ''))
                    if '510300' in symbol or '300' in symbol:
                        data.append(self._parse_etf_option_row(row, '510300'))
            
            # 50ETF options
            df_50 = ak.option_cffex_sz50_daily_sina()
            if df_50 is not None and not df_50.empty:
                for _, row in df_50.iterrows():
                    symbol = str(row.get('symbol', ''))
                    if '510050' in symbol or '50' in symbol:
                        data.append(self._parse_etf_option_row(row, '510050'))
                        
        except Exception as e:
            logger.warning(f"Error fetching ETF options: {e}")
        
        return data
    
    async def _fetch_commodity_options_data(self) -> List[Dict[str, Any]]:
        """Fetch commodity options data"""
        data = []
        
        # List of commodity symbols to fetch
        commodity_symbols = [
            'CU', 'AL', 'ZN', 'AU', 'AG',  # Metals
            'SC', 'FU',  # Energy
            'M', 'C', 'LH',  # Agriculture
            'RB', 'I', 'JM',  # Black metals
            'PP', 'PVC', 'MA', 'TA',  # Chemicals
        ]
        
        for symbol in commodity_symbols:
            try:
                # Use akshare to get commodity option data
                df = ak.option_dce_daily(symbol=symbol)
                if df is not None and not df.empty:
                    for _, row in df.iterrows():
                        data.append(self._parse_commodity_option_row(row, symbol))
            except Exception as e:
                logger.debug(f"Error fetching {symbol} options: {e}")
                continue
        
        return data
    
    def _parse_etf_option_row(self, row: Any, underlying: str) -> Dict[str, Any]:
        """Parse ETF option data row"""
        return {
            'symbol': underlying,
            'latest_price': float(row.get('latest_price', 0) or 0),
            'price_change': float(row.get('price_change', 0) or 0),
            'price_change_percent': float(row.get('price_change_percent', 0) or 0),
            'implied_vol': float(row.get('implied_volatility', 0) or 0) * 100,
            'volume': int(row.get('volume', 0) or 0),
            'open_interest': int(row.get('open_interest', 0) or 0),
        }
    
    def _parse_commodity_option_row(self, row: Any, underlying: str) -> Dict[str, Any]:
        """Parse commodity option data row"""
        return {
            'symbol': underlying,
            'latest_price': float(row.get('latest_price', 0) or 0),
            'price_change': float(row.get('price_change', 0) or 0),
            'price_change_percent': float(row.get('price_change_percent', 0) or 0),
            'implied_vol': float(row.get('implied_volatility', 0) or 0) * 100,
            'volume': int(row.get('volume', 0) or 0),
            'open_interest': int(row.get('open_interest', 0) or 0),
        }
    
    async def fetch_underlying_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Fetch underlying asset price
        """
        try:
            if symbol in ['510300', '510500', '159915', '588000']:
                # ETF - use akshare
                df = ak.fund_etf_hist_em(symbol=symbol, period="daily", start_date="20240101", adjust="")
                if df is not None and not df.empty:
                    latest = df.iloc[-1]
                    prev = df.iloc[-2] if len(df) > 1 else latest
                    
                    return {
                        'symbol': symbol,
                        'latest_price': float(latest['close']),
                        'price_change': float(latest['close']) - float(prev['close']),
                        'price_change_percent': (float(latest['close']) / float(prev['close']) - 1) * 100,
                        'volume': int(latest['volume']),
                    }
            
            else:
                # Futures - use akshare futures data
                df = ak.futures_zh_realtime(symbol=symbol)
                if df is not None and not df.empty:
                    row = df.iloc[0]
                    return {
                        'symbol': symbol,
                        'latest_price': float(row.get('latest', 0)),
                        'price_change': float(row.get('change', 0)),
                        'price_change_percent': float(row.get('change_percent', 0)),
                        'volume': int(row.get('volume', 0)),
                    }
                    
        except Exception as e:
            logger.warning(f"Error fetching price for {symbol}: {e}")
        
        return None
    
    async def calculate_iv_metrics(self, symbol: str, iv: float) -> Dict[str, Any]:
        """
        Calculate IV metrics (percentile, change, etc.)
        In production, this would query historical data
        """
        # Placeholder - would query historical IV data
        return {
            'iv_change': 0.0,
            'iv_speed': 0.0,
            'realized_vol': iv * 0.8,  # Simplified
            'premium': iv * 0.2,  # Simplified
            'skew': 0.0,
            'iv_percentile': 50,
            'skew_percentile': 50,
        }
    
    async def update_market_snapshot(self, db: AsyncSession, data: Dict[str, Any]):
        """
        Update market snapshot in database
        """
        symbol = data.get('symbol')
        if not symbol:
            return
        
        # Check if snapshot exists
        result = await db.execute(
            select(MarketSnapshot).where(MarketSnapshot.symbol == symbol)
        )
        snapshot = result.scalar_one_or_none()
        
        symbol_info = self.SYMBOL_MAP.get(symbol, {})
        
        # Calculate IV metrics
        iv_metrics = await self.calculate_iv_metrics(
            symbol, 
            data.get('implied_vol', 0)
        )
        
        if snapshot:
            # Update existing
            snapshot.latest_price = Decimal(str(data.get('latest_price', 0)))
            snapshot.price_change = Decimal(str(data.get('price_change', 0)))
            snapshot.price_change_percent = Decimal(str(data.get('price_change_percent', 0)))
            snapshot.implied_vol = Decimal(str(data.get('implied_vol', 0)))
            snapshot.iv_change = Decimal(str(iv_metrics['iv_change']))
            snapshot.iv_speed = Decimal(str(iv_metrics['iv_speed']))
            snapshot.realized_vol = Decimal(str(iv_metrics['realized_vol']))
            snapshot.premium = Decimal(str(iv_metrics['premium']))
            snapshot.skew = Decimal(str(iv_metrics['skew']))
            snapshot.iv_percentile = iv_metrics['iv_percentile']
            snapshot.skew_percentile = iv_metrics['skew_percentile']
        else:
            # Create new
            snapshot = MarketSnapshot(
                symbol=symbol,
                name=symbol_info.get('name', symbol),
                exchange=symbol_info.get('exchange', 'UNKNOWN'),
                category=symbol_info.get('category'),
                latest_price=Decimal(str(data.get('latest_price', 0))),
                price_change=Decimal(str(data.get('price_change', 0))),
                price_change_percent=Decimal(str(data.get('price_change_percent', 0))),
                implied_vol=Decimal(str(data.get('implied_vol', 0))),
                iv_change=Decimal(str(iv_metrics['iv_change'])),
                iv_speed=Decimal(str(iv_metrics['iv_speed'])),
                realized_vol=Decimal(str(iv_metrics['realized_vol'])),
                premium=Decimal(str(iv_metrics['premium'])),
                skew=Decimal(str(iv_metrics['skew'])),
                iv_percentile=iv_metrics['iv_percentile'],
                skew_percentile=iv_metrics['skew_percentile'],
                is_main=True,
                is_foreign=False,
            )
            db.add(snapshot)
        
        await db.commit()
    
    async def run_once(self):
        """Run data collection once"""
        logger.info("Starting data collection...")
        
        async with AsyncSessionLocal() as db:
            # Fetch all market data
            market_data = await self.fetch_option_market_data()
            
            for data in market_data:
                try:
                    await self.update_market_snapshot(db, data)
                except Exception as e:
                    logger.error(f"Error updating {data.get('symbol')}: {e}")
                    continue
            
            logger.info(f"Updated {len(market_data)} symbols")
    
    async def run_continuous(self, interval: int = 5):
        """
        Run continuous data collection
        
        Args:
            interval: Seconds between updates
        """
        self.is_running = True
        logger.info(f"Starting continuous data collection (interval: {interval}s)")
        
        while self.is_running:
            try:
                await self.run_once()
            except Exception as e:
                logger.error(f"Error in data collection: {e}")
            
            await asyncio.sleep(interval)
    
    def stop(self):
        """Stop continuous collection"""
        self.is_running = False
        logger.info("Data collection stopped")


# Global collector instance
data_collector = DataCollector()


async def collect_market_data():
    """Entry point for Celery task"""
    await data_collector.run_once()
