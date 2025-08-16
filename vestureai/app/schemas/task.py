from pydantic import BaseModel
from datetime import datetime
from typing import Optional,List

class TaskCreate(BaseModel):
    model_id: int
    name: str
    Discription: Optional[str] = None
    pose: str

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

class TaskResponse(BaseModel):
    id: int
    user_id: int
    model_id: int
    name: str
    created_at: Optional[datetime]
    model_images: List[str] = []
   

    class Config:
        orm_mode = True
        from_attributes = True

class TaskRespons(BaseModel):
    id: int
    user_id: int
    model_id: int
    name: str
    created_at: Optional[datetime]
    model_images: List[str] = []

    class Config:
        orm_mode = True
        from_attributes = True