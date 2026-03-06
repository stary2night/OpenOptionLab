"""
Security utilities
"""
import re
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional

from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def generate_token(length: int = 32) -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(length)


def generate_reset_token() -> str:
    """Generate password reset token"""
    return secrets.token_urlsafe(32)


def generate_verification_token() -> str:
    """Generate email verification token"""
    return secrets.token_urlsafe(32)


def generate_api_key() -> str:
    """Generate API key"""
    return f"opt_{secrets.token_urlsafe(32)}"


def hash_token(token: str) -> str:
    """Hash a token for storage"""
    return hashlib.sha256(token.encode()).hexdigest()


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password strength
    
    Returns:
        (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "密码长度至少为8个字符"
    
    if not re.search(r"[A-Z]", password):
        return False, "密码必须包含至少一个大写字母"
    
    if not re.search(r"[a-z]", password):
        return False, "密码必须包含至少一个小写字母"
    
    if not re.search(r"\d", password):
        return False, "密码必须包含至少一个数字"
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "密码必须包含至少一个特殊字符"
    
    return True, None


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """Validate Chinese phone number"""
    pattern = r'^1[3-9]\d{9}$'
    return re.match(pattern, phone) is not None


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input"""
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    text = re.sub(r'[<>\"\']', '', text)
    
    # Limit length
    return text[:max_length].strip()


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """Mask sensitive data (e.g., phone number, email)"""
    if not data:
        return ""
    
    if len(data) <= visible_chars * 2:
        return "*" * len(data)
    
    return data[:visible_chars] + "*" * (len(data) - visible_chars * 2) + data[-visible_chars:]


def mask_email(email: str) -> str:
    """Mask email address"""
    if not email or "@" not in email:
        return ""
    
    local, domain = email.split("@", 1)
    
    if len(local) <= 2:
        masked_local = "*" * len(local)
    else:
        masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
    
    return f"{masked_local}@{domain}"


def mask_phone(phone: str) -> str:
    """Mask phone number"""
    if not phone or len(phone) != 11:
        return ""
    
    return phone[:3] + "****" + phone[-4:]


def generate_csrf_token() -> str:
    """Generate CSRF token"""
    return secrets.token_urlsafe(32)


def constant_time_compare(val1: str, val2: str) -> bool:
    """Constant time string comparison to prevent timing attacks"""
    return secrets.compare_digest(val1.encode(), val2.encode())


def is_token_expired(created_at: datetime, expires_hours: int = 24) -> bool:
    """Check if token is expired"""
    expiry = created_at + timedelta(hours=expires_hours)
    return datetime.now() > expiry


def generate_secure_id() -> str:
    """Generate secure unique ID"""
    return secrets.token_hex(16)


def hash_ip_address(ip: str) -> str:
    """Hash IP address for privacy"""
    return hashlib.sha256(ip.encode()).hexdigest()[:16]


class RateLimiter:
    """Simple rate limiter using in-memory storage"""
    
    def __init__(self):
        self._storage = {}
    
    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """
        Check if request is allowed under rate limit
        
        Args:
            key: Rate limit key (e.g., IP address)
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
            
        Returns:
            True if request is allowed
        """
        now = datetime.now()
        window_start = now - timedelta(seconds=window_seconds)
        
        # Get existing requests
        requests = self._storage.get(key, [])
        
        # Filter to only include requests in current window
        requests = [r for r in requests if r > window_start]
        
        # Check if under limit
        if len(requests) >= max_requests:
            self._storage[key] = requests
            return False
        
        # Add current request
        requests.append(now)
        self._storage[key] = requests
        
        return True
    
    def get_remaining(self, key: str, max_requests: int, window_seconds: int) -> int:
        """Get remaining requests in current window"""
        now = datetime.now()
        window_start = now - timedelta(seconds=window_seconds)
        
        requests = self._storage.get(key, [])
        requests = [r for r in requests if r > window_start]
        
        return max(0, max_requests - len(requests))


# Global rate limiter instance
rate_limiter = RateLimiter()
