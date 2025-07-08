from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from sqlalchemy.orm import Session
from app.models import Batch, GeneratedImage
from app.schemas import BatchCreate, BatchResponse
from app.workers.image_tasks import generate_images_task
from app.core.config import get_db
import os
import shutil
from datetime import datetime

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
async def create_batch(
        task_id: int = Form(...),
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
    ):
    # Save the garment image to storage and get the URL
    garment_image_url = await save_garment_image(file)

    # Create a new batch entry in the database
    new_batch = Batch(task_id=task_id, garment_image_url=garment_image_url, status="queued")
    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)

    # Trigger Celery task here
    generate_images_task(new_batch.id, ["front", "side", "back"])

    return BatchResponse.model_validate(parse_batch_datetime(new_batch))

@router.get("/{batch_id}", response_model=BatchResponse)
def get_batch(batch_id: int, db: Session = Depends(get_db)):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return BatchResponse.model_validate(parse_batch_datetime(batch))

async def save_garment_image(file: UploadFile):
    save_dir = "uploaded_garments"
    os.makedirs(save_dir, exist_ok=True)
    file_location = os.path.join(save_dir, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return file_location  # Or return a URL if serving files via HTTP