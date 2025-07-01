from sqlalchemy import Column, Integer, String, JSON
from app.database import Base
from sqlalchemy.orm import relationship


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    limits = Column(JSON, nullable=False)


    subscriptions = relationship("Subscription", back_populates="plan")