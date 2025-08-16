from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, plans, subscriptions, models, tasks, batches
from fastapi.staticfiles import StaticFiles
app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Mount both folders
app.mount("/uploaded_garments", StaticFiles(directory="uploaded_garments"), name="uploaded_garments")
app.mount("/uploaded_images", StaticFiles(directory="uploaded_images"), name="uploaded_images")
# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(plans.router, prefix="/plans", tags=["plans"])
app.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
app.include_router(models.router, prefix="/models", tags=["models"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(batches.router, prefix="/batches", tags=["batches"])

@app.get("/")
async def root():
    return {"message": "Welcome to VestureAI API"}