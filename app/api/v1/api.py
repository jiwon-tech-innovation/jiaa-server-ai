from fastapi import APIRouter
from app.api.v1.endpoints import intelligence, prediction

api_router = APIRouter()
api_router.include_router(intelligence.router, tags=["intelligence"])
api_router.include_router(prediction.router, tags=["prediction"])
