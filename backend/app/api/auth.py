from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.auth import get_current_user, create_user, authenticate_user, create_password_reset_token, verify_password_reset_token, send_password_reset_email
from app.schemas.user import UserCreate, UserLogin, UserResponse, PasswordResetRequest, PasswordReset
from app.core.config import get_db
from app.models.subscription import Subscription
from app.models.user import User
from app.core.utils import hash_password

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

@router.post("/forgot-password")
def request_password_reset(request: Request, reset_request: PasswordResetRequest, db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(User).filter(User.email == reset_request.email).first()
    if not user:
        
        return {"message": "If your email is registered, you will receive a password reset link"}
    
    # Generate JWT token
    reset_token = create_password_reset_token(user.email)
    
    # Get base URL from request
    base_url = 'app.trylo.space'
    
    # Send email with reset link
    email_sent = send_password_reset_email(user.email, reset_token, base_url)
    
    if not email_sent:
        raise HTTPException(status_code=500, detail="Failed to send password reset email")
    
    return {"message": "If your email is registered, you will receive a password reset link"}

@router.post("/reset-password")
def reset_password(reset_data: PasswordReset, db: Session = Depends(get_db)):
    # Verify token and get user
    user = verify_password_reset_token(reset_data.token, db)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    # Update password
    user.password_hash = hash_password(reset_data.password)
    db.commit()
    
    return {"message": "Password has been reset successfully"}