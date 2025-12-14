from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from typing import Tuple
import secrets

# Configuration
SECRET_KEY = "your-secret-key-change-this-in-production"
REFRESH_SECRET_KEY = "your-refresh-secret-key-different-from-main"  # NEW
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7  # NEW

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Access Token (short-lived)
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "type": "access"  # NEW: Token type
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# NEW: Refresh Token (long-lived)
def create_refresh_token(user_id: int) -> Tuple[str, datetime]:
    """Create a refresh token and return (token, expiry_datetime)"""
    # Generate random token
    token = secrets.token_urlsafe(64)
    expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    # You could also JWT encode it, but we'll use random string for database storage
    return token, expires_at

# NEW: Validate refresh token
def validate_refresh_token(refresh_token: str, db_token: dict) -> bool:
    """
    Validate refresh token against database record
    Returns True if token is valid
    """
    # Check if token exists in database
    if not db_token:
        return False
    
    # Check if token matches
    if refresh_token != db_token["token"]:
        return False
    
    # Check if token is revoked
    if db_token.get("is_revoked", False):
        return False
    
    # Check if token is expired
    if datetime.utcnow() > db_token["expires_at"]:
        return False
    
    return True

# NEW: Create both tokens
def create_tokens(user_id: int, username: str) -> dict:
    """Create both access and refresh tokens"""
    # Access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username, "user_id": user_id},
        expires_delta=access_token_expires
    )
    
    # Refresh token
    refresh_token, refresh_expiry = create_refresh_token(user_id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "refresh_token_expiry": refresh_expiry,
        "access_token_expiry": datetime.utcnow() + access_token_expires
    }