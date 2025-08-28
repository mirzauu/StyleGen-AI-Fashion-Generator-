from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class ModelImage(Base):
    __tablename__ = 'model_images'

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey('models.id'), nullable=False)
    url = Column(String, nullable=False)
    pose_label = Column(String, nullable=False)

    model = relationship("Model", back_populates="model_images")  # ✅ CORRECT