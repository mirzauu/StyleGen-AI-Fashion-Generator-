from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class GeneratedImage(Base):
    __tablename__ = 'generated_images'

    id = Column(Integer, primary_key=True, index=True)
    garment_image_id = Column(Integer, ForeignKey('garment_images.id'), nullable=False)
    model_id = Column(Integer, ForeignKey('models.id'), nullable=False)
    output_url = Column(String, nullable=False)
    pose_label = Column(String, nullable=False)

    garment_image = relationship("GarmentImage", back_populates="generated_images")
    model = relationship("Model", back_populates="images")