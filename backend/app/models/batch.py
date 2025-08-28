from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Batch(Base):
    __tablename__ = 'batches'

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    status = Column(String, default='queued')  # queued, processing, done, failed
    created_at = Column(String)  # You may want to use DateTime instead


    task = relationship("Task", back_populates="batches")
    garment_images = relationship("GarmentImage", back_populates="batch")


class GarmentImage(Base):
    __tablename__ = 'garment_images'

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey('batches.id'), nullable=False)
    image_url = Column(String, nullable=False)

    batch = relationship("Batch", back_populates="garment_images")
    generated_images = relationship("GeneratedImage", back_populates="garment_image")