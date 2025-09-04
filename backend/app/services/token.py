# app/services/token.py
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from fastapi import APIRouter, Depends, HTTPException, Request
from app.models.user import TokenHistory
from app.models import User, Subscription, Plan
from app.core.config import get_db



class TokenService:
    """Service class for managing user token operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_token_balance(self, user_id: int) -> dict:
        """Get user's current token balance and validity"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "user_id": user_id,
            "token_balance": user.token_balance or 0,
            "token_valid_until": user.token_valid_until,
            "is_valid": self._is_token_valid(user.token_valid_until)
        }
    
    def add_tokens(self, user_id: int, tokens_to_add: int, source: str = "purchase", 
                   validity_days: int = 30) -> dict:
        """Add tokens to user's balance and extend validity"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Add tokens to balance
        user.token_balance = (user.token_balance or 0) + tokens_to_add
        
        # Extend validity
        new_validity = self._calculate_new_validity(user.token_valid_until, validity_days)
        user.token_valid_until = new_validity
        
        # Record in history
        self._record_token_history(
            user_id=user_id,
            change=tokens_to_add,
            source=source,
            validity_extension=validity_days
        )
        
        self.db.commit()
        self.db.refresh(user)
        
        return {
            "user_id": user_id,
            "tokens_added": tokens_to_add,
            "new_balance": user.token_balance,
            "new_validity": user.token_valid_until,
            "source": source
        }
    
    def consume_tokens(self, user_id: int, tokens_to_consume: int, 
                      source: str = "usage") -> dict:
        """Deduct tokens from user's balance"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if user has enough tokens
        current_balance = user.token_balance or 0
        if current_balance < tokens_to_consume:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient tokens. Current balance: {current_balance}, Required: {tokens_to_consume}"
            )
        
        # Check if tokens are still valid
        if not self._is_token_valid(user.token_valid_until):
            raise HTTPException(status_code=400, detail="Tokens have expired")
        
        # Deduct tokens
        user.token_balance = current_balance - tokens_to_consume
        
        # Record in history
        self._record_token_history(
            user_id=user_id,
            change=-tokens_to_consume,
            source=source
        )
        
        self.db.commit()
        self.db.refresh(user)
        
        return {
            "user_id": user_id,
            "tokens_consumed": tokens_to_consume,
            "remaining_balance": user.token_balance,
            "source": source
        }
    
    def get_token_balance_with_plan_limit(self, user_id: int) -> dict:
        """Get user's token balance along with their plan's token limit"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get active subscription
        active_subscription = self.db.query(Subscription).filter(
            and_(
                Subscription.user_id == user_id,
                Subscription.status == "active",
                Subscription.current_period_end > datetime.utcnow()
            )
        ).first()
        
        plan_limit = 0
        plan_name = "No Plan"
        
        if active_subscription and active_subscription.plan:
            plan = active_subscription.plan
            plan_limit = plan.limits.get("token_limit", 0) if plan.limits else 0
            plan_name = plan.name
        
        return {
            "user_id": user_id,
            "token_balance": user.token_balance or 0,
            "plan_token_limit": plan_limit,
            "plan_name": plan_name,
            "usage_percentage": round((user.token_balance or 0) / plan_limit * 100, 2) if plan_limit > 0 else 0,
            "token_valid_until": user.token_valid_until,
            "is_valid": self._is_token_valid(user.token_valid_until)
        }
    
    def allocate_tokens_from_plan(self, user_id: int, subscription_id: int) -> dict:
        """Allocate tokens to user based on purchased plan"""
        subscription = self.db.query(Subscription).filter(
            and_(
                Subscription.id == subscription_id,
                Subscription.user_id == user_id
            )
        ).first()
        
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        plan = subscription.plan
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        # Get token allocation from plan limits
        token_allocation = plan.limits.get("token_allocation", 0) if plan.limits else 0
        validity_days = plan.limits.get("validity_days", 30) if plan.limits else 30
        
        if token_allocation <= 0:
            raise HTTPException(status_code=400, detail="Plan has no token allocation")
        
        # Add tokens to user
        return self.add_tokens(
            user_id=user_id,
            tokens_to_add=token_allocation,
            source=f"plan_purchase_{plan.name}",
            validity_days=validity_days
        )
    
    def get_token_history(self, user_id: int, limit: int = 50) -> list:
        """Get user's token history"""
        history = self.db.query(TokenHistory).filter(
            TokenHistory.user_id == user_id
        ).order_by(TokenHistory.timestamp.desc()).limit(limit).all()
        
        return [
            {
                "id": record.id,
                "change": record.change,
                "source": record.source,
                "timestamp": record.timestamp,
                "validity_extension": record.validity_extension
            }
            for record in history
        ]
    
    def check_token_availability(self, user_id: int, required_tokens: int) -> dict:
        """Check if user has enough valid tokens for an operation"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        current_balance = user.token_balance or 0
        is_valid = self._is_token_valid(user.token_valid_until)
        
        return {
            "user_id": user_id,
            "current_balance": current_balance,
            "required_tokens": required_tokens,
            "has_sufficient_tokens": current_balance >= required_tokens,
            "tokens_valid": is_valid,
            "can_proceed": current_balance >= required_tokens and is_valid,
            "token_valid_until": user.token_valid_until
        }
    
    def _is_token_valid(self, valid_until: Optional[datetime]) -> bool:
        """Check if tokens are still valid"""
        if not valid_until:
            return False
        return datetime.utcnow() < valid_until
    
    def _calculate_new_validity(self, current_validity: Optional[datetime], 
                               days_to_add: int) -> datetime:
        """Calculate new token validity date"""
        if not current_validity or current_validity < datetime.utcnow():
            # If no current validity or expired, start from now
            return datetime.utcnow() + timedelta(days=days_to_add)
        else:
            # Extend current validity
            return current_validity + timedelta(days=days_to_add)
    
    def _record_token_history(self, user_id: int, change: int, source: str, 
                             validity_extension: int = 0):
        """Record token transaction in history"""
        history_record = TokenHistory(
            user_id=user_id,
            change=change,
            source=source,
            validity_extension=validity_extension
        )
        self.db.add(history_record)


# Dependency to get TokenService instance
def get_token_service(db: Session = Depends(get_db)) -> TokenService:
    return TokenService(db)
