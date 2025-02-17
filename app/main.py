from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import get_db, engine
from . import models
from .api import api_router
import uvicorn

app = FastAPI(
    title="PlayStore API",
    description="API for managing PlayStore applications data.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
# Configure CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",  # Streamlit default port
        "http://127.0.0.1:8501",
        "http://0.0.0.0:8501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router with prefix
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Welcome to PlayStore API",
        "docs": "/docs",
        "redoc": "/redoc"
    }

from sqlalchemy import text

# Health check endpoint
@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Try to make a simple query to verify database connection
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": str(e)
        }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
