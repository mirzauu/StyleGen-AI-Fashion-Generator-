from pydantic import BaseModel
from typing import Optional

class GeneratedImageBase(BaseModel):
    output_url: str
    pose_label: str

class GeneratedImageCreate(GeneratedImageBase):
    pass

class GeneratedImage(GeneratedImageBase):
    id: int
    batch_id: int

    class Config:
        orm_mode = True

class GeneratedImageResponse(GeneratedImage):
    pass