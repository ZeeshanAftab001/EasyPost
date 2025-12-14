from fastapi import Depends, HTTPException, status,APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from ..services import auth
from ..schema import user,token
from ..crud import user
from ..core.db import get_db


router=APIRouter()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Dependency to get current user from token
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
        
        user = user.get_user_by_username(db, username=username)
        if user is None:
            raise credentials_exception
        
        return user
        
    except (InvalidTokenError, ExpiredSignatureError):
        raise credentials_exception

def get_current_active_user(current_user: user.UserResponse = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user



@router.post("/register", response_model=user.UserResponse)
def register(user: user.UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = user.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_user = user.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    return user.create_user(db=db, user=user)

@router.post("/login", response_model=token.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Authenticate user
    user = user.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username, "type": "access"},  # Added type field
        expires_delta=access_token_expires
    )
    
    # Create refresh token (simple version without database storage)
    refresh_token_expires = timedelta(days=7)
    refresh_token = auth.create_access_token(
        data={"sub": user.username, "type": "refresh"},
        expires_delta=refresh_token_expires
    )
    
    # Return all required fields
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,  # Added
        "token_type": "bearer",
        "expires_in": auth.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # In seconds
    }


@router.get("/users/me", response_model=user.UserResponse)
def read_users_me(current_user: user.UserResponse = Depends(get_current_active_user)):
    return current_user

@router.get("/users", response_model=list[user.UserResponse])
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: user.UserResponse = Depends(get_current_active_user)
):
    return user.get_users(db)