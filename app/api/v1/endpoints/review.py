from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from app.services.review_service import review_service

router = APIRouter()

class BlogRequest(BaseModel):
    error_log: Optional[str] = None
    solution_code: Optional[str] = None
    user_id: Optional[str] = "dev1"

class BlogResponse(BaseModel):
    status: str
    message: Optional[str] = None
    filename: Optional[str] = None
    content: Optional[str] = None # Markdown Content

@router.post("/review/blog", response_model=BlogResponse)
async def create_auto_blog(request: BlogRequest):
    """
    Triggers 'Auto-Blog' generation.
    Generates a full technical blog post based on daily activity and optional error logs.
    """
    result = await review_service.generate_blog_post(
        error_log=request.error_log,
        solution_code=request.solution_code,
        user_id=request.user_id
    )
    
    if result.get("status") == "GENERATED":
        return BlogResponse(
            status="GENERATED",
            filename=result.get("filename"),
            content=result.get("content"),
            message="Auto-Blog generated successfully. Please save it locally."
        )
    else:
        return BlogResponse(status="ERROR", message=result.get("message"))

from fastapi import BackgroundTasks

@router.post("/daily-wrapped")
async def create_daily_wrapped(background_tasks: BackgroundTasks):
    """
    Generates a "Daily Wrapped" report (Plan vs Actual vs Said).
    Returns the Generated Markdown immediately.
    """
    from app.services.report_service import report_service
    
    report_md = await report_service.generate_daily_wrapped(user_id="dev1")
    return {"status": "GENERATED", "content": report_md}
