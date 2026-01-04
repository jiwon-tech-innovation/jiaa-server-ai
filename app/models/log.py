from sqlalchemy import Column, String, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.core.database import Base

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, index=True, nullable=False)
    
    # Category: STUDY, PLAY, NEUTRAL, WORK, etc.
    category = Column(String, index=True, nullable=False)
    
    # Detailed action (e.g., "YouTube", "VSCode")
    action_detail = Column(String, nullable=True)
    
    # Time of log
    log_time = Column(DateTime, default=datetime.utcnow, index=True)

    # Index for efficient time-range queries
    __table_args__ = (
        Index('idx_user_time', 'user_id', 'log_time'),
    )
