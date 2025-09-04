from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    token_balance = Column(Integer, default=0)
    token_valid_until = Column(DateTime, default=None, nullable=True)
    
    
    subscriptions = relationship("Subscription", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    tasks = relationship("Task", back_populates="user")
    token_history = relationship("TokenHistory", backref="user")

class TokenHistory(Base):
    __tablename__ = "token_history"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    change = Column(Integer)
    source = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    validity_extension = Column(Integer, default=0)
