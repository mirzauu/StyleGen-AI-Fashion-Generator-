from pydantic import BaseModel

class ModelImageBase(BaseModel):
    model_id: int
    url: str
    pose_label: str

class ModelImageCreate(ModelImageBase):
    pass

class ModelImage(ModelImageBase):
    id: int

    class Config:
        orm_mode = True

class ModelImageResponse(ModelImage):
    pass