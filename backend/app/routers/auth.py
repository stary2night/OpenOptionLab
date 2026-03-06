"""
Authentication Router
"""
from datetime import datetime, timedelta
from typing import Optional
import secrets
import string

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.config import get_settings
from app.database import get_db
from app.models.user import User, PasswordReset, EmailVerification, LoginHistory

router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Settings
settings = get_settings()


# ============== Pydantic Models ==============

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    username: Optional[str] = None


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: str = Field(..., min_length=8)
    phone: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    phone: Optional[str]
    avatar: Optional[str]
    bio: Optional[str]
    is_vip: bool
    email_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


class UpdateProfile(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    phone: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)
    avatar: Optional[str] = None


class EmailVerifyRequest(BaseModel):
    email: EmailStr


# ============== Helper Functions ==============

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def generate_reset_token() -> str:
    """Generate secure random token for password reset"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(64))


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if username is None or token_type != "access":
            raise credentials_exception
        
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    result = await db.execute(select(User).where(User.username == token_data.username))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def record_login_history(
    db: AsyncSession,
    user_id: int,
    request: Request,
    success: bool = True,
    failure_reason: Optional[str] = None
):
    """Record login attempt in history"""
    history = LoginHistory(
        user_id=user_id,
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None,
        success=success,
        failure_reason=failure_reason
    )
    db.add(history)
    await db.commit()


# ============== Routes ==============

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    # Check if username exists
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        phone=user_data.phone,
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Login and get access token"""
    # Find user by username
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()
    
    # Verify credentials
    if not user or not verify_password(form_data.password, user.password_hash):
        # Record failed login
        if user:
            await record_login_history(db, user.id, request, success=False, failure_reason="Invalid password")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        await record_login_history(db, user.id, request, success=False, failure_reason="Account inactive")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()
    
    # Record successful login
    await record_login_history(db, user.id, request, success=True)
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    """Refresh access token using refresh token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if username is None or token_type != "refresh":
            raise credentials_exception
        
    except JWTError:
        raise credentials_exception
    
    # Verify user still exists
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    
    if user is None or not user.is_active:
        raise credentials_exception
    
    # Create new tokens
    new_access_token = create_access_token(data={"sub": user.username})
    new_refresh_token = create_refresh_token(data={"sub": user.username})
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """Get current user info"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_me(
    profile_data: UpdateProfile,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user profile"""
    # Check if username is being changed and if it's available
    if profile_data.username and profile_data.username != current_user.username:
        result = await db.execute(select(User).where(User.username == profile_data.username))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        current_user.username = profile_data.username
    
    # Update other fields
    if profile_data.phone is not None:
        current_user.phone = profile_data.phone
    if profile_data.bio is not None:
        current_user.bio = profile_data.bio
    if profile_data.avatar is not None:
        current_user.avatar = profile_data.avatar
    
    await db.commit()
    await db.refresh(current_user)
    
    return current_user


@router.post("/change-password")
async def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Change current user password"""
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.password_hash = get_password_hash(password_data.new_password)
    await db.commit()
    
    return {"message": "Password changed successfully"}


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """Logout (client should discard tokens)"""
    # In a more advanced setup, you might want to blacklist tokens
    return {"message": "Successfully logged out"}


# ============== Password Reset ==============

@router.post("/password-reset/request")
async def request_password_reset(
    reset_request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    """Request password reset (sends email with reset link)"""
    # Find user by email
    result = await db.execute(select(User).where(User.email == reset_request.email))
    user = result.scalar_one_or_none()
    
    # Always return success to prevent email enumeration
    if not user:
        return {"message": "If the email exists, a reset link has been sent"}
    
    # Generate reset token
    token = generate_reset_token()
    expires_at = datetime.utcnow() + timedelta(hours=24)
    
    # Save reset token
    reset = PasswordReset(
        user_id=user.id,
        token=token,
        expires_at=expires_at
    )
    db.add(reset)
    await db.commit()
    
    # TODO: Send email with reset link
    # For now, just return the token in development mode
    if settings.DEBUG:
        return {
            "message": "Password reset requested",
            "token": token,  # Only in debug mode!
            "expires_at": expires_at.isoformat()
        }
    
    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/password-reset/confirm")
async def confirm_password_reset(
    reset_confirm: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
):
    """Confirm password reset with token"""
    # Find valid reset token
    result = await db.execute(
        select(PasswordReset).where(
            and_(
                PasswordReset.token == reset_confirm.token,
                PasswordReset.used == False,
                PasswordReset.expires_at > datetime.utcnow()
            )
        )
    )
    reset = result.scalar_one_or_none()
    
    if not reset:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Update user password
    result = await db.execute(select(User).where(User.id == reset.user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )
    
    user.password_hash = get_password_hash(reset_confirm.new_password)
    reset.used = True
    
    await db.commit()
    
    return {"message": "Password reset successful"}


# ============== Email Verification ==============

@router.post("/email/verify-request")
async def request_email_verification(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Request email verification"""
    if current_user.email_verified:
        return {"message": "Email already verified"}
    
    # Generate verification token
    token = generate_reset_token()
    expires_at = datetime.utcnow() + timedelta(hours=48)
    
    # Save verification token
    verification = EmailVerification(
        user_id=current_user.id,
        token=token,
        expires_at=expires_at
    )
    db.add(verification)
    await db.commit()
    
    # TODO: Send verification email
    # For now, just return the token in development mode
    if settings.DEBUG:
        return {
            "message": "Verification email sent",
            "token": token,  # Only in debug mode!
            "expires_at": expires_at.isoformat()
        }
    
    return {"message": "Verification email sent"}


@router.get("/email/verify/{token}")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    """Verify email with token"""
    # Find valid verification token
    result = await db.execute(
        select(EmailVerification).where(
            and_(
                EmailVerification.token == token,
                EmailVerification.used == False,
                EmailVerification.expires_at > datetime.utcnow()
            )
        )
    )
    verification = result.scalar_one_or_none()
    
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    # Update user
    result = await db.execute(select(User).where(User.id == verification.user_id))
    user = result.scalar_one_or_none()
    
    if user:
        user.email_verified = True
    
    verification.used = True
    await db.commit()
    
    return {"message": "Email verified successfully"}


# ============== Admin Routes ==============

@router.get("/users", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List all users (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    result = await db.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()
    return users
