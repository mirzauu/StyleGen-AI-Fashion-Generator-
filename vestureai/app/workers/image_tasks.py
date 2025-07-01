from celery import Celery
from celery.result import AsyncResult
from app.services.image_generation import generate_images
from app.models import Batch, GeneratedImage
from app.database import SessionLocal

celery_app = Celery('image_tasks', broker='redis://localhost:6379/0')

@celery_app.task(bind=True)
def process_image_generation(self, batch_id: int):
    db = SessionLocal()
    try:
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            raise ValueError("Batch not found")

        # Update batch status to processing
        batch.status = 'processing'
        db.commit()

        # Generate images
        output_urls = generate_images(batch.garment_image_url, batch.task.model_id)

        # Save generated images to the database
        for pose_label, output_url in output_urls.items():
            generated_image = GeneratedImage(batch_id=batch.id, output_url=output_url, pose_label=pose_label)
            db.add(generated_image)

        # Update batch status to done
        batch.status = 'done'
        db.commit()

    except Exception as e:
        self.retry(exc=e, countdown=60)  # Retry on failure
        batch.status = 'failed'
        db.commit()
    finally:
        db.close()

def generate_images_task(batch_id: int, poses: list):
    """
    Triggers the Celery image generation task asynchronously.
    """
    return process_image_generation.delay(batch_id)