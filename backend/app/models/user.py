"""
User Related Models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    """User account model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    
    # Profile info
    avatar = Column(String(255), nullable=True)  # Avatar URL
    bio = Column(Text, nullable=True)  # User bio/description
    
    # User status
    is_active = Column(Boolean, default=True)
    is_vip = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    favorites = relationship("UserFavorite", back_populates="user", cascade="all, delete-orphan")
    strategies = relationship("UserStrategy", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("UserNotification", back_populates="user", cascade="all, delete-orphan")
    password_resets = relationship("PasswordReset", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"
    
    def to_dict(self):
        """Convert to dictionary (safe for public)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'avatar': self.avatar,
            'bio': self.bio,
            'is_vip': self.is_vip,
            'email_verified': self.email_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
        }


class PasswordReset(Base):
    """Password reset tokens"""
    __tablename__ = "password_resets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="password_resets")
    
    def __repr__(self):
        return f"<PasswordReset(user_id={self.user_id})>"


class EmailVerification(Base):
    """Email verification tokens"""
    __tablename__ = "email_verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<EmailVerification(user_id={self.user_id})>"


class UserFavorite(Base):
    """User favorite symbols"""
    __tablename__ = "user_favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String(20), nullable=False, index=True)
    category = Column(String(20), nullable=True)  # index, metal, energy, etc.
    notes = Column(Text, nullable=True)  # User notes for this symbol
    alert_enabled = Column(Boolean, default=False)  # Price/volatility alerts
    alert_settings = Column(JSON, nullable=True)  # Alert configuration
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="favorites")
    
    # Unique constraint handled at application level
    
    def __repr__(self):
        return f"<UserFavorite(user_id={self.user_id}, symbol={self.symbol})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'category': self.category,
            'notes': self.notes,
            'alert_enabled': self.alert_enabled,
            'alert_settings': self.alert_settings,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class UserStrategy(Base):
    """User saved strategies"""
    __tablename__ = "user_strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Strategy info
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    strategy_type = Column(String(50), nullable=False)  # bull_spread, iron_condor, etc.
    tags = Column(JSON, nullable=True)  # Strategy tags
    
    # Strategy data stored as JSON
    strategy_data = Column(JSON, nullable=False)
    
    # Underlying info
    underlying_symbol = Column(String(20), nullable=True)
    underlying_price = Column(String(20), nullable=True)  # Price when strategy was created
    
    # Risk metrics (calculated)
    max_profit = Column(String(50), nullable=True)
    max_loss = Column(String(50), nullable=True)
    breakeven_points = Column(JSON, nullable=True)
    probability_of_profit = Column(String(20), nullable=True)
    
    # Performance tracking
    initial_capital = Column(String(50), nullable=True)
    current_pnl = Column(String(50), nullable=True)
    pnl_percent = Column(String(20), nullable=True)
    
    # Visibility
    is_public = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)  # Whether strategy is currently active
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="strategies")
    
    def __repr__(self):
        return f"<UserStrategy(id={self.id}, name={self.name})>"
    
    def to_dict(self, include_private=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'strategy_type': self.strategy_type,
            'tags': self.tags,
            'underlying_symbol': self.underlying_symbol,
            'underlying_price': self.underlying_price,
            'max_profit': self.max_profit,
            'max_loss': self.max_loss,
            'breakeven_points': self.breakeven_points,
            'probability_of_profit': self.probability_of_profit,
            'is_public': self.is_public,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_private:
            data.update({
                'strategy_data': self.strategy_data,
                'initial_capital': self.initial_capital,
                'current_pnl': self.current_pnl,
                'pnl_percent': self.pnl_percent,
            })
        
        return data


class UserNotification(Base):
    """User notifications"""
    __tablename__ = "user_notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Notification content
    type = Column(String(50), nullable=False)  # price_alert, iv_alert, system, etc.
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    data = Column(JSON, nullable=True)  # Additional data
    
    # Status
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    
    def __repr__(self):
        return f"<UserNotification(id={self.id}, type={self.type})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'data': self.data,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class LoginHistory(Base):
    """User login history"""
    __tablename__ = "login_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Login info
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    login_method = Column(String(20), nullable=True)  # password, oauth, etc.
    success = Column(Boolean, default=True)
    failure_reason = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<LoginHistory(user_id={self.user_id})>"
