# app/api/__init__.py

from fastapi import APIRouter

router = APIRouter()

from . import auth, plans, subscriptions, models, tasks, batches

router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(plans.router, prefix="/plans", tags=["plans"])
router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
router.include_router(models.router, prefix="/models", tags=["models"])
router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
router.include_router(batches.router, prefix="/batches", tags=["batches"])