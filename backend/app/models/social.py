from sqlalchemy import Column, Integer, String, ForeignKey, DateTime,Text
from ..core.db import Base
from sqlalchemy.orm import relationship
from datetime import datetime






class SocialAccount(Base):
    __tablename__ = "social_accounts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    platform = Column(String)
    access_token = Column(Text)

    user = relationship("User", back_populates="social_accounts")
    posts = relationship("ScheduledPost", back_populates="account")

class ScheduledPost(Base):
    __tablename__ = "scheduled_posts"

    id = Column(Integer, primary_key=True)
    social_account_id = Column(Integer, ForeignKey("social_accounts.id"))
    chat_id = Column(String)
    type = Column(String)
    content = Column(Text)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    account = relationship("SocialAccount", back_populates="posts")
