"""
ARA - API v1 Router
"""
from fastapi import APIRouter
from src.api.v1.endpoints import router as endpoints_router

router = APIRouter(prefix="/api/v1")
router.include_router(endpoints_router)
