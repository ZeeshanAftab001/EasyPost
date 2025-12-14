from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime,Text
from ..db import Base
from sqlalchemy.orm import relationship



class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    tenant_id = Column(Integer)
    whatsapp_number = Column(String, unique=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    chats = relationship("ChatSession", back_populates="user")
    social_accounts = relationship("SocialAccount", back_populates="user")