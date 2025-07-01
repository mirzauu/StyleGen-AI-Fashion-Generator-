from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy.sql import func
from sqlalchemy import DateTime

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    model_id = Column(Integer, ForeignKey('models.id'))
    name = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
   
    user = relationship("User", back_populates="tasks")
    model = relationship("Model", back_populates="tasks")
    batches = relationship("Batch", back_populates="task")