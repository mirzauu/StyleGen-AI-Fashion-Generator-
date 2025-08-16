from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models import Task, Batch
from app.schemas import TaskCreate, TaskResponse, BatchCreate, TaskRespons
from app.core.config import get_db
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=TaskResponse)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_task = Task(
        user_id=current_user.id,
        model_id=task.model_id,
        name=task.name,
        description=task.Discription,  # From input schema
        pose=task.pose
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task
@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# @router.post("/{task_id}/batches/", response_model=Batch)
# def create_batch(task_id: int, batch: BatchCreate, db: Session = Depends(get_db)):
#     db_batch = Batch(**batch.dict(), task_id=task_id)
#     db.add(db_batch)
#     db.commit()
#     db.refresh(db_batch)
#     return db_batch

@router.get("/{task_id}/batches/")
def get_batches(task_id: int, db: Session = Depends(get_db)):
    batches = db.query(Batch).filter(Batch.task_id == task_id).all()

    response = []

    for batch in batches:
        batch_data = {
            "batch_id": batch.id,
            "status": batch.status,
            "created_at": batch.created_at,
            "garment_images": []
        }

        for garment in batch.garment_images:
            garment_data = {
                "garment_image_id": garment.id,
                "image_url": garment.image_url,
                "generated_images": []
            }

            for gen_img in garment.generated_images:
                garment_data["generated_images"].append({
                    "generated_image_id": gen_img.id,
                    "output_url": gen_img.output_url,
                    "pose_label": gen_img.pose_label,
                    "model_id": gen_img.model_id
                })

            batch_data["garment_images"].append(garment_data)

        response.append(batch_data)

    return response


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"detail": "Task deleted successfully"}

@router.get("/my/", response_model=list[TaskResponse])
def get_my_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tasks = db.query(Task)
    result = []
    for task in tasks:
        # Get all image URLs for the model
        model_images = []
        if task.model and hasattr(task.model, "model_images"):
            model_images = [img.url for img in task.model.model_images]
        # Build response dict
        task_dict = TaskResponse.from_orm(task).dict()
        task_dict["model_images"] = model_images
        result.append(task_dict)
    return result