from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from sqlalchemy.orm import Session
from app.models import Batch, GeneratedImage,GarmentImage
from app.models.subscription import Subscription
from app.models.task import Task
from app.schemas import BatchCreate, BatchResponse
from app.workers.image_tasks import generate_images_task
from app.core.config import get_db
import os
import shutil
from datetime import datetime
from app.core.auth import get_current_user
from app.models.user import User
from typing import List
from fastapi import Body
import base64
import uuid
from pathlib import Path
from fastapi import Request, UploadFile
from sqlalchemy.orm import Session
from pydantic import BaseModel
from cloudinary.uploader import upload
from app.core.cloudinary_config import cloudinary
from fastapi.responses import StreamingResponse
import io
import zipfile
import requests

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



# Update the create_batch function
@router.post("/", response_model=BatchResponse)
async def create_batch(request: Request, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    form = await request.form()
    
     # Get task_id from frontend
    if current_user.token_balance <= 0:
        raise HTTPException(status_code=403, detail="Your token balance is zero or below. Please purchase a plan to continue using this service.")

    # Get task_id from frontend
    task_id = int(form.get("task_id"))

    # Validate user's subscription status via task -> user
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    # subscription = (
    #     db.query(Subscription)
    #     .filter(Subscription.user_id == task.user_id)
    #     .order_by(Subscription.current_period_end.desc())
    #     .first()
    # )
    # if subscription is None or (subscription.status or "").lower() != "active":
    #     raise HTTPException(status_code=402, detail="Upgrade to pro plan")

    # Get model images count from task's model
    model_images_count = 0
    if task.model and task.model.model_images:
        model_images_count = len(task.model.model_images)
    
    if model_images_count == 0:
        raise HTTPException(status_code=400, detail="No model images found for this task's model")

    # Get all files from 'files'
    upload_files = form.getlist("files")
    if not upload_files:
        raise HTTPException(status_code=400, detail="No file uploaded")

    # Calculate required tokens: number of garment images × number of model images
    required_tokens = len(upload_files) * model_images_count
    
    # Check if user has enough tokens
    if current_user.token_balance < required_tokens:
        raise HTTPException(
            status_code=403, 
            detail=f"Insufficient tokens. Required: {required_tokens}, Available: {current_user.token_balance}"
        )

    # Create batch first
    new_batch = Batch(
        task_id=task_id,
        status="queued",
        created_at=datetime.utcnow().isoformat()
    )

    # Save each garment image as a separate record linked to the same batch
    for file in upload_files:
        garment_image_url = await save_garment_image(file)
        garment_image = GarmentImage(
            image_url=garment_image_url
        )
        new_batch.garment_images.append(garment_image)

    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)

    generate_images_task(new_batch.id,current_user.id)

    return BatchResponse.model_validate(parse_batch_datetime(new_batch))

  

@router.get("/{batch_id}", response_model=BatchResponse)
def get_batch(batch_id: int, db: Session = Depends(get_db)):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return BatchResponse.model_validate(parse_batch_datetime(batch))

@router.get("/{batch_id}/download")
def download_batch_zip(batch_id: int, db: Session = Depends(get_db)):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    # Collect all generated image URLs for the batch
    image_urls: List[str] = []
    for garment in batch.garment_images:
        for gen in garment.generated_images:
            if gen.output_url:
                image_urls.append(gen.output_url)

    if not image_urls:
        raise HTTPException(status_code=404, detail="No generated images found for this batch")

    def iter_zip():
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for idx, url in enumerate(image_urls, start=1):
                try:
                    # Stream each image from its URL
                    resp = requests.get(url, stream=True, timeout=20)
                    resp.raise_for_status()
                    # Guess extension from URL path
                    ext = ".jpg"
                    path_lower = url.split("?")[0].lower()
                    if path_lower.endswith((".png", ".jpeg", ".jpg", ".webp")):
                        for candidate in [".png", ".jpeg", ".jpg", ".webp"]:
                            if path_lower.endswith(candidate):
                                ext = candidate
                                break
                    filename = f"image_{idx}{ext}"
                    # Read content fully into memory for writing into zip
                    content = resp.content
                    zf.writestr(filename, content)
                except Exception:
                    # Skip failed downloads silently
                    continue
        zf.close()
        buffer.seek(0)
        yield from buffer

    headers = {
        "Content-Disposition": f"attachment; filename=batch_{batch_id}.zip"
    }
    return StreamingResponse(iter_zip(), media_type="application/zip", headers=headers)

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
    # Upload directly to Cloudinary
    upload_result = upload(
        file.file,
        folder="my_project_uploads/garments"  # Cloudinary folder name
    )
    
    # Return the secure URL from Cloudinary
    return upload_result["secure_url"]