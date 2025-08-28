from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BatchCreate(BaseModel):
    task_id: int

class Batch(BaseModel):
    id: int
    task_id: int
    status: str
    created_at: datetime

    class Config:
        orm_mode = True

class BatchStatus(BaseModel):
    status: str

class BatchOutput(BaseModel):
    id: int
    output_url: str
    pose_label: str

    class Config:
        orm_mode = True

class BatchResponse(Batch):
    class Config:
        from_attributes = True  # <-- for Pydantic v2+