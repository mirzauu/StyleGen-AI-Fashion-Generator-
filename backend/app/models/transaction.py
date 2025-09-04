from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    # Associations
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id"), index=True, nullable=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), index=True, nullable=True)

    # Payment identifiers
    merchant_order_id = Column(String, index=True, nullable=False)
    gateway_transaction_id = Column(String, index=True, nullable=True)

    # Financials
    amount_paise = Column(Integer, nullable=False)
    currency = Column(String, default="INR", nullable=False)

    # Status and mode
    status = Column(String, index=True, nullable=False)  # e.g., PENDING, COMPLETED, FAILED
    payment_mode = Column(String, nullable=True)  # e.g., NET_BANKING, CARD

    # Raw gateway payloads for audit/debug
    request_payload = Column(JSON, nullable=True)
    response_payload = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="transactions")
    plan = relationship("Plan", back_populates="transactions")
    subscription = relationship("Subscription", back_populates="transactions")


