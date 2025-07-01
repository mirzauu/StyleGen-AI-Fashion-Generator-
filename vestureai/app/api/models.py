from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from app.models.model import Model
from app.schemas.model import ModelCreate, ModelResponse
from app.core.config import get_db
from fastapi import Depends

router = APIRouter()

@router.get("/", response_model=list[ModelResponse])
def list_models(db: Session = Depends(get_db)):
    return db.query(Model).all()

@router.get("/{model_id}", response_model=ModelResponse)
def get_model(model_id: int, db: Session = Depends(get_db)):
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model

@router.post("/", response_model=ModelResponse)
def create_model(model: ModelCreate, db: Session = Depends(get_db)):
    new_model = Model(**model.dict())
    db.add(new_model)
    db.commit()
    db.refresh(new_model)
    return new_model

@router.post("/{id}/images", response_model=None)
def upload_model_images(id: int, images: list[str], db: Session = Depends(get_db)):
    model = db.query(Model).filter(Model.id == id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    # Logic to handle image uploads would go here
    return {"detail": "Images uploaded successfully"}