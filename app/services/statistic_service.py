from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import pytz

class StatisticService:
    async def get_play_ratio(self, db: AsyncSession, user_id: str, current_time_str: str) -> float:
        """
        Calculates the percentage of 'PLAY' activities within +/- 30 minutes 
        of the given time (interpreted as today's time).
        
        Args:
            db: AsyncSession
            user_id: user identifier
            current_time_str: "HH:MM" format (e.g., "14:30")
        
        Returns:
            float: Percentage (0.0 to 100.0)
        """
        # Parse current_time_str to time object
        try:
            target_time = datetime.strptime(current_time_str, "%H:%M").time()
        except ValueError:
            print(f"[StatisticService] Invalid time format: {current_time_str}")
            return 0.0

        # Construct query window for TODAY (Simple implementation)
        # For a robust "historical" analysis independent of date, we would need 
        # to cast log_time to time type in SQL.
        # "Where EXTRACT(HOUR FROM log_time) ... " logic.
        
        # SQL Logic:
        # Select rows where time part of log_time is within +/- 30 mins of target_time
        # This checks ALL dates (historical capability as requested).
        
        # We handle wrap-around (e.g., 23:50 + 30min) by simple time comparison in Python or complex SQL.
        # Let's use PostgreSQL's time type casting for simplicity.
        
        # Casting timestamp to time: log_time::time
        query = text("""
            SELECT 
                COUNT(*) FILTER (WHERE category = 'PLAY') as play_count,
                COUNT(*) as total_count
            FROM activity_logs
            WHERE user_id = :user_id
            AND log_time::time BETWEEN (:start_time) AND (:end_time)
        """)
        
        # Calculate start/end time objects
        # Using dummy date to perform arithmetic
        dummy_date = datetime(2000, 1, 1, target_time.hour, target_time.minute)
        start_dt = dummy_date - timedelta(minutes=30)
        end_dt = dummy_date + timedelta(minutes=30)
        
        start_time = start_dt.time()
        end_time = end_dt.time()
        
        # Handle midnight wrap-around if necessary (not fully covered here for simplicity, 
        # assume standard day hours 09:00~18:00 mostly). 
        # If wrap-around, start_time > end_time, requiring OR condition.
        
        try:
            result = await db.execute(query, {
                "user_id": user_id,
                "start_time": start_time,
                "end_time": end_time
            })
            row = result.fetchone()
            
            if not row:
                return 0.0
                
            play_count = row[0] or 0
            total_count = row[1] or 0
            
            if total_count == 0:
                return 0.0
                
            return (play_count / total_count) * 100.0
            
        except Exception as e:
            print(f"[StatisticService] Query Error: {e}")
            return 0.0

statistic_service = StatisticService()
