"""
FastAPI Dependencies
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.config import get_settings
from app.models.user import User
from app.schemas.auth import TokenPayload

settings = get_settings()
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current user from JWT token
    
    Args:
        credentials: HTTP Authorization credentials
        db: Database session
        
    Returns:
        User object
        
    Raises:
        HTTPException: If authentication fails
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        
        if token_data.sub is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if token_data.type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    from sqlalchemy import select
    result = await db.execute(
        select(User).where(User.id == int(token_data.sub))
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user
    
    Args:
        current_user: Current user from token
        
    Returns:
        User object
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_current_vip_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Get current VIP user
    
    Args:
        current_user: Current active user
        
    Returns:
        User object
        
    Raises:
        HTTPException: If user is not VIP
    """
    if not current_user.is_vip:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="VIP access required"
        )
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Get current admin user
    
    Args:
        current_user: Current active user
        
    Returns:
        User object
        
    Raises:
        HTTPException: If user is not admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Get optional user (for endpoints that work with or without authentication)
    
    Args:
        credentials: HTTP Authorization credentials
        db: Database session
        
    Returns:
        User object or None
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


# Pagination dependency
class PaginationParams:
    """Pagination parameters"""
    def __init__(
        self,
        page: int = 1,
        page_size: int = 20,
        order_by: Optional[str] = None,
        order_desc: bool = True
    ):
        self.page = max(1, page)
        self.page_size = min(100, max(1, page_size))
        self.offset = (self.page - 1) * self.page_size
        self.limit = self.page_size
        self.order_by = order_by
        self.order_desc = order_desc


def get_pagination(
    page: int = 1,
    page_size: int = 20,
    order_by: Optional[str] = None,
    order_desc: bool = True
) -> PaginationParams:
    """Get pagination parameters"""
    return PaginationParams(page, page_size, order_by, order_desc)


# Cache dependency
async def get_cache():
    """Get cache instance"""
    from app.utils.cache import cache
    return cache
