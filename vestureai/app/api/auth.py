from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.auth import get_current_user, create_user, authenticate_user
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.core.config import get_db

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = create_user(user, db)  # <-- Fix argument order
    if db_user is None:
        raise HTTPException(status_code=400, detail="User already exists")
    return db_user

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, user.email, user.password)
    if db_user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    from app.core.auth import create_access_token
    access_token = create_access_token(
        data={"sub": db_user.email}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user