from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from sqlalchemy.orm import Session
from app.models import Batch, GeneratedImage,GarmentImage
from app.schemas import BatchCreate, BatchResponse
from app.workers.image_tasks import generate_images_task
from app.core.config import get_db
import os
import shutil
from datetime import datetime
from typing import List
from fastapi import Body
import base64
import uuid
from pathlib import Path
from fastapi import Request, UploadFile
from sqlalchemy.orm import Session
from pydantic import BaseModel

router = APIRouter()

def parse_batch_datetime(batch):
    # Defensive: handle None and already-datetime
    created_at = batch.created_at
    if created_at is None:
        dt = datetime.utcnow()  # Use current time if missing
    elif isinstance(created_at, datetime):
        dt = created_at
    else:
        try:
            dt = datetime.fromisoformat(created_at)
        except Exception:
            dt = datetime.utcnow()  # Fallback to now if parsing fails
    # Build dict for Pydantic
    batch_dict = batch.__dict__.copy()
    batch_dict["created_at"] = dt
    return batch_dict


@router.post("/", response_model=BatchResponse)
async def create_batch(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    
    # Get task_id from frontend
    task_id = int(form.get("task_id"))

    # Get the first file from 'files'
    upload_files = form.getlist("files")
    if not upload_files:
        raise HTTPException(status_code=400, detail="No file uploaded")
    file: UploadFile = upload_files[0]

    # Save garment image
    garment_image_url = await save_garment_image(file)

    # Create batch
    new_batch = Batch(
    task_id=task_id,
    status="queued",
    created_at=datetime.utcnow().isoformat()
)

    # Create related garment image
    garment_image = GarmentImage(
        image_url=garment_image_url
    )

    # Attach garment image to batch
    new_batch.garment_images.append(garment_image)

    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)
    # Trigger Celery task
    generate_images_task(new_batch.id, ["front", "side", "back"])

    return BatchResponse.model_validate(parse_batch_datetime(new_batch))

@router.get("/{batch_id}", response_model=BatchResponse)
def get_batch(batch_id: int, db: Session = Depends(get_db)):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return BatchResponse.model_validate(parse_batch_datetime(batch))

from app.models import Batch, GeneratedImage
from app.schemas import BatchResponse
from fastapi import UploadFile, File, Form
from typing import List
@router.post("/dummy_create_batch/", response_model=List[BatchResponse])
async def dummy_create_batch(
    task_id: int = Form(...),
    files: List[UploadFile] = File(...),         # Multiple garment images
    dummy_image: UploadFile = File(...),         # Dummy generated image
    db: Session = Depends(get_db)
):
    save_dir = "uploaded_garments"
    os.makedirs(save_dir, exist_ok=True)
    batch_responses = []

    # Save dummy generated image once
    dummy_image_path = os.path.join(save_dir, f"dummy_{dummy_image.filename}")
    with open(dummy_image_path, "wb") as buffer:
        shutil.copyfileobj(dummy_image.file, buffer)

    # Create one batch per request
    new_batch = Batch(
        task_id=task_id,
        status="done",  # dummy generation, so mark as done
        created_at=datetime.utcnow()
    )
    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)

    for file in files:
        # Save garment image
        garment_image_path = os.path.join(save_dir, file.filename)
        with open(garment_image_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Create garment image entry
        garment_image = GarmentImage(
            batch_id=new_batch.id,
            image_url=garment_image_path
        )
        db.add(garment_image)
        db.commit()
        db.refresh(garment_image)

        # Create dummy generated images for each garment image
        for i in range(2):
            gen_img = GeneratedImage(
                garment_image_id=garment_image.id,
                model_id=1,  # Replace this with the actual model_id if needed
                output_url=garment_image_path,
                pose_label=f"dummy_{i + 1}"
            )
            db.add(gen_img)

    db.commit()
    batch_responses.append(BatchResponse.model_validate(parse_batch_datetime(new_batch)))

    return batch_responses


async def save_garment_image(file: UploadFile):
    save_dir = "uploaded_garments"
    os.makedirs(save_dir, exist_ok=True)
    file_location = os.path.join(save_dir, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return file_location  # Or return a URL if serving files via HTTP