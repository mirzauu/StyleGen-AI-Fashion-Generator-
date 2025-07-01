from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Batch(Base):
    __tablename__ = 'batches'

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    garment_image_url = Column(String, nullable=False)
    status = Column(String, default='queued')  # Possible values: queued, processing, done, failed
    created_at = Column(String)  # You may want to use DateTime instead

    task = relationship("Task", back_populates="batches")
    generated_images = relationship("GeneratedImage", back_populates="batch")