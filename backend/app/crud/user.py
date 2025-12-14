from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..schema import user
from ..services import auth
from ..models import user,token

# User CRUD operations (existing)
def get_user(db: Session, user_id: int):
    return db.query(user.User).filter(user.User.id == user_id).first()

def get_users(db: Session):
    return db.query(user.User).all()
def get_user_by_username(db: Session, username: str):
    return db.query(user.User).filter(user.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(user.User).filter(user.User.email == email).first()

def create_user(db: Session, user: user.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = user.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not auth.verify_password(password, user.hashed_password):
        return False
    return user

# NEW: Refresh Token CRUD operations
def create_refresh_token_record(db: Session, user_id: int, token: str, expires_at: datetime):
    """Store refresh token in database"""
    db_token = token.RefreshToken(
        token=token,
        user_id=user_id,
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

def get_refresh_token(db: Session, token: str):
    """Get refresh token from database"""
    return db.query(token.RefreshToken).filter(token.RefreshToken.token == token).first()

def revoke_refresh_token(db: Session, token: str):
    """Mark refresh token as revoked"""
    db_token = get_refresh_token(db, token)
    if db_token:
        db_token.is_revoked = True
        db.commit()
        return True
    return False

def revoke_all_user_tokens(db: Session, user_id: int):
    """Revoke all refresh tokens for a user (on logout/password change)"""
    tokens = db.query(token.RefreshToken).filter(
        token.RefreshToken.user_id == user_id,
        token.RefreshToken.is_revoked == False
    ).all()
    
    for token in tokens:
        token.is_revoked = True
    
    db.commit()
    return len(tokens)

def cleanup_expired_tokens(db: Session):
    """Clean up expired refresh tokens (run periodically)"""
    expired = db.query(token.RefreshToken).filter(
        token.RefreshToken.expires_at < datetime.utcnow()
    ).delete()
    db.commit()
    return expired