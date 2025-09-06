from sqlalchemy import Column, Integer, String
from app.database import Base
from sqlalchemy.orm import relationship

class Model(Base):
    __tablename__ = 'models'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    user_id = Column(Integer, default=0)

    images = relationship("GeneratedImage", back_populates="model")
    model_images = relationship("ModelImage", back_populates="model")
    tasks = relationship("Task", back_populates="model")