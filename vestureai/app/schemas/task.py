from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TaskCreate(BaseModel):
    model_id: int
    name: str

class Task(TaskCreate):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class TaskInDB(Task):
    pass

class TaskResponse(Task):
    pass