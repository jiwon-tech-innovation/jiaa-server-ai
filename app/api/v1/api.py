from fastapi import APIRouter
from app.api.v1.endpoints import intelligence

api_router = APIRouter()
api_router.include_router(intelligence.router, tags=["intelligence"])
