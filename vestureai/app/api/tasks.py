from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models import Task, Batch
from app.schemas import TaskCreate, TaskResponse, BatchCreate
from app.core.config import get_db
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_task = Task(**task.dict(), user_id=current_user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

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
    return batches

@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"detail": "Task deleted successfully"}