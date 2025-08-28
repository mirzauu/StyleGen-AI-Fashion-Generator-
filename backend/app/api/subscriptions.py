from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.subscription import Subscription
from app.schemas.subscription import SubscriptionCreate, SubscriptionOut
from app.core.auth import get_current_user
from app.core.config import get_db
from app.services.billing import BillingService
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=list[SubscriptionOut])
def get_subscriptions(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    subscriptions = db.query(Subscription).filter(Subscription.user_id == current_user.id).all()
    return subscriptions

@router.post("/checkout", response_model=dict)
def checkout(subscription: SubscriptionCreate, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    billing_service = BillingService(db)
    session = billing_service.create_checkout_session(current_user.id, subscription.plan_id)
    return {"url": session.url}

# @router.post("/webhook")
# def webhook(request: Request):
#     payload = await request.body()
#     event = handle_webhook(payload)
#     return {"status": "success"}


@router.post("/", response_model=SubscriptionOut)
def create_subscription(
    subscription: SubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    # Create new subscription
    new_subscription = Subscription(
        user_id=current_user.id,
        plan_id=subscription.plan_id,
        status="active",  # default status
        current_period_end=datetime.utcnow()  # could set trial/end date
    )

    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)

    return new_subscription
