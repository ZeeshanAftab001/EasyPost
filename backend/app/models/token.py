from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime,Text
from sqlalchemy.sql import func
from ..core.db import Base
from sqlalchemy.orm import relationship
from datetime import datetime


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())