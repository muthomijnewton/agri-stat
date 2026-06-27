from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import ALLOWED_ORIGINS, API_TITLE, API_VERSION, API_DESCRIPTION
from app.api.routes import api_router
from app.db.database import engine, Base
import app.models.models  # noqa: F401

from init_db import add_default_user, add_sample_data

# Initialize FastAPI app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
)

@app.on_event("startup")
def startup_event():
    """
    Seed default/demo data.

    Database schema is managed exclusively by Alembic migrations.
    """
    add_default_user()
    add_sample_data()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Include routers
app.include_router(api_router)
