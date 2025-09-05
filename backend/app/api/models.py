from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.models.model import Model
from app.schemas.model import ModelCreate, ModelResponse
from app.core.config import get_db
from fastapi import Depends
import shutil
import os
from app.models.model_image import ModelImage
from typing import Optional
import uuid
from cloudinary.uploader import upload
from app.core.cloudinary_config import cloudinary 
router = APIRouter()

@router.get("/", response_model=list[ModelResponse])
def list_models(db: Session = Depends(get_db)):
    models = db.query(Model).all()
    result = []
    for model in models:
        images = [
            img.url
            for img in db.query(ModelImage).filter(ModelImage.model_id == model.id).all()
        ]
        result.append({
            "id": model.id,
            "name": model.name,
            "description": model.description,
            "images": images
        })
    return result

@router.get("/{model_id}", response_model=ModelResponse)
def get_model(model_id: int, db: Session = Depends(get_db)):
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model

import logging

# Configure logging (so logs show up in uvicorn terminal)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn")

@router.post("/", response_model=dict)
async def create_model(
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    # Create the model entry
    random_name = f"Model-{uuid.uuid4().hex[:8]}"
    random_description = f"Auto-generated model {uuid.uuid4().hex[:6]}"

    new_model = Model(name=random_name, description=random_description)
    db.add(new_model)
    db.commit()
    db.refresh(new_model)

    logger.info(f"📂 Received {len(files)} file(s)")

    if files:
        for file in files:
            logger.info(f"📂 File: {file.filename} | ContentType: {file.content_type}")

            # ✅ Upload directly to Cloudinary
            upload_result = upload(
                file.file,
                folder="my_project_uploads"  # Cloudinary folder name
            )

            # ✅ Save Cloudinary URL in DB
            model_image = ModelImage(
                model_id=new_model.id,
                url=upload_result["secure_url"],
                pose_label="pose_label"
            )
            db.add(model_image)

        db.commit()

    logger.info(f"✅ Model {new_model.id} created successfully with {len(files)} file(s)")

    return {"model_id": new_model.id}



@router.post("/create_with_images", response_model=ModelResponse)
async def create_model_with_images(
    model_id: Optional[str] = Form(None),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    files: Optional[list[UploadFile]] = File(None),
    pose_labels: str = Form(...),
    db: Session = Depends(get_db)
):
    # Convert model_id to int if it's a digit, else None
    if model_id is not None and model_id != "" and model_id.isdigit():
        model_id = int(model_id)
    else:
        model_id = None

    # If model_id is given, fetch the model
    if model_id is not None:
        model = db.query(Model).filter(Model.id == model_id).first()
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        new_model = model
    else:
        if not name or not description:
            raise HTTPException(status_code=400, detail="Name and description are required to create a new model.")
        new_model = Model(name=name, description=description)
        db.add(new_model)
        db.commit()
        db.refresh(new_model)

    save_dir = "uploaded_images"
    os.makedirs(save_dir, exist_ok=True)

    if files:
        for file in files:
            if not isinstance(file, UploadFile):
                continue  # skip invalid files
            file_location = os.path.join(save_dir, file.filename)
            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            model_image = ModelImage(
                model_id=new_model.id,
                url=file_location,
                pose_label=pose_labels
            )
            db.add(model_image)
        db.commit()

    return ModelResponse(
        id=new_model.id,
        name=new_model.name,
        description=new_model.description,
        images=[img.url for img in db.query(ModelImage).filter(ModelImage.model_id == new_model.id).all()]
    )