from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime,Text
from sqlalchemy.sql import func
from ..core.db import Base
from sqlalchemy.orm import relationship
from datetime import datetime


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True)
    tenant_id = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chats")
    memories = relationship("ChatMemory", back_populates="chat")

class ChatMemory(Base):
    __tablename__ = "chat_memories"

    id = Column(Integer, primary_key=True)
    chat_id = Column(String, ForeignKey("chat_sessions.id"))
    role = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    chat = relationship("ChatSession", back_populates="memories")