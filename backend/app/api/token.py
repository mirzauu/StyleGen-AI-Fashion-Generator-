# app/routers/tokens.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.token import TokenService, get_token_service
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/tokens", tags=["tokens"])

@router.get("/balance")
async def get_balance(
    current_user: User = Depends(get_current_user),
    token_service: TokenService = Depends(get_token_service)
):
    """Get user's token balance and plan limit"""
    return token_service.get_token_balance_with_plan_limit(current_user.id)

@router.post("/consume")
async def consume_tokens(
    tokens_to_consume: int,
    current_user: User = Depends(get_current_user),
    token_service: TokenService = Depends(get_token_service)
):
    """Consume user's tokens"""
    return token_service.consume_tokens(current_user.id, tokens_to_consume)

@router.get("/history")
async def get_token_history(
    current_user: User = Depends(get_current_user),
    token_service: TokenService = Depends(get_token_service)
):
    """Get user's token history"""
    return token_service.get_token_history(current_user.id)
