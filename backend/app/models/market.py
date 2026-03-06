"""
Market Data Models
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Index, Text, BigInteger, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB

from app.database import Base


class MarketSnapshot(Base):
    """
    Market snapshot - current state of all symbols
    This is a regular table for fast queries
    """
    __tablename__ = "market_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(50), nullable=False)
    name_en = Column(String(50), nullable=True)
    
    # Exchange info
    exchange = Column(String(20), nullable=False, index=True)
    category = Column(String(20), nullable=True, index=True)  # index, metal, energy, etc.
    
    # Price data
    latest_price = Column(Numeric(12, 4), nullable=False)
    price_change = Column(Numeric(12, 4), nullable=True)
    price_change_percent = Column(Numeric(8, 4), nullable=True)
    
    # Options data
    days_to_expiry = Column(Integer, nullable=True)
    implied_vol = Column(Numeric(8, 4), nullable=True)
    iv_change = Column(Numeric(8, 4), nullable=True)
    iv_speed = Column(Numeric(10, 6), nullable=True)
    realized_vol = Column(Numeric(8, 4), nullable=True)
    premium = Column(Numeric(8, 4), nullable=True)
    skew = Column(Numeric(8, 4), nullable=True)
    
    # Percentiles
    iv_percentile = Column(Integer, nullable=True)
    skew_percentile = Column(Integer, nullable=True)
    
    # Flags
    is_main = Column(Boolean, default=True)
    is_foreign = Column(Boolean, default=False)
    
    # Timestamps
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_snapshot_category', 'category'),
        Index('idx_snapshot_exchange', 'exchange'),
        Index('idx_snapshot_iv_percentile', 'iv_percentile'),
    )
    
    def __repr__(self):
        return f"<MarketSnapshot(symbol={self.symbol}, price={self.latest_price})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'name': self.name,
            'nameEn': self.name_en,
            'exchange': self.exchange,
            'category': self.category,
            'latestPrice': float(self.latest_price) if self.latest_price else None,
            'priceChange': float(self.price_change) if self.price_change else None,
            'priceChangePercent': float(self.price_change_percent) if self.price_change_percent else None,
            'daysToExpiry': self.days_to_expiry,
            'impliedVol': float(self.implied_vol) if self.implied_vol else None,
            'ivChange': float(self.iv_change) if self.iv_change else None,
            'ivSpeed': float(self.iv_speed) if self.iv_speed else None,
            'realizedVol': float(self.realized_vol) if self.realized_vol else None,
            'premium': float(self.premium) if self.premium else None,
            'skew': float(self.skew) if self.skew else None,
            'ivPercentile': self.iv_percentile,
            'skewPercentile': self.skew_percentile,
            'isMain': self.is_main,
            'isForeign': self.is_foreign,
        }


class OptionContract(Base):
    """Option contract definitions"""
    __tablename__ = "option_contracts"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, index=True, nullable=False)
    underlying = Column(String(20), nullable=False, index=True)
    option_type = Column(String(4), nullable=False)  # call or put
    strike = Column(Numeric(12, 4), nullable=False)
    expiry_date = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Contract specs
    contract_size = Column(Integer, default=10000)  # Usually 10,000 for options
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    quotes = relationship("OptionQuote", back_populates="contract")
    
    __table_args__ = (
        Index('idx_option_underlying_expiry', 'underlying', 'expiry_date'),
    )
    
    def __repr__(self):
        return f"<OptionContract(symbol={self.symbol}, strike={self.strike})>"


class MarketQuote(Base):
    """
    Historical market quotes - TimescaleDB hypertable
    This will be converted to a hypertable for time-series optimization
    """
    __tablename__ = "market_quotes"
    
    # For TimescaleDB, time must be the first column in primary key
    time = Column(DateTime(timezone=True), primary_key=True, nullable=False)
    symbol = Column(String(20), primary_key=True, nullable=False)
    
    # Price data
    latest_price = Column(Numeric(12, 4), nullable=True)
    price_change = Column(Numeric(12, 4), nullable=True)
    price_change_percent = Column(Numeric(8, 4), nullable=True)
    
    # Volume data
    volume = Column(BigInteger, nullable=True)
    open_interest = Column(BigInteger, nullable=True)
    
    # Volatility data
    implied_vol = Column(Numeric(8, 4), nullable=True)
    iv_change = Column(Numeric(8, 4), nullable=True)
    realized_vol = Column(Numeric(8, 4), nullable=True)
    premium = Column(Numeric(8, 4), nullable=True)
    skew = Column(Numeric(8, 4), nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_quote_symbol_time', 'symbol', 'time'),
    )
    
    def __repr__(self):
        return f"<MarketQuote(symbol={self.symbol}, time={self.time})>"


class OptionQuote(Base):
    """
    Historical option quotes - TimescaleDB hypertable
    """
    __tablename__ = "option_quotes"
    
    time = Column(DateTime(timezone=True), primary_key=True, nullable=False)
    contract_id = Column(Integer, ForeignKey("option_contracts.id"), primary_key=True, nullable=False)
    
    # Price data
    bid = Column(Numeric(12, 4), nullable=True)
    ask = Column(Numeric(12, 4), nullable=True)
    last_price = Column(Numeric(12, 4), nullable=True)
    
    # Volume
    volume = Column(Integer, nullable=True)
    open_interest = Column(Integer, nullable=True)
    
    # Greeks
    implied_vol = Column(Numeric(8, 4), nullable=True)
    delta = Column(Numeric(10, 6), nullable=True)
    gamma = Column(Numeric(12, 8), nullable=True)
    theta = Column(Numeric(12, 6), nullable=True)
    vega = Column(Numeric(12, 6), nullable=True)
    
    # Relationships
    contract = relationship("OptionContract", back_populates="quotes")
    
    def __repr__(self):
        return f"<OptionQuote(contract_id={self.contract_id}, time={self.time})>"


class UnusualFlow(Base):
    """
    Unusual options flow detection
    """
    __tablename__ = "unusual_flows"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Trade info
    symbol = Column(String(20), nullable=False, index=True)
    underlying = Column(String(20), nullable=False, index=True)
    option_type = Column(String(4), nullable=False)  # call or put
    strike = Column(Numeric(12, 4), nullable=False)
    expiry_date = Column(DateTime(timezone=True), nullable=False)
    
    # Volume data
    volume = Column(BigInteger, nullable=False)
    open_interest = Column(BigInteger, nullable=True)
    premium = Column(BigInteger, nullable=False)  # Total premium in currency
    
    # Sentiment analysis
    sentiment = Column(String(10), nullable=False)  # bullish, bearish, neutral
    
    # Trade timestamp
    trade_time = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Detection timestamp
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Additional metadata
    metadata = Column(JSONB, nullable=True)
    
    __table_args__ = (
        Index('idx_flow_symbol_time', 'symbol', 'trade_time'),
        Index('idx_flow_sentiment', 'sentiment'),
    )
    
    def __repr__(self):
        return f"<UnusualFlow(symbol={self.symbol}, volume={self.volume})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'underlying': self.underlying,
            'optionType': self.option_type,
            'strike': float(self.strike) if self.strike else None,
            'expiryDate': self.expiry_date.isoformat() if self.expiry_date else None,
            'volume': self.volume,
            'openInterest': self.open_interest,
            'premium': self.premium,
            'sentiment': self.sentiment,
            'tradeTime': self.trade_time.isoformat() if self.trade_time else None,
        }
