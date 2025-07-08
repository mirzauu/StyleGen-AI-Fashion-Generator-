from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.models.model import Model
from app.schemas.model import ModelCreate, ModelResponse
from app.core.config import get_db
from fastapi import Depends
import shutil
import os
from app.models.model_image import ModelImage

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
async def upload_model_images(
    id: int,
    files: list[UploadFile] = File(...),
    pose_labels: list[str] = Form(...),
    db: Session = Depends(get_db)
):
    model = db.query(Model).filter(Model.id == id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    # Directory to save images (ensure this exists or create it)
    save_dir = "uploaded_images"
    os.makedirs(save_dir, exist_ok=True)

    for file, pose_label in zip(files, pose_labels):
        file_location = os.path.join(save_dir, file.filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        # Save to ModelImage table
        model_image = ModelImage(
            model_id=id,
            url=file_location,
            pose_label=pose_label
        )
        db.add(model_image)
    db.commit()
    return {"detail": "Images uploaded successfully"}