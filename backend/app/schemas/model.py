from pydantic import BaseModel
from typing import List, Optional

class ModelBase(BaseModel):
    name: str
    description: Optional[str] = None

class ModelCreate(ModelBase):
    images: List[str] = []

class ModelUpdate(ModelBase):
    pass

class Model(ModelBase):
    id: int
    images: List[str] = []

    class Config:
        orm_mode = True
        from_attributes=True

class ModelResponse(Model):
    pass