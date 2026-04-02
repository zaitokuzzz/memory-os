from fastapi import APIRouter

from app.api.v1.admin import router as admin_router
from app.api.v1.health import router as health_router
from app.api.v1.memory_feedback import router as memory_feedback_router
from app.api.v1.memory_query import router as memory_query_router
from app.api.v1.memory_write import router as memory_write_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(memory_write_router, prefix="/memory", tags=["memory-write"])
api_router.include_router(memory_query_router, prefix="/memory", tags=["memory-query"])
api_router.include_router(memory_feedback_router, prefix="/memory", tags=["memory-feedback"])
api_router.include_router(admin_router, tags=["admin"])
