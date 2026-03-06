"""
Authentication Schemas
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator


class Token(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class TokenPayload(BaseModel):
    """Token payload"""
    sub: Optional[str] = None
    exp: Optional[int] = None
    type: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class RegisterRequest(BaseModel):
    """Register request"""
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$')
    email: EmailStr
    password: str = Field(..., min_length=8)
    phone: Optional[str] = Field(None, pattern=r'^1[3-9]\d{9}$')
    
    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not any(c.islower() for c in v):
            raise ValueError('密码必须包含至少一个小写字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含至少一个数字')
        return v


class PasswordResetRequest(BaseModel):
    """Password reset request"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not any(c.islower() for c in v):
            raise ValueError('密码必须包含至少一个小写字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含至少一个数字')
        return v


class PasswordChange(BaseModel):
    """Password change request"""
    current_password: str
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not any(c.islower() for c in v):
            raise ValueError('密码必须包含至少一个小写字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含至少一个数字')
        return v


class ProfileUpdate(BaseModel):
    """Profile update request"""
    phone: Optional[str] = Field(None, pattern=r'^1[3-9]\d{9}$')
    bio: Optional[str] = Field(None, max_length=500)


class EmailVerificationRequest(BaseModel):
    """Email verification request"""
    email: EmailStr


class LogoutRequest(BaseModel):
    """Logout request"""
    refresh_token: Optional[str] = None
