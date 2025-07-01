from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from app.models.plan import Plan
from app.schemas.plan import PlanResponse
from app.core.config import get_db
from fastapi import Depends

router = APIRouter()

@router.get("/", response_model=list[PlanResponse])
def get_plans(db: Session = Depends(get_db)):
    plans = db.query(Plan).all()
    return plans
    
@router.get("/{plan_id}", response_model=PlanResponse)
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan