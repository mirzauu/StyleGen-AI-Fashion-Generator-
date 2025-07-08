from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TaskCreate(BaseModel):
    model_id: int
    name: str

class TaskBase(BaseModel):
    id: int
    user_id: int
    model_id: int
    name: str
    created_at: Optional[datetime]

    class Config:
        orm_mode = True

class TaskInDB(TaskBase):
    pass

class TaskResponse(TaskBase):
    pass