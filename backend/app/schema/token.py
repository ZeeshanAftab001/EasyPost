from pydantic import BaseModel
from datetime import datetime

# Token schemas (UPDATED)
class Token(BaseModel):
    access_token: str
    refresh_token: str  # NEW: Added refresh token
    token_type: str = "bearer"
    expires_in: int  # Access token expiry in seconds

class TokenRefresh(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

# For frontend storage
class TokensStore(BaseModel):
    access_token: str
    refresh_token: str
    access_token_expiry: datetime

# Login schema
class LoginRequest(BaseModel):
    username: str
    password: str