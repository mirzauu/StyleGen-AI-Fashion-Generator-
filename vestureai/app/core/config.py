from pydantic_settings import BaseSettings
from app.database import SessionLocal

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    STRIPE_API_KEY: str
    MINIO_URL: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    CELERY_BROKER_URL: str

    class Config:
        env_file = ".env"

settings = Settings()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()