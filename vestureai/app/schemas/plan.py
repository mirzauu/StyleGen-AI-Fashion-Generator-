from pydantic import BaseModel
from typing import List, Optional

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