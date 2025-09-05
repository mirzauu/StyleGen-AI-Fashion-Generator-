from pydantic_settings import BaseSettings
from app.database import SessionLocal

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 300000
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Email configuration
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587
    EMAIL_USERNAME: str
    EMAIL_PASSWORD: str
    EMAIL_FROM: str
    
    STRIPE_API_KEY: str
    MINIO_URL: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    CELERY_BROKER_URL: str
    FAL_KEY: str

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()