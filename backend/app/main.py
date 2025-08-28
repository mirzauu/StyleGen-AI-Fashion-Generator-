from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response
from starlette.requests import Request

from app.api import auth, plans, subscriptions, models, tasks, batches
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

class CORSAwareStaticFiles(StaticFiles):
    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        response.headers["Access-Control-Allow-Origin"] = "*"  # allow all
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "*"
        return response

app = FastAPI()

import logging
from fastapi import FastAPI

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # INFO, DEBUG, ERROR, etc.
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("vestureai")
# Global CORS for API routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files with CORS headers
app.mount("/uploaded_garments", CORSAwareStaticFiles(directory="uploaded_garments"), name="uploaded_garments")
app.mount("/uploaded_images", CORSAwareStaticFiles(directory="uploaded_images"), name="uploaded_images")

# Include API routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(plans.router, prefix="/plans", tags=["plans"])
app.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
app.include_router(models.router, prefix="/models", tags=["models"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(batches.router, prefix="/batches", tags=["batches"])


@app.get("/")
async def root():
    return {"message": "Welcome to VestureAI API"}
