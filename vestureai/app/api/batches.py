from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models import Batch, GeneratedImage
from app.schemas import BatchCreate, BatchResponse
from app.workers.image_tasks import generate_images_task
from app.core.config import get_db

router = APIRouter()

@router.post("/", response_model=BatchResponse)
async def create_batch(batch: BatchCreate, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Save the garment image to storage and get the URL
    garment_image_url = await save_garment_image(file)

    # Create a new batch entry in the database
    new_batch = Batch(task_id=batch.task_id, garment_image_url=garment_image_url, status="queued")
    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)

    # Trigger Celery task here
    generate_images_task(new_batch.id, ["front", "side", "back"])

    return BatchResponse.model_validate(new_batch)

@router.get("/{batch_id}", response_model=BatchResponse)
def get_batch(batch_id: int, db: Session = Depends(get_db)):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return BatchResponse.model_validate(batch)

async def save_garment_image(file: UploadFile):
    # Logic to save the garment image to S3/MinIO and return the URL
    pass