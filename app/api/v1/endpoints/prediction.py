from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.services.statistic_service import statistic_service
from app.services.predictor import predictor_service

router = APIRouter()

class RiskResponse(BaseModel):
    should_warn: bool
    risk_percentage: float
    message: Optional[str] = None

@router.get("/predict/risk", response_model=RiskResponse)
async def predict_risk(
    user_id: str, 
    current_time: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Predicts if the user is likely to slack off based on historical data.
    Triggered by Dev 4 (Router).
    """
    
    # 1. Get Play Ratio from DB
    play_ratio = await statistic_service.get_play_ratio(db, user_id, current_time)
    
    # 2. Logic: Threshold Check (70%)
    if play_ratio < 70.0:
        return RiskResponse(
            should_warn=False, 
            risk_percentage=play_ratio, 
            message=None
        )
        
    # 3. Generate Warning via LLM
    warning_msg = await predictor_service.generate_prediction_warning(
        current_time=current_time,
        risk_percentage=play_ratio
    )
    
    return RiskResponse(
        should_warn=True, 
        risk_percentage=play_ratio, 
        message=warning_msg
    )
