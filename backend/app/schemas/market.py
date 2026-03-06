"""
Market Data Schemas
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class MarketSnapshot(BaseModel):
    """Market snapshot schema"""
    symbol: str
    name: str
    market_type: str
    price: float
    change: float
    change_percent: float
    open: Optional[float]
    high: Optional[float]
    low: Optional[float]
    pre_close: Optional[float]
    volume: int
    turnover: Optional[float]
    open_interest: Optional[int]
    iv: Optional[float]
    iv_percentile: Optional[float]
    iv_rank: Optional[float]
    hv: Optional[float]
    hv_percentile: Optional[float]
    put_call_ratio: Optional[float]
    timestamp: datetime


class SymbolDetail(BaseModel):
    """Symbol detail schema"""
    symbol: str
    name: str
    market_type: str
    price: float
    change: float
    change_percent: float
    open: Optional[float]
    high: Optional[float]
    low: Optional[float]
    pre_close: Optional[float]
    volume: int
    turnover: Optional[float]
    open_interest: Optional[int]
    iv: Optional[float]
    iv_percentile: Optional[float]
    iv_rank: Optional[float]
    hv: Optional[float]
    hv_percentile: Optional[float]
    put_call_ratio: Optional[float]
    iv_history: Optional[List[Dict[str, Any]]]
    price_history: Optional[List[Dict[str, Any]]]
    option_chain: Optional[List[Dict[str, Any]]]
    timestamp: datetime


class HistoricalData(BaseModel):
    """Historical data point"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    open_interest: Optional[int]
    iv: Optional[float]


class HistoricalDataResponse(BaseModel):
    """Historical data response"""
    symbol: str
    interval: str
    data: List[HistoricalData]


class TopListItem(BaseModel):
    """Top list item"""
    rank: int
    symbol: str
    name: str
    price: float
    change: float
    change_percent: float
    iv: Optional[float]
    iv_change: Optional[float]
    volume: int
    volume_change: Optional[float]


class TopListResponse(BaseModel):
    """Top list response"""
    type: str
    title: str
    updated_at: datetime
    items: List[TopListItem]


class UnusualFlowItem(BaseModel):
    """Unusual flow item"""
    id: str
    symbol: str
    option_symbol: str
    option_type: str
    strike: float
    expiry_date: str
    volume: int
    open_interest: int
    volume_oi_ratio: float
    premium: float
    sentiment: str  # bullish, bearish, neutral
    timestamp: datetime


class UnusualFlowResponse(BaseModel):
    """Unusual flow response"""
    items: List[UnusualFlowItem]
    total: int
    updated_at: datetime


class OptionChainItem(BaseModel):
    """Option chain item"""
    strike: float
    expiry_date: str
    days_to_expiry: int
    call: Optional[Dict[str, Any]]
    put: Optional[Dict[str, Any]]


class OptionChainResponse(BaseModel):
    """Option chain response"""
    underlying_symbol: str
    underlying_price: float
    expiry_dates: List[str]
    strikes: List[float]
    chain: List[OptionChainItem]


class GreeksData(BaseModel):
    """Option greeks"""
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float
    implied_volatility: float


class OptionQuote(BaseModel):
    """Option quote"""
    symbol: str
    underlying_symbol: str
    option_type: str
    strike: float
    expiry_date: str
    days_to_expiry: int
    price: float
    change: float
    change_percent: float
    volume: int
    open_interest: int
    bid: float
    ask: float
    bid_volume: int
    ask_volume: int
    iv: float
    delta: Optional[float]
    gamma: Optional[float]
    theta: Optional[float]
    vega: Optional[float]
    rho: Optional[float]
    intrinsic_value: float
    time_value: float
    break_even: float
    timestamp: datetime
