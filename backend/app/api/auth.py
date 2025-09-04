from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.auth import get_current_user, create_user, authenticate_user
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.core.config import get_db
from app.models.subscription import Subscription

router = APIRouter()

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = create_user(user, db)  # <-- Fix argument order
    if db_user is None:
        raise HTTPException(status_code=400, detail="User already exists")
    from app.core.auth import create_access_token
    access_token = create_access_token(
        data={"sub": db_user.email}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, user.email, user.password)
    if db_user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    from app.core.auth import create_access_token
    access_token = create_access_token(
        data={"sub": db_user.email}
    )
    subscription = (
        db.query(Subscription)
        .filter(Subscription.user_id == db_user.id)
        .order_by(Subscription.current_period_end.desc())
        .first()
    )
    subscription_status = subscription.status if subscription else None
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "subscription_status": subscription_status
    }

from fastapi.security import OAuth2PasswordRequestForm

@router.post("/token")
def login_for_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    from app.core.auth import create_access_token
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
def read_users_me(db: Session = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    subscription = (
        db.query(Subscription)
        .filter(Subscription.user_id == current_user.id)
        .order_by(Subscription.current_period_end.desc())
        .first()
    )
    subscription_status = subscription.status if subscription else None
    return {
        "email": current_user.email,
        "subscription_status": subscription_status,
    }