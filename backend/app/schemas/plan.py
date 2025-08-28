from pydantic import BaseModel
from typing import List, Optional
from typing import Dict

class PlanBase(BaseModel):
    name: str
    price: float
    limits: dict

class PlanCreate(PlanBase):
    pass

class Plan(PlanBase):
    id: int

    class Config:
        orm_mode = True

class PlanList(BaseModel):
    plans: List[Plan]

class PlanResponse(Plan):
    pass

class PlanCreate(BaseModel):
    name: str
    price: int
    limits: Dict  # because your SQLAlchemy model uses JSON

class PlanResponse(BaseModel):
    id: int
    name: str
    price: int
    limits: Dict

    class Config:
        orm_mode = True