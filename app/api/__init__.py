from fastapi import APIRouter
from .categories import router as categories_router
from .developers import router as developers_router
from .apps import router as apps_router

api_router = APIRouter()

api_router.include_router(categories_router)
api_router.include_router(developers_router)
api_router.include_router(apps_router)
